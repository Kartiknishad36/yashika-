"""
Deep user scan (sudo/owner)

  .uinfo / .scan / .fullinfo   reply | @user | id

Telegram API se REAL data:
  • Profile (name, username, bio, premium…)
  • Common groups/channels with YOUR account
  • Admin status in those common chats
  • Profile photo count (DP history count)

Local tracking (jab userbot unke messages dekhe):
  • Messages / voice / stickers counts
  • Name / username / bio change counts (profile track)

NOTE: Telegram kisi random user ke SAARI groups / SAARI DMs / global
message history nahi deta — sirf common chats + jo tumhare account
ne dekha hai.
"""
import asyncio
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus, ParseMode

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import (
    _read,
    _write,
    _lock,
    get_feature,
    set_feature,
)

PREFIXES = [".", "!"]


# ===================== Local activity store =====================
async def _bump_stat(user_id: int, field: str, amount: int = 1):
    async with _lock:
        data = _read()
        data.setdefault("user_stats", {})
        key = str(user_id)
        st = data["user_stats"].setdefault(
            key,
            {
                "messages": 0,
                "voice": 0,
                "stickers": 0,
                "photos": 0,
                "videos": 0,
                "name_changes": 0,
                "username_changes": 0,
                "bio_changes": 0,
                "dp_changes": 0,
                "last_name": "",
                "last_username": "",
                "last_bio": "",
                "names_history": [],
                "usernames_history": [],
            },
        )
        st[field] = int(st.get(field, 0)) + amount
        _write(data)


async def _get_stats(user_id: int) -> dict:
    async with _lock:
        return dict(_read().get("user_stats", {}).get(str(user_id), {}))


async def _record_profile_snapshot(user_id: int, name: str, username: str, bio: str):
    async with _lock:
        data = _read()
        data.setdefault("user_stats", {})
        key = str(user_id)
        st = data["user_stats"].setdefault(
            key,
            {
                "messages": 0,
                "voice": 0,
                "stickers": 0,
                "photos": 0,
                "videos": 0,
                "name_changes": 0,
                "username_changes": 0,
                "bio_changes": 0,
                "dp_changes": 0,
                "last_name": "",
                "last_username": "",
                "last_bio": "",
                "names_history": [],
                "usernames_history": [],
            },
        )
        changed = False
        if st.get("last_name") and st["last_name"] != name and name:
            st["name_changes"] = int(st.get("name_changes", 0)) + 1
            hist = st.setdefault("names_history", [])
            if name not in hist:
                hist.append(name)
            st["names_history"] = hist[-15:]
            changed = True
        elif not st.get("last_name") and name:
            st["names_history"] = [name]

        if st.get("last_username") and st["last_username"] != (username or "") and username is not None:
            st["username_changes"] = int(st.get("username_changes", 0)) + 1
            hist = st.setdefault("usernames_history", [])
            u = username or "—"
            if u not in hist:
                hist.append(u)
            st["usernames_history"] = hist[-15:]
            changed = True
        elif not st.get("last_username") and username:
            st["usernames_history"] = [username]

        if st.get("last_bio") is not None and st.get("last_bio", "") != (bio or "") and bio is not None:
            if st.get("last_bio", "") != "":
                st["bio_changes"] = int(st.get("bio_changes", 0)) + 1
            changed = True

        st["last_name"] = name or st.get("last_name", "")
        st["last_username"] = username if username is not None else st.get("last_username", "")
        if bio is not None:
            st["last_bio"] = bio
        if changed:
            _write(data)
        else:
            # still save first snapshot
            if not st.get("last_name") and name:
                st["last_name"] = name
                _write(data)


# Passive tracker — counts what THIS userbot sees
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
        if message.voice or message.video_note:
            await _bump_stat(uid, "voice")
        if message.sticker:
            await _bump_stat(uid, "stickers")
        if message.photo:
            await _bump_stat(uid, "photos")
        if message.video:
            await _bump_stat(uid, "videos")

        # light profile snapshot on activity
        u = message.from_user
        name = f"{u.first_name or ''} {u.last_name or ''}".strip()
        await _record_profile_snapshot(uid, name, u.username or "", None)
    except Exception:
        pass


async def _resolve_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        arg = message.command[1].lstrip("@")
        try:
            return await client.get_users(int(arg) if arg.lstrip("-").isdigit() else arg)
        except Exception:
            return None
    return message.from_user


async def _count_photos(client, user_id: int) -> int:
    n = 0
    try:
        async for _ in client.get_chat_photos(user_id, limit=100):
            n += 1
    except Exception:
        pass
    return n


async def _scan_common(client, user_id: int):
    """Returns groups, channels, admin_in list."""
    groups, channels, admin_in = [], [], []
    try:
        async for chat in client.get_common_chats(user_id):
            title = chat.title or chat.first_name or str(chat.id)
            entry = {"id": chat.id, "title": title, "username": getattr(chat, "username", None)}
            t = chat.type
            if t == ChatType.CHANNEL:
                channels.append(entry)
            else:
                groups.append(entry)
            # admin check
            try:
                member = await client.get_chat_member(chat.id, user_id)
                if member.status in (
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                ):
                    role = "Owner" if member.status == ChatMemberStatus.OWNER else "Admin"
                    admin_in.append({"title": title, "id": chat.id, "role": role})
            except Exception:
                pass
            await asyncio.sleep(0.05)
    except Exception:
        pass
    return groups, channels, admin_in


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
            "Usage: reply / <code>.uinfo @user</code> / <code>.uinfo id</code>"
        )
        return

    status = await message.reply_text("🔍 Scanning user…")

    # Profile
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "—"
    username = f"@{user.username}" if user.username else "—"
    bio = "—"
    try:
        chat = await client.get_chat(user.id)
        bio = getattr(chat, "bio", None) or "—"
    except Exception:
        chat = None

    await _record_profile_snapshot(
        user.id, full_name, user.username or "", bio if bio != "—" else ""
    )

    # DP count
    await status.edit_text("🖼️ Counting profile photos…")
    dp_count = await _count_photos(client, user.id)

    # Common chats + admin
    await status.edit_text("📡 Fetching common groups/channels…")
    groups, channels, admin_in = await _scan_common(client, user.id)

    # Local stats
    st = await _get_stats(user.id)

    # Build report
    lines = [
        f"👤 <b>USER SCAN</b>",
        f"{'─' * 22}",
        f"<b>Name:</b> {full_name}",
        f"<b>Username:</b> {username}",
        f"<b>ID:</b> <code>{user.id}</code>",
        f"<b>DC:</b> {getattr(user, 'dc_id', '—')}",
        f"<b>Premium:</b> {'Yes' if getattr(user, 'is_premium', False) else 'No'}",
        f"<b>Bot:</b> {'Yes' if user.is_bot else 'No'}",
        f"<b>Scam/Fake:</b> {getattr(user, 'is_scam', False)}/{getattr(user, 'is_fake', False)}",
        f"<b>Bio:</b> {str(bio)[:120]}",
        f"<b>DP photos:</b> <code>{dp_count}</code>",
        "",
        f"📊 <b>COMMON WITH YOU</b>",
        f"├ Groups: <code>{len(groups)}</code>",
        f"├ Channels: <code>{len(channels)}</code>",
        f"└ Admin in: <code>{len(admin_in)}</code>",
    ]

    if groups:
        lines.append("")
        lines.append("👥 <b>Common groups</b> (max 15)")
        for g in groups[:15]:
            un = f" @{g['username']}" if g.get("username") else ""
            lines.append(f"• {g['title']}{un} <code>{g['id']}</code>")
        if len(groups) > 15:
            lines.append(f"… +{len(groups) - 15} more")

    if channels:
        lines.append("")
        lines.append("📢 <b>Common channels</b> (max 10)")
        for c in channels[:10]:
            un = f" @{c['username']}" if c.get("username") else ""
            lines.append(f"• {c['title']}{un} <code>{c['id']}</code>")

    if admin_in:
        lines.append("")
        lines.append("🛡 <b>Admin / Owner (common)</b>")
        for a in admin_in[:15]:
            lines.append(f"• [{a['role']}] {a['title']} <code>{a['id']}</code>")

    lines.extend(
        [
            "",
            f"📈 <b>ACTIVITY (seen by this userbot)</b>",
            f"├ Messages: <code>{st.get('messages', 0)}</code>",
            f"├ Voice / video notes: <code>{st.get('voice', 0)}</code>",
            f"├ Stickers: <code>{st.get('stickers', 0)}</code>",
            f"├ Photos: <code>{st.get('photos', 0)}</code>",
            f"└ Videos: <code>{st.get('videos', 0)}</code>",
            "",
            f"📝 <b>PROFILE CHANGES (tracked)</b>",
            f"├ Name changes: <code>{st.get('name_changes', 0)}</code>",
            f"├ Username changes: <code>{st.get('username_changes', 0)}</code>",
            f"└ Bio changes: <code>{st.get('bio_changes', 0)}</code>",
        ]
    )

    names_h = st.get("names_history") or []
    users_h = st.get("usernames_history") or []
    if names_h:
        lines.append("")
        lines.append("<b>Names seen:</b> " + ", ".join(f"<code>{n}</code>" for n in names_h[-8:]))
    if users_h:
        lines.append(
            "<b>Usernames seen:</b> "
            + ", ".join(f"@{u}" if u != "—" else "—" for u in users_h[-8:])
        )

    lines.append("")
    lines.append(
        "<i>⚠️ Global group/DM counts Telegram API nahi deta — "
        "sirf common chats + is account ne jo activity dekhi.</i>"
    )

    text = "\n".join(lines)
    # Telegram caption limit ~4096
    if len(text) > 4000:
        text = text[:3990] + "\n…"

    try:
        await status.edit_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception:
        await message.reply_text(text, parse_mode=ParseMode.HTML)
