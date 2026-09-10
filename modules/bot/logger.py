"""
LOG_GROUP alerts (Kartik-style):
  - Bot / assistant started
  - Bot added to group (full info)
  - Bot removed from group
  - Play log (who played what, where)
"""
import asyncio
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus, ChatType

from core.clients import bot, app, assistant
from config import LOG_GROUP_ID, BOT_NAME, BOT_USERNAME

if bot is None:
    raise RuntimeError("logger needs BOT_TOKEN")


def _log_chat():
    return LOG_GROUP_ID


async def _send_log(text: str, photo: str | None = None):
    chat = _log_chat()
    if not chat:
        return
    try:
        if photo:
            await bot.send_photo(chat, photo, caption=text)
        else:
            await bot.send_message(chat, text)
    except Exception as e:
        print(f"[logger] send failed: {e}")


# ---------- startup (call from main.py) ----------
async def send_startup_logs():
    if not _log_chat():
        print("[logger] LOG_GROUP_ID not set — skip startup logs")
        return

    try:
        me = await bot.get_me()
        uname = f"@{me.username}" if me.username else "None"
        text = (
            f"» <b>{BOT_NAME.upper()}</b> BOT STARTED :\n\n"
            f"ID : <code>{me.id}</code>\n"
            f"NAME : <b>{me.first_name}</b>\n"
            f"USERNAME : {uname}"
        )
        await _send_log(text)
    except Exception as e:
        print(f"[logger] bot start log: {e}")

    if assistant:
        try:
            am = await assistant.get_me()
            await _send_log(
                f"» <b>ASSISTANT STARTED</b>\n\n"
                f"ID : <code>{am.id}</code>\n"
                f"NAME : <b>{am.first_name}</b>\n"
                f"USERNAME : @{am.username or 'None'}"
            )
        except Exception as e:
            print(f"[logger] assistant start log: {e}")

    if app:
        try:
            um = await app.get_me()
            await _send_log(
                f"» <b>USERBOT STARTED</b>\n\n"
                f"ID : <code>{um.id}</code>\n"
                f"NAME : <b>{um.first_name}</b>\n"
                f"USERNAME : @{um.username or 'None'}"
            )
        except Exception as e:
            print(f"[logger] userbot start log: {e}")

    # Alive card
    try:
        await _send_log(
            f"❖ <b>{BOT_NAME.upper()}</b> IS ALIVE.\n\n"
            f"◎ UPTIME : just started\n"
            f"◎ TIME : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )
    except Exception:
        pass


# ---------- bot added / removed ----------
@bot.on_chat_member_updated()
async def on_bot_membership(client, update: ChatMemberUpdated):
    if not _log_chat():
        return
    me = await client.get_me()
    if not update.new_chat_member or update.new_chat_member.user.id != me.id:
        return

    chat = update.chat
    old = update.old_chat_member
    new = update.new_chat_member

    was_member = old and old.status not in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED,
    )
    is_member = new.status not in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED,
    )

    # ADDED
    if is_member and not was_member:
        by = update.from_user
        try:
            count = await client.get_chat_members_count(chat.id)
        except Exception:
            count = "?"
        link = "None"
        if getattr(chat, "username", None):
            link = f"https://t.me/{chat.username}"
        text = (
            f"📝 <b>MUSIC BOT ADDED IN A NEW GROUP</b>\n\n"
            f"📌 CHAT NAME: <b>{chat.title or 'Unknown'}</b>\n"
            f"🆔 CHAT ID: <code>{chat.id}</code>\n"
            f"🔒 CHAT USERNAME: @{chat.username or 'None'}\n"
            f"🔗 CHAT LINK: {link}\n"
            f"👥 GROUP MEMBERS: {count}\n"
            f"😊 ADDED BY: {by.mention if by else 'Unknown'}\n"
            f"   USER ID: <code>{by.id if by else '?'}</code>"
        )
        await _send_log(text)
        return

    # REMOVED
    if was_member and not is_member:
        by = update.from_user
        text = (
            f"☆ <b>#LEFT_GROUP</b> ☆\n\n"
            f"CHAT TITLE : <b>{chat.title or 'Unknown'}</b>\n\n"
            f"CHAT ID : <code>{chat.id}</code>\n\n"
            f"REMOVED BY : {by.mention if by else 'Unknown'}\n\n"
            f"BOT : @{me.username or BOT_USERNAME or 'bot'}"
        )
        await _send_log(text)


# ---------- play log (call from music.py) ----------
async def log_play(
    chat_id: int,
    chat_title: str,
    chat_username: str | None,
    user,
    query: str,
    stream_type: str = "youtube",
):
    if not _log_chat():
        return
    un = f"@{user.username}" if user and user.username else "@None"
    name = user.first_name if user else "?"
    uid = user.id if user else "?"
    cun = f"@{chat_username}" if chat_username else "@None"
    text = (
        f"<b>{BOT_NAME.upper()} PLAY LOG</b>\n\n"
        f"CHAT ID : <code>{chat_id}</code>\n"
        f"CHAT NAME : <b>{chat_title or 'Unknown'}</b>\n"
        f"CHAT USERNAME : {cun}\n\n"
        f"USER ID : <code>{uid}</code>\n"
        f"NAME : {name}\n"
        f"USERNAME : {un}\n\n"
        f"QUERY : <code>{query}</code>\n"
        f"STREAMTYPE : {stream_type}"
    )
    await _send_log(text)
