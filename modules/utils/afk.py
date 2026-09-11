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
        await message.reply_text("AFK pehle se OFF tha.")


@app.on_message(filters.command(["afkstatus"], prefixes=PREFIXES))
@sudo_only
async def afk_status(client, message: Message):
    if not _AFK_ON:
        await message.reply_text("AFK: **OFF**")
        return
    await message.reply_text(
        f"AFK: **ON**\n"
        f"Reason: <i>{_AFK_REASON}</i>\n"
        f"Since: {_fmt_duration(time.time() - _AFK_SINCE)}"
    )


@app.on_message(
    filters.incoming & \~filters.bot & \~filters.service & \~filters.me,
    group=15,
)
async def afk_watcher(client, message: Message):
    global _AFK_ON
    if not _AFK_ON:
        return
    if not message.from_user:
        return

    # ignore own commands path already \~filters.me
    try:
        me = await client.get_me()
    except Exception:
        return

    uid = message.from_user.id
    if uid == me.id:
        return

    should = False
    # 1) Private chat
    if message.chat.type == ChatType.PRIVATE:
        should = True
    else:
        # 2) Reply to me
        if (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == me.id
        ):
            should = True
        # 3) Mention me
        if not should and message.entities and me.username:
            t = (message.text or message.caption or "").lower()
            if f"@{me.username.lower()}" in t:
                should = True
        if not should and message.entities:
            for e in message.entities:
                if e.type.name == "TEXT_MENTION" and e.user and e.user.id == me.id:
                    should = True
                    break

    if not should:
        return

    now = time.time()
    last = _LAST_REPLY.get(uid, 0)
    if now - last < REPLY_COOLDOWN:
        return
    _LAST_REPLY[uid] = now

    dur = _fmt_duration(now - _AFK_SINCE) if _AFK_SINCE else "?"
    text = (
        f"💤 <b>I'm AFK</b>\n"
        f"Reason: <i>{_AFK_REASON or 'AFK'}</i>\n"
        f"Since: {dur}"
    )
    try:
        await message.reply_text(text)
    except Exception:
        pass
