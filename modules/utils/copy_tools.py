from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

@app.on_message(filters.command(["copycap", "hideforward", "copy"], prefixes=PREFIXES))
@sudo_only
async def copycap_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        return await message.reply_text("Reply media/text + `·copycap`")
    try:
        await r.copy(message.chat.id)
        try:
            await message.delete()
        except Exception:
            pass
    except Exception as e:
        if r.caption:
            await message.reply_text(r.caption)
        else:
            await message.reply_text(f"❌ `{e}`")
