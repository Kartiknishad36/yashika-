"""
.slowmode 10
.slowmode off
"""
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


@app.on_message(filters.command("slowmode", prefixes=PREFIXES) & filters.group)
@sudo_only
async def slowmode_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n<code>.slowmode 10</code> (seconds)\n<code>.slowmode off</code>"
        )
        return
    arg = message.command[1].lower()
    if arg in ("off", "0", "disable"):
        try:
            await client.set_slow_mode(message.chat.id, None)
            await message.reply_text("✅ Slowmode OFF")
        except Exception as e:
            await message.reply_text(f"❌ <code>{e}</code>")
        return
    try:
        sec = int(arg)
        sec = max(0, min(sec, 21600))
        await client.set_slow_mode(message.chat.id, sec)
        await message.reply_text(f"🐢 Slowmode: <b>{sec}s</b>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
