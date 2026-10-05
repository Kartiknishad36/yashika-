import os
import sys
import time
import asyncio
from datetime import timedelta

from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only
from config import BOT_NAME, OWNER_ID

START_TIME = time.time()
VERSION = "Yashika 2.0"


def _uptime() -> str:
    return str(timedelta(seconds=int(time.time() - START_TIME)))


@app.on_message(ub_cmd("uptime", "runtime"))
@sudo_only
async def uptime_cmd(client, message: Message):
    await message.reply_text(
        f"<b>Uptime</b>\n<code>{_uptime()}</code>\n"
        f"Bot: <b>{BOT_NAME or 'Yashika'}</b>"
    )


@app.on_message(ub_cmd("about", "version"))
@sudo_only
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


@app.on_message(ub_cmd("restart"))
@sudo_only
async def restart_cmd(client, message: Message):
    await message.reply_text("Restarting…")
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable] + sys.argv)


@app.on_message(ub_cmd("logs"))
@sudo_only
async def logs_cmd(client, message: Message):
    await message.reply_text("Check Railway / host logs for full output.")
