"""
.raid <count> <text>   | reply + .raid <count>
.raid off

.spam <count> <text>   | reply + .spam <count>  (mention target on reply)
.spam off

Sudo only. Max 9999999999999999999, delay 0.6s. Cancellable.
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
MAX_COUNT = 9999999999999999999
DELAY = 0.6

# chat_id -> Task
_RAID_TASKS: dict[int, asyncio.Task] = {}
_SPAM_TASKS: dict[int, asyncio.Task] = {}


def _parse_count_text(message: Message):
    """Returns (count, text) or (None, error_str)."""
    if len(message.command) < 2:
        return None, "Usage: `.raid 10 text` | reply + `.raid 10`"

    try:
        count = int(message.command[1])
    except ValueError:
        # .raid off handled elsewhere
        return None, "Count number hona chahiye."

    if count < 1:
        return None, "Count >= 1"
    if count > MAX_COUNT:
        count = MAX_COUNT

    text = ""
    if len(message.command) > 2:
        text = message.text.split(None, 2)[2]
    elif message.reply_to_message:
        r = message.reply_to_message
        text = r.text or r.caption or ""
        # mention replied user
        if r.from_user and not text:
            text = r.from_user.mention
        elif r.from_user and text:
            text = f"{r.from_user.mention} {text}"

    if not text.strip():
        return None, "Text do ya kisi msg pe reply karke chalao."
    return count, text


async def _runner(client, chat_id: int, count: int, text: str, tag: str):
    try:
        for i in range(count):
            await client.send_message(chat_id, text)
            if i < count - 1:
                await asyncio.sleep(DELAY)
    except asyncio.CancelledError:
        try:
            await client.send_message(chat_id, f"⏹ {tag} stopped.")
        except Exception:
            pass
        raise
    except Exception as e:
        try:
            await client.send_message(chat_id, f"⏹ {tag} error: `{e}`")
        except Exception:
            pass


@app.on_message(filters.command("raid", prefixes=PREFIXES))
@sudo_only
async def raid_cmd(client, message: Message):
    chat_id = message.chat.id

    if len(message.command) >= 2 and message.command[1].lower() in (
        "off", "stop", "cancel",
    ):
        t = _RAID_TASKS.pop(chat_id, None)
        if t and not t.done():
            t.cancel()
            await message.reply_text("⏹ Raid **OFF**.")
        else:
            await message.reply_text("Koi raid nahi chal rahi.")
        return

    if chat_id in _RAID_TASKS and not _RAID_TASKS[chat_id].done():
        await message.reply_text("Raid pehle se ON. `.raid off` se band karo.")
        return

    count, text = _parse_count_text(message)
    if count is None:
        await message.reply_text(text)
        return

    try:
        await message.delete()
    except Exception:
        pass

    task = asyncio.create_task(
        _runner(client, chat_id, count, text, "Raid")
    )
    _RAID_TASKS[chat_id] = task
    await client.send_message(chat_id, f"🔥 Raid x{count} started…")


@app.on_message(filters.command("spam", prefixes=PREFIXES))
@sudo_only
async def spam_cmd(client, message: Message):
    chat_id = message.chat.id

    if len(message.command) >= 2 and message.command[1].lower() in (
        "off", "stop", "cancel",
    ):
        t = _SPAM_TASKS.pop(chat_id, None)
        if t and not t.done():
            t.cancel()
            await message.reply_text("⏹ Spam **OFF**.")
        else:
            await message.reply_text("Koi spam nahi chal raha.")
        return

    if message.chat.type == ChatType.CHANNEL:
        await message.reply_text("❌ Channel mein spam band.")
        return

    if chat_id in _SPAM_TASKS and not _SPAM_TASKS[chat_id].done():
        await message.reply_text("Spam pehle se ON. `.spam off`")
        return

    count, text = _parse_count_text(message)
    if count is None:
        await message.reply_text(text)
        return

    # reply → force mention + custom text after count
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        extra = ""
        if len(message.command) > 2:
            extra = message.text.split(None, 2)[2]
        text = f"{u.mention} {extra}".strip()

    try:
        await message.delete()
    except Exception:
        pass

    task = asyncio.create_task(
        _runner(client, chat_id, count, text, "Spam")
    )
    _SPAM_TASKS[chat_id] = task
