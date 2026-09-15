"""
.stats — uptime + chats count
"""
import time
from datetime import timedelta
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import get_all_chats
from config import BOT_NAME

PREFIXES = [".", "!"]
START = time.time()


@app.on_message(filters.command(["stats", "botstats"], prefixes=PREFIXES))
@sudo_only
async def stats_cmd(client, message: Message):
    up = str(timedelta(seconds=int(time.time() - START)))
    try:
        chats = await get_all_chats()
        n = len(chats) if chats else 0
    except Exception:
        n = 0
    me = await client.get_me()
    await message.reply_text(
        f"📊 <b>{BOT_NAME} Stats</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Uptime: <code>{up}</code>\n"
        f"Tracked chats: <code>{n}</code>\n"
        f"Account: <code>{me.id}</code>\n"
        f"@{me.username or '—'}\n"
        f"━━━━━━━━━━━━━━"
    )
