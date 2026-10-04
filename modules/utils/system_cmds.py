import os
import sys
import time
import asyncio
from datetime import timedelta

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd
from config import BOT_NAME, OWNER_ID

START_TIME = time.time()
VERSION = "Yashika 2.0"


def _uptime() -> str:
    return str(timedelta(seconds=int(time.time() - START_TIME)))


@app.on_message(ub_cmd("uptime", "runtime") & filters.me)
async def uptime_cmd(client, message: Message):
    await message.reply_text(
        f"<b>Uptime</b>\n<code>{_uptime()}</code>\n"
        f"Bot: <b>{BOT_NAME or 'Yashika'}</b>"
    )


@app.on_message(ub_cmd("about", "version") & filters.me)
async def about_cmd(client, message: Message):
    me = await client.get_me()
    await message.reply_text(
        f"<b>{BOT_NAME or 'Yashika'}</b>\n"
        f"Version: <code>{VERSION}</code>\n"
        f"Userbot: <code>{me.id}</code>\n"
        f"@{me.username or '—'}\n"
        f"Uptime: <code>{_uptime()}</code>\n"
        f"Owner: <code>{OWNER_ID}</code>"
    )


@app.on_message(ub_cmd("restart") & filters.me)
async def restart_cmd(client, message: Message):
    await message.reply_text("Restarting…")
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable, *sys.argv])


@app.on_message(ub_cmd("shutdown") & filters.me)
async def shutdown_cmd(client, message: Message):
    await message.reply_text("Shutdown…")
    await asyncio.sleep(1)
    os._exit(0)


@app.on_message(ub_cmd("logs") & filters.me)
async def logs_cmd(client, message: Message):
    for path in ("bot.log", "logs/bot.log", "output.log"):
        if os.path.exists(path):
            await message.reply_document(path, caption="Logs")
            return
    await message.reply_text("Log file nahi mili (Railway dashboard dekho).")
