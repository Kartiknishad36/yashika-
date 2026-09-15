from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

@app.on_message(filters.command(["hashtaggen", "hashtag", "tags"], prefixes=PREFIXES))
@sudo_only
async def hashtag_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("`·hashtaggen love`")
    w = message.command[1].strip().lstrip("#")
    tags = [
        f"#{w}", f"#{w}vibes", f"#{w}life", f"#{w}mood", f"#{w}daily",
        f"#{w}goals", f"#{w}time", f"#{w}story", f"#viral{w}", f"#{w}india",
    ]
    await message.reply_text("🏷 **Hashtags**\n\n" + " ".join(tags))
