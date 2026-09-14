"""
.remind 10m buy milk
.remind 2h call
.remind 1d birthday
"""
import asyncio
import re

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
_TASKS = []


def _parse_delay(s: str) -> int | None:
    m = re.fullmatch(r"(\d+)(s|m|h|d)", s.lower())
    if not m:
        return None
    n, u = int(m.group(1)), m.group(2)
    return n * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]


@app.on_message(filters.command(["remind", "reminder"], prefixes=PREFIXES))
@sudo_only
async def remind_cmd(client, message: Message):
    if len(message.command) < 3:
        await message.reply_text(
            "Usage:\n<code>.remind 10m text</code>\n"
            "<code>.remind 2h call mom</code>\n"
            "Units: s m h d"
        )
        return

    delay = _parse_delay(message.command[1])
    if delay is None or delay < 5 or delay > 86400 * 7:
        await message.reply_text("Time 5s–7d: <code>10m</code> <code>2h</code>")
        return

    text = message.text.split(None, 2)[2]
    chat_id = message.chat.id
    await message.reply_text(f"⏰ Reminder set: <b>{message.command[1]}</b>\n{text}")

    async def _job():
        await asyncio.sleep(delay)
        try:
            await client.send_message(chat_id, f"⏰ <b>Reminder</b>\n{text}")
        except Exception:
            pass

    _TASKS.append(asyncio.create_task(_job()))
