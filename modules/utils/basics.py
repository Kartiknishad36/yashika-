"""
basics — ping / alive / id
.help / .menu → modules/utils/help_cmd.py (premium colour menu)
"""
import time

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def cmd(name):
    return filters.command(name, prefixes=PREFIXES)


@app.on_message(cmd("ping"))
@sudo_only
async def ping_cmd(client, message: Message):
    start = time.time()
    msg = await message.reply_text("🏓 Pinging…")
    ms = (time.time() - start) * 1000
    await msg.edit_text(f"🏓 <b>Pong!</b> <code>{ms:.2f}ms</code>")


@app.on_message(cmd("alive"))
@sudo_only
async def alive_cmd(client, message: Message):
    await message.reply_text(
        f"✨ <b>{BOT_NAME}</b> is <b>ALIVE</b> 🔥\n"
        f"📖 <code>.help</code> — command center\n"
        f"⚡ <code>.ping</code> — speed"
    )


@app.on_message(cmd("id"))
@sudo_only
async def id_cmd(client, message: Message):
    chat_id = message.chat.id
    user_id = (
        message.reply_to_message.from_user.id
        if message.reply_to_message and message.reply_to_message.from_user
        else (message.from_user.id if message.from_user else "N/A")
    )
    await message.reply_text(
        f"🆔 <b>IDs</b>\nChat: <code>{chat_id}</code>\nUser: <code>{user_id}</code>"
    )
