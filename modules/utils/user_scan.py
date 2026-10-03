"""
FULL USER INTEL — sirf Telegram API + local track (sach)

Commands (sudo):
  .uinfo / .scan / .fullinfo     deep profile + common + activity
  .dphist                        last profile photos bhejo
  .member                        is group me status + rights
  .fwdinfo                       reply msg pe — forward origin
  .commonlist                    saari common groups/channels list

Jo API nahi deta (IP, saari DMs, global groups) — nahi dikhate.
"""
import asyncio
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus, ParseMode, MessageMediaType

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import (
    _read,
    _write,
    _lock,
    is_gbanned,
    get_gban_list,
    get_warns,
    get_approved_pm,
)

PREFIXES = [".", "!"]

_STAT_DEFAULT = {
    "messages": 0,
    "voice": 0,
    "stickers": 0,
    "photos": 0,
    "videos": 0,
    "documents": 0,
    "animations": 0,
    "audio": 0,
    "contacts": 0,
    "locations": 0,
    "polls": 0,
    "replies": 0,
    "forwards": 0,
    "edits": 0,
    "name_changes": 0,
    "username_changes": 0,
    "bio_changes": 0,
    "last_name": "",
    "last_username": "",
    "last_bio": "",
    "names_history": [],
    "usernames_history": [],
    "first_seen": 0,
    "last_seen_msg": 0,
    "chats_seen": [],
}


# ===================== storage helpers =====================
async def _bump_stat(user_id: int, field: str, amount: int = 1):
    async with _lock:
        data = _read()
        data.setdefault("user_stats", {})
        st = data["user_stats"].setdefault(str(user_id), dict(_STAT_DEFAULT))
        for k, v in _STAT_DEFAULT.items():
            if k not in st:
                st[k] = type(v)() if isinstance(v, (dict, list)) else v
        st[field] = int(st.get(field, 0)) + amount
        now = int(datetime.now(timezone.utc).timestamp())
        if not st.get("first_seen"):
            st["first_seen"] = now
        st["last_seen_msg"] = now
        _write(data)


async def _mark_chat_seen(user_id: int, chat_id: int):
    async with _lock:
        data = _read()
        data.setdefault("user_stats", {})
        st = data["user_stats"].setdefault(str(user_id), dict(_STAT_DEFAULT))
        seen = st.setdefault("chats_seen", [])
        if chat_id not in seen:
            seen.append(chat_id)
            st["chats_seen"] = seen[-200:]
            _write(data)


async def _get_stats(user_id: int) -> dict:
    async with _lock:
        st = dict(_read().get("user_stats", {}).get(str(user_id), {}))
        for k, v in _STAT_DEFAULT.items():
            if k not in st:
                st[k] = type(v)() if isinstance(v, (dict, list)) else v
        return st


async def _record_profile_snapshot(user_id: int, name: str, username: str, bio):
    async with _lock:
        data = _read()
        data.setdefault("user_stats", {})
        st = data["user_stats"].setdefault(str(user_id), dict(_STAT_DEFAULT))
        for k, v in _STAT_DEFAULT.items():
            if k not in st:
                st[k] = type(v)() if isinstance(v, (dict, list)) else v

        if st.get("last_name") and name and st["last_name"] != name:
            st["name_changes"] = int(st.get("name_changes", 0)) + 1
            hist = st.setdefault("names_history", [])
            if name not in hist:
                hist.append(name)
            st["names_history"] = hist[-20:]
        elif name and not st.get("names_history"):
            st["names_history"] = [name]

        uname = username or ""
        if st.get("last_username") is not None and st.get("last_username", "") != uname:
            if st.get("last_username", "") != "" or uname:
                st["username_changes"] = int(st.get("username_changes", 0)) + 1
            hist = st.setdefault("usernames_history", [])
            tag = uname or "—"
            if tag not in hist:
                hist.append(tag)
            st["usernames_history"] = hist[-20:]
        elif uname and not st.get("usernames_history"):
            st["usernames_history"] = [uname]

        if bio is not None:
            old_bio = st.get("last_bio", "")
            if old_bio != "" and old_bio != (bio or ""):
                st["bio_changes"] = int(st.get("bio_changes", 0)) + 1
            st["last_bio"] = bio or ""

        if name:
            st["last_name"] = name
        st["last_username"] = uname
        _write(data)


# ===================== passive activity tracker =====================
@app.on_message(
    filters.incoming & ~filters.me & ~filters.bot & ~filters.service,
    group=12,
)
async def _activity_tracker(client, message: Message):
    if not message.from_user:
        return
    uid = message.from_user.id
    try:
        await _bump_stat(uid, "messages")
        if message.chat:
            await _mark_chat_seen(uid, message.chat.id)

        if message.voice or message.video_note:
            await _bump_stat(uid, "voice")
        if message.sticker:
            await _bump_stat(uid, "stickers")
        if message.photo:
            await _bump_stat(uid, "photos")
        if message.video:
            await _bump_stat(uid, "videos")
        if message.document and not message.animation:
            await _bump_stat(uid, "documents")
        if message.animation:
            await _bump_stat(uid, "animations")
        if message.audio:
            await _bump_stat(uid, "audio")
        if message.contact:
            await _bump_stat(uid, "contacts")
        if message.location or message.venue:
            await _bump_stat(uid, "locations")
        if message.poll:
            await _bump_stat(uid, "polls")
        if message.reply_to_message_id:
            await _bump_stat(uid, "replies")
        if message.forward_date or message.forward_from or message.forward_from_chat:
            await _bump_stat(uid, "forwards")
        if message.edit_date:
            await _bump_stat(uid, "edits")

        u = message.from_user
        name = f"{u.first_name or ''} {u.last_name or ''}".strip()
        await _record_profile_snapshot(uid, name, u.username or "", None)
    except Exception:
        pass


# ===================== resolve =====================
async def _resolve_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        arg = message.command[1].lstrip("@")
        try:
            return await client.get_users(
                int(arg) if arg.lstrip("-").isdigit() else arg
            )
        except Exception:
            return None
    return message.from_user


def _ts(ts) -> str:
    if not ts:
        return "—"
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(ts)


def _yn(v) -> str:
    return "Yes" if v else "No"


async def _count_photos(client, user_id: int) -> int:
    n = 0
    try:
        async for _ in client.get_chat_photos(user_id, limit=100):
            n += 1
    except Exception:
        pass
    return n


async def _scan_common(client, user_id: int):
    groups, channels, admin_in = [], [], []
    try:
        async for chat in client.get_common_chats(user_id):
            title = chat.title or getattr(chat, "first_name", None) or str(chat.id)
            entry = {
                "id": chat.id,
                "title": title,
                "username": getattr(chat, "username", None),
                "members": getattr(chat, "members_count", None),
            }
            if chat.type == ChatType.CHANNEL:
                channels.append(entry)
            else:
                groups.append(entry)
            try:
                member = await client.get_chat_member(chat.id, user_id)
                if member.status in (
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                ):
                    role = (
                        "Owner"
                        if member.status == ChatMemberStatus.OWNER
                        else "Admin"
                    )
                    title_admin = getattr(member, "title", None) or ""
                    admin_in.append(
                        {
                            "title": title,
                            "id": chat.id,
                            "role": role,
                            "custom": title_admin,
                        }
                    )
            except Exception:
                pass
            await asyncio.sleep(0.04)
    except Exception:
        pass
    return groups, channels, admin_in


# ===================== .uinfo =====================
@app.on_message(
    filters.command(
        ["uinfo", "scan", "fullinfo", "userinfo", "whoisfull"],
        prefixes=PREFIXES,
    )
)
@sudo_only
async def user_scan_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text(
            "Usage: <b>reply</b> / <code>.uinfo @user</code> / <code>.uinfo id</code>"
        )
        return

    status = await message.reply_text("🔍 Full scan…")

    # ---- basic ----
    first = user.first_name or ""
    last = user.last_name or ""
    full_name = f"{first} {last}".strip() or "—"
    username = f"@{user.username}" if user.username else "—"

    bio = "—"
    chat_obj = None
    try:
        chat_obj = await client.get_chat(user.id)
        bio = getattr(chat_obj, "bio", None) or "—"
    except Exception:
        pass

    await _record_profile_snapshot(
        user.id, full_name, user.username or "", bio if bio != "—" else ""
    )

    # ---- flags (every real field) ----
    dc = getattr(user, "dc_id", None)
    lang = getattr(user, "language_code", None) or "—"
    is_bot = bool(user.is_bot)
    is_premium = bool(getattr(user, "is_premium", False))
    is_verified = bool(getattr(user, "is_verified", False))
    is_scam = bool(getattr(user, "is_scam", False))
    is_fake = bool(getattr(user, "is_fake", False))
    is_deleted = bool(getattr(user, "is_deleted", False))
    is_support = bool(getattr(user, "is_support", False))
    is_self = bool(getattr(user, "is_self", False))
    is_contact = bool(getattr(user, "is_contact", False))
    is_mutual = bool(getattr(user, "is_mutual_contact", False))
    is_restricted = bool(getattr(user, "is_restricted", False))
    phone = getattr(user, "phone_number", None)  # only if contact

    emoji_status = None
    try:
        es = getattr(user, "emoji_status", None)
        if es is not None:
            emoji_status = getattr(es, "custom_emoji_id", None) or str(es)
    except Exception:
        pass

    # ---- DP ----
    await status.edit_text("🖼️ DP count…")
    dp_count = await _count_photos(client, user.id)

    # ---- common ----
    await status.edit_text("📡 Common chats…")
    groups, channels, admin_in = await _scan_common(client, user.id)

    # ---- this chat member ----
    this_status = "—"
    this_joined = "—"
    this_title = "—"
    this_perms = ""
    if message.chat and message.chat.type in (
        ChatType.GROUP,
        ChatType.SUPERGROUP,
        ChatType.CHANNEL,
    ):
        try:
            mem = await client.get_chat_member(message.chat.id, user.id)
            this_status = mem.status.value if hasattr(mem.status, "value") else str(mem.status)
            this_title = getattr(mem, "title", None) or "—"
            jd = getattr(mem, "joined_date", None)
            if jd:
                this_joined = jd.strftime("%Y-%m-%d %H:%M") if hasattr(jd, "strftime") else str(jd)
            pr = getattr(mem, "privileges", None)
            if pr:
                bits = []
                for attr in (
                    "can_manage_chat",
                    "can_delete_messages",
                    "can_manage_video_chats",
                    "can_restrict_members",
                    "can_promote_members",
                    "can_change_info",
                    "can_invite_users",
                    "can_pin_messages",
                    "can_post_messages",
                    "can_edit_messages",
                ):
                    if getattr(pr, attr, None):
                        bits.append(attr.replace("can_", ""))
                this_perms = ", ".join(bits) if bits else "none"
        except Exception as e:
            this_status = f"n/a ({type(e).__name__})"

    # ---- local DB ----
    st = await _get_stats(user.id)
    gbanned = await is_gbanned(user.id)
    gban_reason = "—"
    if gbanned:
        for g in await get_gban_list():
            if g["user_id"] == user.id:
                gban_reason = g.get("reason") or "—"
                break

    warns_here = []
    if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        try:
            warns_here = await get_warns(message.chat.id, user.id)
        except Exception:
            pass

    approved = user.id in await get_approved_pm()

    # ---- build text ----
    lines = [
        "👤 <b>FULL USER SCAN</b>",
        "═" * 18,
        "",
        "📌 <b>IDENTITY</b>",
        f"├ First name: <code>{first or '—'}</code>",
        f"├ Last name: <code>{last or '—'}</code>",
        f"├ Full name: <b>{full_name}</b>",
        f"├ Username: {username}",
        f"├ User ID: <code>{user.id}</code>",
        f"├ DC ID: <code>{dc if dc is not None else '—'}</code>",
        f"├ Language: <code>{lang}</code>",
        f"├ Phone: <code>{phone or '— (sirf contact pe)'}</code>",
        f"├ Emoji status: <code>{emoji_status or '—'}</code>",
        f"├ Bio: {str(bio)[:180]}",
        f"└ Link: <a href='tg://user?id={user.id}'>tg://user?id={user.id}</a>",
        "",
        "🏷 <b>FLAGS</b>",
        f"├ Bot: {_yn(is_bot)}",
        f"├ Premium: {_yn(is_premium)}",
        f"├ Verified: {_yn(is_verified)}",
        f"├ Support: {_yn(is_support)}",
        f"├ Scam: {_yn(is_scam)}",
        f"├ Fake: {_yn(is_fake)}",
        f"├ Deleted: {_yn(is_deleted)}",
        f"├ Restricted: {_yn(is_restricted)}",
        f"├ Self (you): {_yn(is_self)}",
        f"├ Your contact: {_yn(is_contact)}",
        f"└ Mutual contact: {_yn(is_mutual)}",
        "",
        f"🖼 <b>PROFILE PHOTOS:</b> <code>{dp_count}</code>",
        "",
        "📊 <b>COMMON WITH YOUR ACCOUNT</b>",
        f"├ Groups: <code>{len(groups)}</code>",
        f"├ Channels: <code>{len(channels)}</code>",
        f"└ Admin/Owner in: <code>{len(admin_in)}</code>",
    ]

    if groups:
        lines.append("")
        lines.append("👥 <b>Common groups</b> (max 20)")
        for g in groups[:20]:
            un = f" @{g['username']}" if g.get("username") else ""
            mc = f" · {g['members']}" if g.get("members") else ""
            lines.append(f"• {g['title']}{un}{mc} <code>{g['id']}</code>")
        if len(groups) > 20:
            lines.append(f"… +{len(groups) - 20} more · <code>.commonlist</code>")

    if channels:
        lines.append("")
        lines.append("📢 <b>Common channels</b> (max 15)")
        for c in channels[:15]:
            un = f" @{c['username']}" if c.get("username") else ""
            lines.append(f"• {c['title']}{un} <code>{c['id']}</code>")

    if admin_in:
        lines.append("")
        lines.append("🛡 <b>Admin / Owner (common chats)</b>")
        for a in admin_in[:20]:
            cust = f" «{a['custom']}»" if a.get("custom") else ""
            lines.append(f"• [{a['role']}]{cust} {a['title']} <code>{a['id']}</code>")

    lines.extend(
        [
            "",
            "📍 <b>THIS CHAT</b>",
            f"├ Status: <code>{this_status}</code>",
            f"├ Custom title: <code>{this_title}</code>",
            f"├ Joined: <code>{this_joined}</code>",
            f"├ Warns here: <code>{len(warns_here)}</code>",
            f"└ Admin rights: <code>{this_perms or '—'}</code>",
            "",
            "🔐 <b>LOCAL DB</b>",
            f"├ GBanned: {_yn(gbanned)} ({gban_reason})",
            f"└ PM approved: {_yn(approved)}",
            "",
            "📈 <b>ACTIVITY (is userbot ne jo dekha)</b>",
            f"├ Messages: <code>{st.get('messages', 0)}</code>",
            f"├ Voice / video-note: <code>{st.get('voice', 0)}</code>",
            f"├ Stickers: <code>{st.get('stickers', 0)}</code>",
            f"├ Photos: <code>{st.get('photos', 0)}</code>",
            f"├ Videos: <code>{st.get('videos', 0)}</code>",
            f"├ Documents: <code>{st.get('documents', 0)}</code>",
            f"├ GIFs/animations: <code>{st.get('animations', 0)}</code>",
            f"├ Audio: <code>{st.get('audio', 0)}</code>",
            f"├ Contacts shared: <code>{st.get('contacts', 0)}</code>",
            f"├ Locations: <code>{st.get('locations', 0)}</code>",
            f"├ Polls: <code>{st.get('polls', 0)}</code>",
            f"├ Replies: <code>{st.get('replies', 0)}</code>",
            f"├ Forwards: <code>{st.get('forwards', 0)}</code>",
            f"├ Edits seen: <code>{st.get('edits', 0)}</code>",
            f"├ Chats seen in: <code>{len(st.get('chats_seen') or [])}</code>",
            f"├ First seen: <code>{_ts(st.get('first_seen'))}</code>",
            f"└ Last msg seen: <code>{_ts(st.get('last_seen_msg'))}</code>",
            "",
            "📝 <b>PROFILE CHANGES (tracked)</b>",
            f"├ Name changes: <code>{st.get('name_changes', 0)}</code>",
            f"├ Username changes: <code>{st.get('username_changes', 0)}</code>",
            f"└ Bio changes: <code>{st.get('bio_changes', 0)}</code>",
        ]
    )

    names_h = st.get("names_history") or []
    users_h = st.get("usernames_history") or []
    if names_h:
        lines.append("")
        lines.append(
            "<b>Names history:</b> "
            + ", ".join(f"<code>{n}</code>" for n in names_h[-12:])
        )
    if users_h:
        lines.append(
            "<b>Usernames history:</b> "
            + ", ".join(
                (f"@{u}" if u and u != "—" else "—") for u in users_h[-12:]
            )
        )

    lines.extend(
        [
            "",
            "📎 <b>EXTRA CMDS</b>",
            "<code>.dphist</code> · <code>.member</code> · <code>.fwdinfo</code> · <code>.commonlist</code>",
            "",
            "<i>⚠️ Telegram global groups/DMs/IP/device nahi deta. "
            "Sirf common chats + is account ki observed activity.</i>",
        ]
    )

    # split if too long
    text = "\n".join(lines)
    chunks = []
    while text:
        if len(text) <= 4000:
            chunks.append(text)
            break
        cut = text.rfind("\n", 0, 3900)
        if cut < 500:
            cut = 3900
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")

    try:
        await status.edit_text(
            chunks[0], parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    except Exception:
        await message.reply_text(
            chunks[0], parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    for extra in chunks[1:]:
        await message.reply_text(
            extra, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )


# ===================== .dphist =====================
@app.on_message(filters.command(["dphist", "dpphotos", "pfphist"], prefixes=PREFIXES))
@sudo_only
async def dphist_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Reply / @user / id")
        return
    status = await message.reply_text(f"🖼 Fetching DPs — {user.first_name or user.id}…")
    sent = 0
    try:
        async for photo in client.get_chat_photos(user.id, limit=12):
            cap = f"DP #{sent + 1} — {user.mention}\n<code>{user.id}</code>"
            try:
                await client.send_photo(message.chat.id, photo.file_id, caption=cap)
                sent += 1
            except Exception:
                pass
            await asyncio.sleep(0.3)
    except Exception as e:
        await status.edit_text(f"❌ {type(e).__name__}: {e}")
        return
    try:
        await status.edit_text(f"✅ Sent <b>{sent}</b> profile photo(s)." if sent else "❌ No DP")
    except Exception:
        pass


# ===================== .member =====================
@app.on_message(filters.command(["member", "meminfo", "chatmember"], prefixes=PREFIXES))
@sudo_only
async def member_cmd(client, message: Message):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
        await message.reply_text("Sirf group/channel me use karo.")
        return
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Reply / @user / id")
        return
    try:
        mem = await client.get_chat_member(message.chat.id, user.id)
    except Exception as e:
        await message.reply_text(f"❌ Member nahi mila: <code>{e}</code>")
        return

    status_v = mem.status.value if hasattr(mem.status, "value") else str(mem.status)
    joined = getattr(mem, "joined_date", None)
    joined_s = joined.strftime("%Y-%m-%d %H:%M UTC") if joined and hasattr(joined, "strftime") else str(joined or "—")
    custom = getattr(mem, "title", None) or "—"
    inv = getattr(mem, "invited_by", None)
    inv_s = inv.mention if inv else "—"
    rest = getattr(mem, "restricted_by", None)
    rest_s = rest.mention if rest else "—"
    until = getattr(mem, "until_date", None)
    until_s = until.strftime("%Y-%m-%d %H:%M") if until and hasattr(until, "strftime") else str(until or "—")

    lines = [
        f"👤 <b>MEMBER INFO</b> — {message.chat.title or message.chat.id}",
        f"User: {user.mention} <code>{user.id}</code>",
        f"Status: <code>{status_v}</code>",
        f"Custom title: <code>{custom}</code>",
        f"Joined: <code>{joined_s}</code>",
        f"Invited by: {inv_s}",
        f"Restricted by: {rest_s}",
        f"Until: <code>{until_s}</code>",
    ]
    pr = getattr(mem, "privileges", None)
    if pr:
        lines.append("<b>Privileges:</b>")
        for attr in dir(pr):
            if attr.startswith("can_") and not attr.startswith("can_be"):
                try:
                    val = getattr(pr, attr)
                    if isinstance(val, bool):
                        lines.append(f"  • {attr}: {_yn(val)}")
                except Exception:
                    pass
    warns = await get_warns(message.chat.id, user.id)
    lines.append(f"Warns: <code>{len(warns)}</code>")
    if warns:
        for i, w in enumerate(warns[-5:], 1):
            lines.append(f"  {i}. {w}")

    await message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


# ===================== .fwdinfo =====================
@app.on_message(filters.command(["fwdinfo", "forwardinfo", "fwinfo"], prefixes=PREFIXES))
@sudo_only
async def fwdinfo_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        await message.reply_text("Kisi message pe <b>reply</b> + <code>.fwdinfo</code>")
        return

    lines = [
        "📨 <b>MESSAGE / FORWARD INFO</b>",
        f"Msg ID: <code>{r.id}</code>",
        f"Date: <code>{r.date}</code>",
        f"Edit date: <code>{r.edit_date or '—'}</code>",
        f"Media: <code>{r.media or 'text'}</code>",
        f"From user: {r.from_user.mention if r.from_user else '—'}"
        + (f" <code>{r.from_user.id}</code>" if r.from_user else ""),
        f"Sender chat: <code>{getattr(r.sender_chat, 'title', None) or getattr(r.sender_chat, 'id', '—')}</code>",
        f"Via bot: {r.via_bot.mention if r.via_bot else '—'}",
        f"Reply to msg: <code>{r.reply_to_message_id or '—'}</code>",
    ]

    if r.forward_date or r.forward_from or r.forward_from_chat or r.forward_sender_name:
        lines.append("")
        lines.append("<b>Forward origin</b>")
        lines.append(f"├ Forward date: <code>{r.forward_date or '—'}</code>")
        if r.forward_from:
            lines.append(
                f"├ From user: {r.forward_from.mention} <code>{r.forward_from.id}</code>"
            )
        if r.forward_from_chat:
            fc = r.forward_from_chat
            lines.append(
                f"├ From chat: {fc.title or fc.id} <code>{fc.id}</code>"
            )
            lines.append(f"├ Chat username: @{getattr(fc, 'username', None) or '—'}")
        lines.append(f"├ Sender name (hidden): <code>{r.forward_sender_name or '—'}</code>")
        lines.append(
            f"└ Forward msg id: <code>{getattr(r, 'forward_from_message_id', None) or '—'}</code>"
        )
    else:
        lines.append("")
        lines.append("<i>Ye message forward nahi hai.</i>")

    if r.sticker:
        s = r.sticker
        lines.append("")
        lines.append("<b>Sticker</b>")
        lines.append(f"├ Emoji: {s.emoji or '—'}")
        lines.append(f"├ Set: <code>{s.set_name or '—'}</code>")
        lines.append(f"├ File id: <code>{s.file_id[:40]}…</code>")
        lines.append(f"└ Animated/video: {_yn(s.is_animated)}/{_yn(getattr(s, 'is_video', False))}")

    await message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


# ===================== .commonlist =====================
@app.on_message(
    filters.command(["commonlist", "mutuals", "commongroups"], prefixes=PREFIXES)
)
@sudo_only
async def commonlist_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Reply / @user / id")
        return
    status = await message.reply_text("📡 Loading all common chats…")
    groups, channels, admin_in = await _scan_common(client, user.id)
    admin_ids = {a["id"] for a in admin_in}

    lines = [
        f"📡 <b>COMMON CHATS</b> — {user.mention}",
        f"Groups: <code>{len(groups)}</code> · Channels: <code>{len(channels)}</code>",
        "",
    ]
    for g in groups:
        mark = " 🛡" if g["id"] in admin_ids else ""
        un = f" @{g['username']}" if g.get("username") else ""
        lines.append(f"•{mark} {g['title']}{un} <code>{g['id']}</code>")
    if channels:
        lines.append("")
        lines.append("<b>Channels</b>")
        for c in channels:
            un = f" @{c['username']}" if c.get("username") else ""
            lines.append(f"• {c['title']}{un} <code>{c['id']}</code>")

    text = "\n".join(lines) if len(lines) > 3 else "\n".join(lines) + "\nNo common chats."
    if len(text) > 4000:
        text = text[:3990] + "\n…"
    try:
        await status.edit_text(text, parse_mode=ParseMode.HTML)
    except Exception:
        await message.reply_text(text, parse_mode=ParseMode.HTML)
