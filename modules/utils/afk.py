"""
AFK mode (userbot `app`):
  .afk [reason]   — AFK ON
  .unafk / .back  — AFK OFF
  .afkstatus      — current state

Jab AFK ho:
  - kisi ke reply / private / mention pe auto reply (cooldown per user)
"""
import time

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!"]

# in-memory (restart pe reset — OK for AFK)
_AFK_ON = False
_AFK_REASON = ""
_AFK_SINCE = 0.0
# user_id -> last reply time (anti-spam)
_LAST_REPLY: dict[int, float] = {}
REPLY_COOLDOWN = 30  # seconds per chatter


def _fmt_duration(sec: float) -> str:
    sec = int(sec)
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m {sec % 60}s"
    h = sec // 3600
    m = (sec % 3600) // 60
    return f"{h}h {m}m"


@app.on_message(filters.command(["afk"], prefixes=PREFIXES))
@sudo_only
async def afk_on(client, message: Message):
    global _AFK_ON, _AFK_REASON, _AFK_SINCE
    reason = " ".join(message.command[1:]).strip() if len(message.command) > 1 else "AFK"
    _AFK_ON = True
    _AFK_REASON = reason[:200]
    _AFK_SINCE = time.time()
    await set_feature("afk", True)
    await message.reply_text(
        f"💤 AFK **ON**\nReason: <i>{_AFK_REASON}</i>"
    )


@app.on_message(filters.command(["unafk", "back"], prefixes=PREFIXES))
@sudo_only
async def afk_off(client, message: Message):
    global _AFK_ON, _AFK_REASON, _AFK_SINCE
    was = _AFK_ON
    dur = _fmt_duration(time.time() - _AFK_SINCE) if _AFK_SINCE else "—"
    _AFK_ON = False
    _AFK_REASON = ""
    _AFK_SINCE = 0.0
    await set_feature("afk", False)
    _LAST_REPLY.clear()
    if was:
        await message.reply_text(f"✅ Back online (AFK duration: {dur}).")
    else:
        await message.reply_text("AFK pehle se OFF
