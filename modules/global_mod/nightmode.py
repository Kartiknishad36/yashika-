"""
.nightmode on|off
.nightmode 00:00 06:00
Raat me group permissions lock (best-effort).
"""
import asyncio
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]
_TASKS: dict[int, asyncio.Task] = {}


def _parse_hhmm(s: str):
    h, m = s.split(":")
    return int(h), int(m)


async def _loop(client, chat_id: int):
    while await get_chat_flag(chat_id, "nightmode", False):
        start = await get_chat_flag(chat_id, "night_start", "00:00") or "00:00"
        end = await get_chat_flag(chat_id, "night_end", "06:00") or "06:00"
        try:
            sh, sm = _parse_hhmm(start)
            eh, em = _parse_hhmm(end)
        except Exception:
            sh, sm, eh, em = 0, 0, 6, 0
        now = datetime.now()
        mins = now.hour * 60 + now.minute
        a, b = sh * 60 + sm, eh * 60 + em
        in_night = a <= mins < b if a < b else (mins >= a or mins < b)
        try:
            if in_night:
                await client.set_chat_permissions(
                    chat_id,
                    ChatPermissions(can_send_messages=False),
                )
            else:
                await client.set_chat_permissions(
                    chat_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                    ),
                )
        except Exception:
            pass
        await asyncio.sleep(60)


@app.on_message(filters.command("nightmode", prefixes=PREFIXES) & filters.group)
@sudo_only
async def nightmode_cmd(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await get_chat_flag(chat_id, "nightmode", False)
        s = await get_chat_flag(chat_id, "night_start", "00:00")
        e = await get_chat_flag(chat_id, "night_end", "06:00")
        await message.reply_text(
            f"🌙 NightMode: <b>{'ON' if on else 'OFF'}</b>\n"
            f"<code>{s}</code> → <code>{e}</code>\n"
            f"<code>.nightmode on</code>\n"
            f"<code>.nightmode off</code>\n"
            f"<code>.nightmode 00:00 06:00</code>"
        )
        return

    arg = message.command[1].lower()
    if arg in ("off", "0"):
        await set_chat_flag(chat_id, "nightmode", False)
        t = _TASKS.pop(chat_id, None)
        if t:
            t.cancel()
        await message.reply_text("❌ NightMode OFF")
        return

    if ":" in arg and len(message.command) >= 3:
        await set_chat_flag(chat_id, "night_start", message.command[1])
        await set_chat_flag(chat_id, "night_end", message.command[2])
        await message.reply_text(
            f"✅ Window: <code>{message.command[1]}</code>–<code>{message.command[2]}</code>"
        )
        return

    if arg in ("on", "1"):
        await set_chat_flag(chat_id, "nightmode", True)
        if chat_id not in _TASKS or _TASKS[chat_id].done():
            _TASKS[chat_id] = asyncio.create_task(_loop(client, chat_id))
        await message.reply_text("✅ NightMode ON (admin rights needed)")
        return

    await message.reply_text("Usage: on/off / HH:MM HH:MM")
