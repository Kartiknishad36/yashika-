from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

@app.on_message(filters.command("fakelocation", prefixes=PREFIXES))
@sudo_only
async def fakeloc_cmd(client, message: Message):
    place = message.text.split(None, 1)[1] if len(message.command) > 1 else "Unknown"
    await message.reply_text(
        f"📍 **Location card** (fun only)\n"
        f"Place: **{place}**\n"
        f"<i>Real GPS spoof nahi — text card.</i>"
    )
