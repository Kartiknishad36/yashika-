"""
.info — reply / @user / id / me
"""
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus, UserStatus

from core.clients import app
from config import OWNER_ID
from database.mongo import get_warns
from modules.owner.sudoers import ub_cmd, sudo_only


def _status_line(status) -> str:
    if status is None:
        return "Unknown"
    if status == UserStatus.ONLINE:
        return "Online 🟢"
    if status == UserStatus.OFFLINE:
        return "Offline ⚫"
    if status == UserStatus.RECENTLY:
        return "Recently 🟡"
    if status == UserStatus.LAST_WEEK:
        return "Last week 🟠"
    if status == UserStatus.LAST_MONTH:
        return "Last month 🔴"
    return str(status)


@app.on_message(ub_cmd("info", "whois"))
@sudo_only
async def info_cmd(client, message: Message):
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
    else:
        parts = (message.text or "").split()
        if len(parts) > 1:
            target = parts[1].lstrip("@")
        else:
            target = "me"

    status_msg = await message.reply_text("Processing…")
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

        status = _status_line(getattr(user, "status", None))
        bio = getattr(chat, "bio", None) or "—"
        full = (user.first_name or "") + ((" " + user.last_name) if user.last_name else "")

        if OWNER_ID and user.id == OWNER_ID:
            link = "<a href='tg://user?id=" + str(user.id) + "'>👑 OWNER</a>"
        else:
            link = "<a href='tg://user?id=" + str(user.id) + "'>" + str(user.first_name or user.id) + "</a>"

        warns_line = ""
        if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            try:
                member = await client.get_chat_member(message.chat.id, user.id)
                st = member.status
                if st == ChatMemberStatus.OWNER:
                    ms = "👑 Owner"
                elif st == ChatMemberStatus.ADMINISTRATOR:
                    ms = "🛡 Admin"
                elif st == ChatMemberStatus.MEMBER:
                    ms = "👤 Member"
                else:
                    ms = str(st)
                warns = await get_warns(message.chat.id, user.id)
                warns_line = "\n📍 In this chat: <b>" + ms + "</b>\n⚠️ Warns: <code>" + str(len(warns)) + "</code>"
            except Exception:
                pass

        caption = (
            "<b>USER INFORMATION</b>\n\n"
            "🆔 ID: <code>" + str(user.id) + "</code>\n"
            "👤 Name: " + full + "\n"
            "🌐 Username: @" + (user.username or "—") + "\n"
            "🏛 DC: <code>" + str(getattr(user, "dc_id", "—")) + "</code>\n"
            "🤖 Bot: " + str(user.is_bot) + "\n"
            "⭐ Premium: " + str(bool(getattr(user, "is_premium", False))) + "\n"
            "✅ Verified: " + str(bool(getattr(user, "is_verified", False))) + "\n"
            "🚫 Scam: " + str(bool(getattr(user, "is_scam", False))) + "\n"
            "📝 Bio: " + str(bio)[:200] + "\n"
            "👀 Common groups: <code>" + str(common) + "</code>\n"
            "👁 Status: " + status + "\n"
            "🔗 Link: " + link
            + warns_line
        )

        photos = []
        try:
            async for p in client.get_chat_photos(user.id, limit=1):
                photos.append(p.file_id)
        except Exception:
            pass

        try:
            await status_msg.delete()
        except Exception:
            pass

        if photos:
            await client.send_photo(message.chat.id, photos[0], caption=caption)
        else:
            await message.reply_text(caption)
    except Exception as e:
        try:
            await status_msg.edit_text("❌ <code>" + type(e).__name__ + ": " + str(e) + "</code>")
        except Exception:
            await message.reply_text("❌ <code>" + str(e) + "</code>")
