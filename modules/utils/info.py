"""
.info / .whois — full Telegram user details
  .info
  .info @user / id
  reply + .info
"""
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus, UserStatus

from core.clients import app
from config import OWNER_ID
from database.mongo import get_warns
from modules.owner.sudoers import ub_cmd, sudo_only


def _yn(v) -> str:
    return "✅ Yes" if v else "❌ No"


def _status_line(status) -> str:
    if status is None:
        return "Hidden / Unknown"
    if status == UserStatus.ONLINE:
        return "🟢 Online"
    if status == UserStatus.OFFLINE:
        was = getattr(status, "was_online", None)
        return f"⚫ Offline · last={was}" if was else "⚫ Offline"
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


@app.on_message(ub_cmd("info", "whois"))
@sudo_only
async def info_cmd(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
    else:
        parts = (message.text or "").split()
        target = parts[1].lstrip("@") if len(parts) > 1 else "me"

    status_msg = await message.reply_text("⏳ Fetching full info…")
    try:
        user = await client.get_users(target)
        try:
            chat = await client.get_chat(user.id)
        except Exception:
            chat = None

        try:
            common = len(await client.get_common_chats(user.id))
        except Exception:
            common = 0

        full = (user.first_name or "") + (f" {user.last_name}" if user.last_name else "")
        bio = getattr(chat, "bio", None) or "—"
        status = _status_line(getattr(user, "status", None))
        link = f"<a href='tg://user?id={user.id}'>{'👑 OWNER' if OWNER_ID and user.id == OWNER_ID else (user.first_name or user.id)}</a>"

        photo_n = 0
        try:
            async for _ in client.get_chat_photos(user.id, limit=50):
                photo_n += 1
        except Exception:
            pass

        lines = [
            "╔══ 💎 <b>FULL USER INFO</b> ══╗",
            "",
            f"👤 <b>Name:</b> {full or '—'}",
            f"🔖 <b>Username:</b> @{user.username or '—'}",
            f"🆔 <b>User ID:</b> <code>{user.id}</code>",
            f"🔗 <b>Profile link:</b> {link}",
            f"🏛 <b>DC ID:</b> <code>{getattr(user, 'dc_id', '—')}</code>",
            f"📡 <b>Status:</b> {status}",
            f"🗣 <b>Language:</b> <code>{getattr(user, 'language_code', None) or '—'}</code>",
            f"📝 <b>Bio:</b> {str(bio)[:200]}",
            "",
            "<b>─── Flags ───</b>",
            f"⭐ Premium: {_yn(getattr(user, 'is_premium', False))}",
            f"✅ Verified: {_yn(getattr(user, 'is_verified', False))}",
            f"🤖 Bot: {_yn(user.is_bot)}",
            f"🗑 Deleted: {_yn(getattr(user, 'is_deleted', False))}",
            f"🎭 Fake: {_yn(getattr(user, 'is_fake', False))}",
            f"⚠️ Scam: {_yn(getattr(user, 'is_scam', False))}",
            f"🛟 Support: {_yn(getattr(user, 'is_support', False))}",
            f"📇 Contact: {_yn(getattr(user, 'is_contact', False))}",
            f"🤝 Mutual: {_yn(getattr(user, 'is_mutual_contact', False))}",
            f"💜 Close friend: {_yn(getattr(user, 'is_close_friend', False))}",
            f"🔒 Restricted: {_yn(getattr(user, 'is_restricted', False))}",
            f"🖼 Profile photos: <code>{photo_n}</code>",
            f"👀 Common chats: <code>{common}</code>",
        ]

        if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            lines.append("")
            lines.append("<b>─── This chat ───</b>")
            try:
                member = await client.get_chat_member(message.chat.id, user.id)
                lines.append(f"Status: {_member_status(member.status)}")
                title = getattr(member, "title", None)
                if title:
                    lines.append(f"Title: <code>{title}</code>")
                perms = getattr(member, "privileges", None)
                if perms:
                    bits = []
                    for attr, label in [
                        ("can_manage_chat", "manage"),
                        ("can_delete_messages", "delete"),
                        ("can_restrict_members", "ban"),
                        ("can_promote_members", "promote"),
                        ("can_change_info", "info"),
                        ("can_invite_users", "invite"),
                        ("can_pin_messages", "pin"),
                        ("can_manage_video_chats", "vc"),
                    ]:
                        if getattr(perms, attr, False):
                            bits.append(label)
                    if bits:
                        lines.append(f"Rights: <code>{', '.join(bits)}</code>")
            except Exception:
                lines.append("Status: <i>not in chat / hidden</i>")
            try:
                warns = await get_warns(message.chat.id, user.id)
                lines.append(f"Warns here: <code>{len(warns)}</code>")
            except Exception:
                pass

        lines.append("")
        lines.append("╚══════════════════════╝")
        text = "\n".join(lines)

        try:
            await status_msg.delete()
        except Exception:
            pass

        photos = []
        try:
            async for p in client.get_chat_photos(user.id, limit=1):
                photos.append(p.file_id)
        except Exception:
            pass

        if photos:
            await client.send_photo(message.chat.id, photos[0], caption=text)
        else:
            await message.reply_text(text)
    except Exception as e:
        try:
            await status_msg.edit_text(f"❌ <code>{type(e).__name__}: {e}</code>")
        except Exception:
            await message.reply_text(f"❌ <code>{e}</code>")
