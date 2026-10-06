"""
.info — premium full user info
  .info
  .info @user / id
  reply + .info
"""
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus

from core.clients import app
from database.mongo import get_warns
from modules.owner.sudoers import ub_cmd, sudo_only


def _yn(v) -> str:
    return "✅ Yes" if v else "❌ No"


def _status_text(status) -> str:
    if status is None:
        return "Hidden / Unknown"
    n = type(status).__name__
    if "Online" in n:
        return "🟢 Online"
    if "Offline" in n:
        was = getattr(status, "was_online", None)
        return f"⚫ Offline · last={was}" if was else "⚫ Offline"
    if "Recently" in n:
        return "🟡 Recently"
    if "LastWeek" in n:
        return "🟠 Last week"
    if "LastMonth" in n:
        return "🔴 Last month"
    if "Empty" in n:
        return "⚪ Long ago / Hidden"
    return n


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


async def _resolve(client, message: Message):
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


@app.on_message(ub_cmd("info", "whois"))
@sudo_only
async def info_cmd(client, message: Message):
    user = await _resolve(client, message)
    if not user:
        await message.reply_text("❌ User nahi mila.\nReply / <code>.info @user</code> / id")
        return

    m = await message.reply_text("⏳ <b>Fetching premium info…</b>")

    try:
        user = await client.get_users(user.id)
    except Exception:
        pass

    chat_obj = None
    try:
        chat_obj = await client.get_chat(user.id)
    except Exception:
        pass

    full_name = (user.first_name or "") + (f" {user.last_name}" if user.last_name else "")
    username = f"@{user.username}" if user.username else "—"
    bio = getattr(chat_obj, "bio", None) or getattr(user, "bio", None) or "—"
    phone = getattr(user, "phone_number", None) or "—"
    status_line = _status_text(getattr(user, "status", None))
    lang = getattr(user, "language_code", None) or "—"
    dc = getattr(user, "dc_id", None) or "—"

    # photos
    photo_n = 0
    try:
        async for _ in client.get_chat_photos(user.id, limit=50):
            photo_n += 1
    except Exception:
        pass

    # common chats count
    common_n = 0
    try:
        async for _ in client.get_common_chats(user.id):
            common_n += 1
            if common_n >= 100:
                break
    except Exception:
        pass

    text = (
        f"╔══ 💎 <b>PREMIUM USER INFO</b> ══╗\n\n"
        f"👤 <b>Name:</b> {full_name or '—'}\n"
        f"🔖 <b>Username:</b> {username}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"📞 <b>Phone:</b> <code>{phone}</code>\n"
        f"🌐 <b>DC:</b> <code>{dc}</code>\n"
        f"📡 <b>Status:</b> {status_line}\n"
        f"🗣 <b>Language:</b> <code>{lang}</code>\n"
        f"📝 <b>Bio:</b> {str(bio)[:180]}\n\n"
        f"<b>─── 🏷 Flags ───</b>\n"
        f"⭐ Premium: {_yn(getattr(user, 'is_premium', False))}\n"
        f"✅ Verified: {_yn(getattr(user, 'is_verified', False))}\n"
        f"🤖 Bot: {_yn(user.is_bot)}\n"
        f"🗑 Deleted: {_yn(getattr(user, 'is_deleted', False))}\n"
        f"🎭 Fake: {_yn(getattr(user, 'is_fake', False))}\n"
        f"⚠️ Scam: {_yn(getattr(user, 'is_scam', False))}\n"
        f"🛟 Support: {_yn(getattr(user, 'is_support', False))}\n"
        f"📇 Contact: {_yn(getattr(user, 'is_contact', False))}\n"
        f"🤝 Mutual: {_yn(getattr(user, 'is_mutual_contact', False))}\n"
        f"💜 Close friend: {_yn(getattr(user, 'is_close_friend', False))}\n"
        f"🔒 Restricted: {_yn(getattr(user, 'is_restricted', False))}\n"
        f"🖼 Profile photos: <code>{photo_n}</code>\n"
        f"🔗 Common chats: <code>{common_n}</code>\n"
    )

    # group context
    if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        text += f"\n<b>─── 🏠 This chat ───</b>\n"
        try:
            member = await client.get_chat_member(message.chat.id, user.id)
            text += f"Status: {_member_status(member.status)}\n"
            title = getattr(member, "title", None)
            if title:
                text += f"Title: <code>{title}</code>\n"
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
                    text += f"Rights: <code>{', '.join(bits)}</code>\n"
        except Exception:
            text += "Status: <i>not in chat / hidden</i>\n"

        try:
            warns = await get_warns(message.chat.id, user.id)
            text += f"Warns here: <code>{len(warns)}</code>\n"
        except Exception:
            pass

    text += (
        f"\n<a href='tg://user?id={user.id}'>Open profile</a>"
        f"\n╚══════════════════════╝"
    )

    try:
        await m.edit_text(text, disable_web_page_preview=True)
    except Exception:
        await message.reply_text(text, disable_web_page_preview=True)

    # send current DP if any
    try:
        async for p in client.get_chat_photos(user.id, limit=1):
            await client.send_photo(
                message.chat.id,
                p.file_id,
                caption=f"🖼 DP — {full_name or user.id}",
            )
            break
    except Exception:
        pass
