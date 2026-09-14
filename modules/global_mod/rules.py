"""
.setrules <text>
.rules
.clearrules
"""
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]


@app.on_message(filters.command("setrules", prefixes=PREFIXES) & filters.group)
@sudo_only
async def setrules_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.setrules No spam | Be respectful</code>")
        return
    text = message.text.split(None, 1)[1][:3500]
    await set_chat_flag(message.chat.id, "rules_text", text)
    await message.reply_text("✅ Rules saved.")


@app.on_message(filters.command("rules", prefixes=PREFIXES) & filters.group)
async def rules_cmd(client, message: Message):
    text = await get_chat_flag(message.chat.id, "rules_text", None)
    if not text:
        await message.reply_text("Rules set nahi — admin <code>.setrules</code> kare.")
        return
    await message.reply_text(f"📜 <b>Group Rules</b>\n\n{text}")


@app.on_message(filters.command("clearrules", prefixes=PREFIXES) & filters.group)
@sudo_only
async def clearrules_cmd(client, message: Message):
    await set_chat_flag(message.chat.id, "rules_text", "")
    await message.reply_text("✅ Rules cleared.")
