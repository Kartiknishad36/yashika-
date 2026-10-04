"""
.afk [reason] · .unafk / .back · .afkstatus
"""
import time

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only
from database.mongo import set_feature

_AFK_ON = False
_AFK_REASON = ""
_AFK_SINCE = 0.0
_LAST_REPLY: dict[int, float] = {}
REPLY_COOLDOWN = 30


def _fmt_duration(sec: float) -> str:
    sec = int(sec)
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m {sec % 60}s"
    h = sec // 3600
    m = (sec % 3600) // 60
    return f"{h}h {m}m"


@app.on_message(ub_cmd("afk"))
@sudo_only
async def afk_on(client, message: Message):
    global _AFK_ON, _AFK_REASON, _AFK_SINCE
    parts = (message.text or "").split(None, 1)
    reason = parts[1].strip()[:200] if len(parts) > 1 else "AFK"
    _AFK_ON = True
    _AFK_REASON = reason
    _AFK_SINCE = time.time()
    await set_feature("afk", True)
    await message.reply_text(f"AFK <b>ON</b>\nReason: <i>{_AFK_REASON}</i>")


@app.on_message(ub_cmd("unafk", "back"))
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
        await message.reply_text(f"Back online (AFK: {dur}).")
    else:
        await message.reply_text("AFK pehle se OFF tha.")


@app.on_message(ub_cmd("afkstatus"))
@sudo_only
async def afk_status(client, message: Message):
    if not _AFK_ON:
        await message.reply_text("AFK: <b>OFF</b>")
        return
    await message.reply_text(
        f"AFK: <b>ON</b>\n"
        f"Reason: <i>{_AFK_REASON}</i>\n"
        f"Since: {_fmt_duration(time.time() - _AFK_SINCE)}"
    )


@app.on_message(
    filters.incoming & ~filters.bot & ~filters.service & ~filters.me,
    group=15,
)
async def afk_watcher(client, message: Message):
    if not _AFK_ON or not message.from_user:
        return
    try:
        me = await client.get_me()
    except Exception:
        return
    uid = message.from_user.id
    if uid == me.id:
        return

    should = False
    if message.chat.type == ChatType.PRIVATE:
        should = True
    else:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == me.id
        ):
            should = True
        if not should and me.username:
            t = (message.text or message.caption or "").lower()
            if f"@{me.username.lower()}" in t:
                should = True
        if not should and message.entities:
            for e in message.entities:
                if getattr(e.type, "name", "") == "TEXT_MENTION" and e.user and e.user.id == me.id:
                    should = True
                    break

    if not should:
        return
    now = time.time()
    if now - _LAST_REPLY.get(uid, 0) < REPLY_COOLDOWN:
        return
    _LAST_REPLY[uid] = now
    dur = _fmt_duration(now - _AFK_SINCE) if _AFK_SINCE else "?"
    try:
        await message.reply_text(
            f"<b>I'm AFK</b>\n"
            f"Reason: <i>{_AFK_REASON or 'AFK'}</i>\n"
            f"Since: {dur}"
        )
    except Exception:
        pass
