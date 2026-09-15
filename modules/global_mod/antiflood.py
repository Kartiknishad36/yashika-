"""
.antiflood on [limit] [mute_minutes]
.antiflood off
.antiflood status
"""
import time
from collections import defaultdict, deque

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]
# chat_id -> deque of timestamps
_MSG_TIMES: dict[int, dict[int, deque]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=30)))


@app.on_message(filters.command("antiflood", prefixes=PREFIXES) & filters.group)
@sudo_only
async def antiflood_cmd(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await get_chat_flag(chat_id, "antiflood", False)
        lim = await get_chat_flag(chat_id, "antiflood_limit", 5)
        mute_m = await get_chat_flag(chat_id, "antiflood_mute", 60)
        await message.reply_text(
            f"🛡 <b>AntiFlood</b>\n"
            f"Status: <b>{'ON' if on else 'OFF'}</b>\n"
            f"Limit: <code>{lim}</code> msgs / 10s\n"
            f"Mute: <code>{mute_m}</code> min\n\n"
            f"<code>.antiflood on 5 60</code>\n"
            f"<code>.antiflood off</code>"
        )
        return

    arg = message.command[1].lower()
    if arg in ("off", "0", "disable"):
        await set_chat_flag(chat_id, "antiflood", False)
        await message.reply_text("❌ AntiFlood OFF")
        return

    if arg in ("on", "1", "enable"):
        limit = int(message.command[2]) if len(message.command) > 2 else 5
        mute_m = int(message.command[3]) if len(message.command) > 3 else 60
        await set_chat_flag(chat_id, "antiflood", True)
        await set_chat_flag(chat_id, "antiflood_limit", max(3, limit))
        await set_chat_flag(chat_id, "antiflood_mute", max(1, mute_m))
        await message.reply_text(
            f"✅ AntiFlood ON\nLimit: <code>{limit}</code>/10s\nMute: <code>{mute_m}</code> min"
        )
        return

    await message.reply_text("Usage: <code>.antiflood on|off</code>")


@app.on_message(filters.group & filters.incoming & ~filters.service & \~filters.me, group=8)
async def antiflood_watch(client, message: Message):
    if not message.from_user:
        return
    chat_id = message.chat.id
    if not await get_chat_flag(chat_id, "antiflood", False):
        return

    uid = message.from_user.id
    now = time.time()
    q = _MSG_TIMES[chat_id][uid]
    q.append(now)
    window = [t for t in q if now - t <= 10]
    _MSG_TIMES[chat_id][uid] = deque(window, maxlen=30)

    limit = int(await get_chat_flag(chat_id, "antiflood_limit", 5) or 5)
    if len(window) < limit:
        return

    mute_m = int(await get_chat_flag(chat_id, "antiflood_mute", 60) or 60)
    try:
        until = int(now + mute_m * 60)
        await client.restrict_chat_member(
            chat_id,
            uid,
            permissions=None,  # filled below
            until_date=until,
        )
    except Exception:
        try:
            from pyrogram.types import ChatPermissions
            await client.restrict_chat_member(
                chat_id,
                uid,
                ChatPermissions(can_send_messages=False),
                until_date=int(now + mute_m * 60),
            )
            await message.reply_text(
                f"🛡 Flood: {message.from_user.mention} muted <b>{mute_m}</b> min"
            )
        except Exception:
            pass
    _MSG_TIMES[chat_id][uid].clear()
