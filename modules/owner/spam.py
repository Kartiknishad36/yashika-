"""
.spam <count> <text>
Reply + .spam <count>  → replied msg ka text use

Limits: max 9999999999999999999 messages, min 0.7s delay (flood protect)
Sudo / me only.
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
MAX_COUNT = 9999999999999999999
DELAY = 0.7  # seconds between msgs


@app.on_message(filters.command("spam", prefixes=PREFIXES))
@sudo_only
async def spam_cmd(client, message: Message):
    # Optional: only private + groups (not channels)
    if message.chat.type == ChatType.CHANNEL:
        await message.reply_text("❌ Channel mein spam allow nahi.")
        return

    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n"
            "`.spam 5 hello`\n"
            "Reply + `.spam 5`"
        )
        return

    try:
        count = int(message.command[1])
    except ValueError:
        await message.reply_text("Count number hona chahiye: `.spam 5 text`")
        return

    if count < 1:
        await message.reply_text("Count kam se kam 1 ho.")
        return
    if count > MAX_COUNT:
        count = MAX_COUNT
        await message.reply_text(f"⚠️ Max {MAX_COUNT} — usi limit pe chalega.")

    # text: args ke baad, ya reply
    text = ""
    if len(message.command) > 2:
        text = message.text.split(None, 2)[2]
    elif message.reply_to_message:
        text = (
            message.reply_to_message.text
            or message.reply_to_message.caption
            or ""
        )

    if not text.strip():
        await message.reply_text("Text do: `.spam 5 hello` ya reply + `.spam 5`")
        return

    try:
        await message.delete()
    except Exception:
        pass

    for i in range(count):
        try:
            await client.send_message(message.chat.id, text)
        except Exception as e:
            await client.send_message(
                message.chat.id,
                f"⏹ Spam stopped: `{e}`",
            )
            break
        if i < count - 1:
            await asyncio.sleep(DELAY)
