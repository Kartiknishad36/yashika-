from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

@app.on_message(filters.command("paste", prefixes=PREFIXES))
@sudo_only
async def paste_cmd(client, message: Message):
    text = None
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        text = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    if not text:
        return await message.reply_text("Reply text / `·paste hello`")
    await message.reply_text(f"📋 **Paste**\n<code>{text[:3500]}</code>")
