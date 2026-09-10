"""
LOG_GROUP / LOGGER_ID logs — NISHAD40 style:
  bot/assistant start, group add/remove, play log
"""
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus, ParseMode

from core.clients import bot, app, assistant
from config import BOT_NAME, BOT_USERNAME

try:
    from config import LOG_GROUP_ID
except ImportError:
    LOG_GROUP_ID = None

try:
    from config import LOGGER_ID as _LOGGER_ID
except ImportError:
    _LOGGER_ID = None

LOGGER_CHAT = LOG_GROUP_ID or _LOGGER_ID

if bot is None:
    raise RuntimeError("logger needs BOT_TOKEN")


async def _send(text: str):
    if not LOGGER_CHAT:
        return
    try:
        await bot.send_message(
            LOGGER_CHAT,
            text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"[logger] send failed: {e}")


async def send_startup_logs():
    if not LOGGER_CHAT:
        print("[logger] LOG_GROUP_ID / LOGGER_ID not set")
        return

    # Bot started
    try:
        me = await bot.get_me()
        await _send(
            f"<u><b>» {me.mention} BOT STARTED :</b></u>\n\n"
            f"ID : <code>{me.id}</code>\n"
            f"NAME : {me.first_name}\n"
            f"USERNAME : @{me.username or 'None'}"
        )
    except Exception as e:
        print(f"[logger] bot start: {e}")

    # Assistant started
    if assistant:
        try:
            am = await assistant.get_me()
            try:
                await assistant.send_message(LOGGER_CHAT, "Assistant Started")
            except Exception:
                await _send(
                    f"» <b>ASSISTANT STARTED</b>\n\n"
                    f"ID : <code>{am.id}</code>\n"
                    f"NAME : {am.first_name}\n"
                    f"USERNAME : @{am.username or 'None'}"
                )
        except Exception as e:
            print(f"[logger] assistant: {e}")

    # Userbot
    if app:
        try:
            um = await app.get_me()
            await _send(
                f"» <b>USERBOT STARTED</b>\n\n"
                f"ID : <code>{um.id}</code>\n"
                f"NAME : {um.first_name}\n"
                f"USERNAME : @{um.username or 'None'}"
            )
        except Exception as e:
            print(f"[logger] userbot: {e}")

    await _send(
        f"❖ <b>{BOT_NAME.upper()}</b> IS ALIVE.\n\n"
        f"◎ TIME : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )


async def play_logs(message, streamtype: str = "youtube"):
    """Same shape as NISHAD40 utils/logger.play_logs"""
    if not LOGGER_CHAT or not message.from_user:
        return
    if message.chat.id == LOGGER_CHAT:
        return
    un = message.from_user.username or "None"
    cun = message.chat.username or "None"
    try:
        q = message.text.split(None, 1)[1]
    except Exception:
        q = message.text or ""
    text = (
        f"<b>{BOT_NAME.upper()} PLAY LOG</b>\n\n"
        f"<b>CHAT ID :</b> <code>{message.chat.id}</code>\n"
        f"<b>CHAT NAME :</b> {message.chat.title}\n"
        f"<b>CHAT USERNAME :</b> @{cun}\n\n"
        f"<b>USER ID :</b> <code>{message.from_user.id}</code>\n"
        f"<b>NAME :</b> {message.from_user.mention}\n"
        f"<b>USERNAME :</b> @{un}\n\n"
        f"<b>QUERY :</b> {q}\n"
        f"<b>STREAMTYPE :</b> {streamtype}"
    )
    await _send(text)


# music.py compatible helper
async def log_play(chat_id, chat_title, chat_username, user, query, stream_type="youtube"):
    if not LOGGER_CHAT or not user:
        return
    if chat_id == LOGGER_CHAT:
        return
    text = (
        f"<b>{BOT_NAME.upper()} PLAY LOG</b>\n\n"
        f"<b>CHAT ID :</b> <code>{chat_id}</code>\n"
        f"<b>CHAT NAME :</b> {chat_title or 'Unknown'}\n"
        f"<b>CHAT USERNAME :</b> @{chat_username or 'None'}\n\n"
        f"<b>USER ID :</b> <code>{user.id}</code>\n"
        f"<b>NAME :</b> {user.mention}\n"
        f"<b>USERNAME :</b> @{user.username or 'None'}\n\n"
        f"<b>QUERY :</b> {query}\n"
        f"<b>STREAMTYPE :</b> {stream_type}"
    )
    await _send(text)


@bot.on_chat_member_updated()
async def on_bot_membership(client, update: ChatMemberUpdated):
    if not LOGGER_CHAT:
        return
    me = await client.get_me()
    if not update.new_chat_member or update.new_chat_member.user.id != me.id:
        return

    chat = update.chat
    old, new = update.old_chat_member, update.new_chat_member
    was = old and old.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED)
    now = new.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED)
    by = update.from_user

    if now and not was:
        try:
            count = await client.get_chat_members_count(chat.id)
        except Exception:
            count = "?"
        link = f"https://t.me/{chat.username}" if chat.username else "None"
        await _send(
            f"📝 <b>MUSIC BOT ADDED IN A NEW GROUP</b>\n\n"
            f"📌 CHAT NAME: <b>{chat.title}</b>\n"
            f"🆔 CHAT ID: <code>{chat.id}</code>\n"
            f"🔒 USERNAME: @{chat.username or 'None'}\n"
            f"🔗 LINK: {link}\n"
            f"👥 MEMBERS: {count}\n"
            f"😊 ADDED BY: {by.mention if by else '?'}\n"
            f"   ID: <code>{by.id if by else '?'}</code>"
        )
    elif was and not now:
        await _send(
            f"☆ <b>#LEFT_GROUP</b> ☆\n\n"
            f"CHAT TITLE : <b>{chat.title}</b>\n\n"
            f"CHAT ID : <code>{chat.id}</code>\n\n"
            f"REMOVED BY : {by.mention if by else '?'}\n\n"
            f"BOT : @{me.username or BOT_USERNAME or 'bot'}"
  )
