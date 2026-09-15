from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

@app.on_message(filters.command("captiongen", prefixes=PREFIXES))
@sudo_only
async def captiongen_cmd(client, message: Message):
    topic = message.text.split(None, 1)[1][:80] if len(message.command) > 1 else "moment"
    caps = [
        f"✨ {topic} | pure vibes",
        f"📌 {topic} — saved for later",
        f"💫 Living for {topic}",
    ]
    await message.reply_text("📝 **Captions**\n\n" + "\n\n".join(caps))

@app.on_message(filters.command("secretlink", prefixes=PREFIXES))
@sudo_only
async def secretlink_cmd(client, message: Message):
    if len(message.command) < 2 or "|" not in message.text:
        return await message.reply_text("`·secretlink Click Here | https://t.me/x`")
    raw = message.text.split(None, 1)[1]
    label, url = raw.split("|", 1)
    await message.reply_text(
        f'<a href="{url.strip()}">{label.strip()}</a>',
        disable_web_page_preview=True,
    )
