"""
Broadcast — OWNER_ID + sudo users only.
Works from group or DM.
  /broadcast <text>  or  .broadcast <text>
  Reply + /broadcast  → copy that message to all tracked chats
"""
import asyncio
import functools

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait

from core.clients import app, bot
from config import OWNER_ID
from database.mongo import get_all_chats, get_sudoers

PREFIXES = ["/", ".", "!"]


async def _allowed(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    try:
        if user_id in await get_sudoers():
            return True
    except Exception:
        pass
    # in-memory list if load_sudoers filled it
    try:
        from modules.owner.sudoers import SUDO_USERS
        if user_id in SUDO_USERS:
            return True
    except Exception:
        pass
    return False


def owner_or_sudo(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user:
            return
        if not await _allowed(message.from_user.id):
            await message.reply_text("❌ Sirf OWNER / sudo is command ko use kar sakte hain.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper


async def _do_broadcast(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text(
            "Usage:\n"
            "`/broadcast <text>`\n"
            "ya kisi message pe reply karke `/broadcast`"
        )
        return

    chats = await get_all_chats()
    if not chats:
        await message.reply_text(
            "Koi tracked chat nahi. Bot/userbot ko group mein ek message dekhna chahiye."
        )
        return

    status = await message.reply_text(f"📢 Broadcasting to {len(chats)} chat(s)...")

    sent, failed = 0, 0
    text = None
    if not message.reply_to_message:
        text = message.text.split(None, 1)[1]

    for chat_id in chats:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(chat_id)
            else:
                await client.send_message(chat_id, text)
            sent += 1
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(chat_id)
                else:
                    await client.send_message(chat_id, text)
                sent += 1
            except RPCError:
                failed += 1
        except RPCError:
            failed += 1
        await asyncio.sleep(0.15)  # mild flood protect

    try:
        await status.edit_text(f"📢 Done — sent: <b>{sent}</b> | failed: <b>{failed}</b>")
    except Exception:
        pass


@app.on_message(filters.command(["broadcast", "gcast"], prefixes=PREFIXES))
@owner_or_sudo
async def broadcast_app(client, message: Message):
    await _do_broadcast(client, message)


if bot is not None:
    @bot.on_message(filters.command(["broadcast", "gcast"], prefixes=PREFIXES))
    @owner_or_sudo
    async def broadcast_bot(client, message: Message):
        await _do_broadcast(client, message)
