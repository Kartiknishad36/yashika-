"""
.user — full user info (Telegram API only, no fake IP/GPS)

Usage:
  .user              → reply pe / self
  .user @username
  .user 123456789
"""
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only


def _status_text(status) -> str:
    if status is None:
        return "hidden / unknown"
    n = type(status).__name__
    if "Online" in n:
        return "online"
    if "Offline" in n:
        was = getattr(status, "was_online", None)
        return f"offline (last_seen={was})" if was else "offline"
    if "Recently" in n:
        return "recently"
    if "LastWeek" in n:
        return "last week"
    if "LastMonth" in n:
        return "last month"
    if "Empty" in n:
        return "long ago / hidden"
    return n


async def _resolve_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    parts = (message.text or "").split()
    if len(parts) > 1:
        arg = parts[1].lstrip("@")
        try:
            if arg.lstrip("-").isdigit():
                return await client.get_users(int(arg))
            return await client.get_users(arg)
        except Exception:
            return None
    return message.from_user


@app.on_message(ub_cmd("user", "userinfo", "uinfo"))
@sudo_only
async def user_full_cmd(client, message: Message):
    u = await _resolve_user(client, message)
    if not u:
        await message.reply_text("Reply / <code>.user @name</code> / <code>.user id</code>")
        return

    status = await message.reply_text("Fetching full info…")

    # refresh full user object
    try:
        u = await client.get_users(u.id)
    except Exception:
        pass

    chat = None
    try:
        chat = await client.get_chat(u.id)
    except Exception:
        pass

    bio = getattr(chat, "bio", None) or getattr(u, "bio", None) or "—"
    status_line = _status_text(getattr(u, "status", None))

    # photos count
    photo_n = 0
    first_photo = None
    try:
        async for p in client.get_chat_photos(u.id, limit=50):
            photo_n += 1
            if first_photo is None:
                first_photo = p.file_id
    except Exception:
        pass

    # common chats
    common_lines = []
    common_n = 0
    try:
        async for c in client.get_common_chats(u.id):
            common_n += 1
            if len(common_lines) < 15:
                title = c.title or c.first_name or str(c.id)
                common_lines.append(f"• {title} <code>{c.id}</code>")
    except Exception:
        pass

    # restriction reason if any
    restriction = getattr(u, "restriction_reason", None) or getattr(u, "restrictions", None) or "—"

    body = (
        f"<b>═══ USER FULL INFO ═══</b>\n\n"
        f"<b>Name:</b> {u.first_name or '—'} {u.last_name or ''}\n"
        f"<b>Username:</b> @{u.username or '—'}\n"
        f"<b>ID:</b> <code>{u.id}</code>\n"
        f"<b>DC:</b> <code>{getattr(u, 'dc_id', '—')}</code>\n"
        f"<b>Status:</b> <code>{status_line}</code>\n"
        f"<b>Bio:</b> {str(bio)[:200]}\n\n"
        f"<b>── Flags ──</b>\n"
        f"Premium: <code>{bool(getattr(u, 'is_premium', False))}</code>\n"
        f"Verified: <code>{bool(getattr(u, 'is_verified', False))}</code>\n"
        f"Bot: <code>{bool(u.is_bot)}</code>\n"
        f"Deleted: <code>{bool(getattr(u, 'is_deleted', False))}</code>\n"
        f"Fake: <code>{bool(getattr(u, 'is_fake', False))}</code>\n"
        f"Scam: <code>{bool(getattr(u, 'is_scam', False))}</code>\n"
        f"Support: <code>{bool(getattr(u, 'is_support', False))}</code>\n"
        f"Contact: <code>{bool(getattr(u, 'is_contact', False))}</code>\n"
        f"Mutual contact: <code>{bool(getattr(u, 'is_mutual_contact', False))}</code>\n"
        f"Close friend: <code>{bool(getattr(u, 'is_close_friend', False))}</code>\n"
        f"Restricted: <code>{bool(getattr(u, 'is_restricted', False))}</code>\n"
        f"Restriction: <code>{restriction}</code>\n"
        f"Language: <code>{getattr(u, 'language_code', None) or '—'}</code>\n\n"
        f"<b>── Media ──</b>\n"
        f"Profile photos: <code>{photo_n}</code>\n\n"
        f"<b>── Common chats ──</b> ({common_n})\n"
        + ("\n".join(common_lines) if common_lines else "None / hidden")
        + f"\n\n<a href='tg://user?id={u.id}'>Open profile</a>"
    )

    try:
        await status.edit_text(body, disable_web_page_preview=True)
    except Exception:
        await message.reply_text(body, disable_web_page_preview=True)

    if first_photo:
        try:
            await client.send_photo(
                message.chat.id,
                first_photo,
                caption=f"DP — {u.first_name or u.id}",
            )
        except Exception:
            pass
