"""
.info / .whois — ultra full Telegram user report (premium)
  .info
  .info @user | id
  reply + .info

Every field Telegram API allows — multi-message if long.
"""
import html
from datetime import datetime, timezone

from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus, UserStatus

from core.clients import app
from config import OWNER_ID
from database.mongo import get_warns
from modules.owner.sudoers import ub_cmd, sudo_only

# Telegram DC map
DC_MAP = {
    1: "Miami, FL, USA",
    2: "Amsterdam, NL",
    3: "Miami, FL, USA",
    4: "Amsterdam, NL",
    5: "Singapore",
}


def _yn(v) -> str:
    return "✅ Yes" if v else "❌ No"


def _esc(s) -> str:
    return html.escape(str(s)) if s is not None else "—"


def _status_line(status) -> str:
    if status is None:
        return "Hidden / Unknown"
    if status == UserStatus.ONLINE:
        return "🟢 Online"
    if status == UserStatus.OFFLINE:
        was = getattr(status, "was_online", None)
        if was:
            try:
                return f"⚫ Offline · last seen {was}"
            except Exception:
                return f"⚫ Offline · last={was}"
        return "⚫ Offline"
    if status == UserStatus.RECENTLY:
        return "🟡 Recently"
    if status == UserStatus.LAST_WEEK:
        return "🟠 Last week"
    if status == UserStatus.LAST_MONTH:
        return "🔴 Last month"
    return str(status)


def _member_status(st) -> str:
    try:
        if st == ChatMemberStatus.OWNER:
            return "👑 Owner"
        if st == ChatMemberStatus.ADMINISTRATOR:
            return "🛡 Admin"
        if st == ChatMemberStatus.MEMBER:
            return "👤 Member"
        if st == ChatMemberStatus.RESTRICTED:
            return "🚫 Restricted"
        if st == ChatMemberStatus.LEFT:
            return "🚪 Left"
        if st == ChatMemberStatus.BANNED:
            return "⛔ Banned"
        return str(getattr(st, "value", st))
    except Exception:
        return str(st)


def _approx_reg(uid: int) -> str:
    """Rough registration era from user id ranges (approximate)."""
    try:
        uid = int(uid)
    except Exception:
        return "—"
    ranges = [
        (1_000_000_000, "2020+ (newer)"),
        (500_000_000, "2018–2020"),
        (200_000_000, "2016–2018"),
        (100_000_000, "2015–2016"),
        (50_000_000, "2014–2015"),
        (10_000_000, "2013–2014"),
        (1_000_000, "2013 early"),
        (0, "Very early / special"),
    ]
    for threshold, label in ranges:
        if uid >= threshold:
            return label
    return "—"


def _chat_link(chat) -> str:
    uname = getattr(chat, "username", None)
    if uname:
        return f"https://t.me/{uname}"
    cid = getattr(chat, "id", 0) or 0
    s = str(cid)
    if s.startswith("-100"):
        return f"https://t.me/c/{s[4:]}/1"
    return f"tg://openmessage?chat_id={cid}"


async def _send_chunks(client, chat_id: int, text: str, reply_to=None):
    chunk = 3900
    first = True
    for i in range(0, len(text), chunk):
        part = text[i : i + chunk]
        if first and reply_to:
            await client.send_message(chat_id, part, reply_to_message_id=reply_to)
            first = False
        else:
            await client.send_message(chat_id, part)


@app.on_message(ub_cmd("info", "whois"))
@sudo_only
async def info_cmd(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
    else:
        parts = (message.text or "").split()
        target = parts[1].lstrip("@") if len(parts) > 1 else "me"

    status_msg = await message.reply_text("⏳ <b>Premium scan…</b> full details")
    try:
        user = await client.get_users(target)
        try:
            chat = await client.get_chat(user.id)
        except Exception:
            chat = None

        common_list = []
        try:
            common_list = await client.get_common_chats(user.id)
        except Exception:
            common_list = []
        common_n = len(common_list)

        full = (user.first_name or "") + (f" {user.last_name}" if user.last_name else "")
        bio = getattr(chat, "bio", None) or "—"
        status = _status_line(getattr(user, "status", None))
        is_owner = bool(OWNER_ID and user.id == OWNER_ID)
        link = (
            f"<a href='tg://user?id={user.id}'>"
            f"{'👑 OWNER' if is_owner else _esc(user.first_name or user.id)}"</a>"
        )

        photo_n = 0
        first_photo = None
        try:
            async for p in client.get_chat_photos(user.id, limit=100):
                photo_n += 1
                if first_photo is None:
                    first_photo = p.file_id
        except Exception:
            pass

        dc = getattr(user, "dc_id", None)
        dc_loc = DC_MAP.get(dc, "Unknown") if dc else "—"

        # emoji status / premium extras
        emoji_status = getattr(user, "emoji_status", None)
        emoji_line = "—"
        if emoji_status is not None:
            custom_id = getattr(emoji_status, "custom_emoji_id", None)
            emoji_line = f"custom_id=<code>{custom_id}</code>" if custom_id else str(emoji_status)

        phone = getattr(user, "phone_number", None) or "— (privacy)"

        lines = [
            "╔════════════════════════════════╗",
            "║  💎 <b>YASHIKA FULL USER INFO</b>  ║",
            "╚════════════════════════════════╝",
            "",
            "<b>─── Identity ───</b>",
            f"👤 Name: <b>{_esc(full) or '—'}</b>",
            f"🔖 Username: @{_esc(user.username) if user.username else '—'}",
            f"🆔 User ID: <code>{user.id}</code>",
            f"📱 Phone: <code>{_esc(phone)}</code>",
            f"🔗 Profile: {link}",
            f"🔗 tg://user?id=<code>{user.id}</code>",
            f"🌐 t.me link: "
            + (f"https://t.me/{user.username}" if user.username else "—"),
            "",
            "<b>─── Presence ───</b>",
            f"📡 Status: {status}",
            f"🗣 Language: <code>{getattr(user, 'language_code', None) or '—'}</code>",
            f"🏛 DC ID: <code>{dc or '—'}</code> ({dc_loc})",
            f"📅 Approx. era: <code>{_approx_reg(user.id)}</code>",
            f"📝 Bio: {_esc(str(bio)[:300])}",
            f"🎭 Emoji status: {emoji_line}",
            "",
            "<b>─── Flags (Telegram) ───</b>",
            f"⭐ Premium: {_yn(getattr(user, 'is_premium', False))}",
            f"✅ Verified: {_yn(getattr(user, 'is_verified', False))}",
            f"🤖 Bot: {_yn(user.is_bot)}",
            f"🗑 Deleted account: {_yn(getattr(user, 'is_deleted', False))}",
            f"🎭 Fake: {_yn(getattr(user, 'is_fake', False))}",
            f"⚠️ Scam: {_yn(getattr(user, 'is_scam', False))}",
            f"🛟 Support: {_yn(getattr(user, 'is_support', False))}",
            f"📇 In contacts: {_yn(getattr(user, 'is_contact', False))}",
            f"🤝 Mutual contact: {_yn(getattr(user, 'is_mutual_contact', False))}",
            f"💜 Close friend: {_yn(getattr(user, 'is_close_friend', False))}",
            f"🔒 Restricted: {_yn(getattr(user, 'is_restricted', False))}",
            f"👑 Is OWNER (bot): {_yn(is_owner)}",
            "",
            "<b>─── Media ───</b>",
            f"🖼 Profile photos: <code>{photo_n}</code>",
            f"👀 Common chats with you: <code>{common_n}</code>",
        ]

        # Restrictions detail
        restrictions = getattr(user, "restrictions", None) or getattr(user, "restriction_reason", None)
        if restrictions:
            lines.append("")
            lines.append("<b>─── Restrictions ───</b>")
            if isinstance(restrictions, (list, tuple)):
                for r in restrictions[:10]:
                    lines.append(f"• {_esc(r)}")
            else:
                lines.append(f"• {_esc(restrictions)}")

        # This chat membership
        if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            lines.append("")
            lines.append("<b>─── This chat ───</b>")
            lines.append(f"Chat: {_esc(message.chat.title or message.chat.id)}")
            lines.append(f"Chat ID: <code>{message.chat.id}</code>")
            try:
                member = await client.get_chat_member(message.chat.id, user.id)
                lines.append(f"Status: {_member_status(member.status)}")
                title = getattr(member, "title", None)
                if title:
                    lines.append(f"Custom title: <code>{_esc(title)}</code>")
                joined = getattr(member, "joined_date", None)
                if joined:
                    lines.append(f"Joined: <code>{joined}</code>")
                perms = getattr(member, "privileges", None)
                if perms:
                    lines.append("<b>Admin rights:</b>")
                    for attr, label in [
                        ("can_manage_chat", "manage chat"),
                        ("can_delete_messages", "delete messages"),
                        ("can_manage_video_chats", "manage VC"),
                        ("can_restrict_members", "ban/restrict"),
                        ("can_promote_members", "promote"),
                        ("can_change_info", "change info"),
                        ("can_invite_users", "invite users"),
                        ("can_pin_messages", "pin messages"),
                        ("can_post_messages", "post (channel)"),
                        ("can_edit_messages", "edit (channel)"),
                        ("is_anonymous", "anonymous"),
                    ]:
                        val = getattr(perms, attr, None)
                        if val is not None:
                            lines.append(f"  · {label}: {_yn(val)}")
                # restrictions on member
                perms_r = getattr(member, "permissions", None)
                if perms_r and member.status == ChatMemberStatus.RESTRICTED:
                    lines.append("<b>Member permissions:</b>")
                    for attr in [
                        "can_send_messages",
                        "can_send_media_messages",
                        "can_send_other_messages",
                        "can_add_web_page_previews",
                        "can_send_polls",
                        "can_invite_users",
                        "can_pin_messages",
                        "can_change_info",
                    ]:
                        if hasattr(perms_r, attr):
                            lines.append(f"  · {attr}: {_yn(getattr(perms_r, attr))}")
            except Exception as e:
                lines.append(f"Status: <i>not in chat / hidden ({type(e).__name__})</i>")
            try:
                warns = await get_warns(message.chat.id, user.id)
                lines.append(f"Warns here: <code>{len(warns)}</code>")
            except Exception:
                pass

        # Common chats list (detailed)
        if common_list:
            lines.append("")
            lines.append("<b>─── Common chats (sample) ───</b>")
            g = c = 0
            for ch in common_list[:40]:
                title = _esc(ch.title or ch.first_name or ch.id)
                tname = getattr(ch.type, "name", str(ch.type))
                if "CHANNEL" in tname:
                    c += 1
                    tag = "📢"
                else:
                    g += 1
                    tag = "👥"
                lines.append(
                    f"{tag} <b>{title}</b>\n"
                    f"   id=<code>{ch.id}</code> · {_chat_link(ch)}"
                )
            lines.append(f"Shown groups≈{g} channels≈{c} (of {common_n})")

        lines.append("")
        lines.append(f"⏱ Generated: <code>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</code>")
        lines.append("💎 <b>Yashika Premium</b> · Telegram-visible data only")
        lines.append("╚════════════════════════════════╝")

        text = "\n".join(lines)

        try:
            await status_msg.delete()
        except Exception:
            pass

        if first_photo:
            # caption limit ~1024 — send photo + full text separately
            cap = (
                f"💎 <b>{_esc(full) or user.id}</b>\n"
                f"ID: <code>{user.id}</code> · @{user.username or '—'}\n"
                f"Premium: {_yn(getattr(user, 'is_premium', False))}"
            )
            try:
                await client.send_photo(message.chat.id, first_photo, caption=cap)
            except Exception:
                pass
            await _send_chunks(client, message.chat.id, text, reply_to=message.id)
        else:
            await _send_chunks(client, message.chat.id, text, reply_to=message.id)

    except Exception as e:
        try:
            await status_msg.edit_text(f"❌ <code>{type(e).__name__}: {e}</code>")
        except Exception:
            await message.reply_text(f"❌ <code>{e}</code>")
