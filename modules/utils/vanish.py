import asyncio
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!"]

@app.on_message(filters.command("vanish", prefixes=PREFIXES))
@sudo_only
async def vanish_cmd(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("vanish_mode", False)
        return await message.reply_text(
            f"💨 Vanish: **{'ON' if on else 'OFF'}**\n"
            f"`·vanish on|off`\n`·vanish 5s text`"
        )
    arg = message.command[1].lower()
    if arg in ("on", "off"):
        await set_feature("vanish_mode", arg == "on")
        return await message.reply_text(f"Vanish {arg.upper()}")
    if arg.endswith("s") and arg[:-1].isdigit():
        sec = max(1, min(int(arg[:-1]), 60))
        text = message.text.split(None, 2)[2] if len(message.command) > 2 else "•"
        msg = await message.reply_text(text)
        await asyncio.sleep(sec)
        try:
            await msg.delete()
            await message.delete()
        except Exception:
            pass
        return
    await message.reply_text("Usage: on/off / `·vanish 5s hi`")

@app.on_message(filters.me, group=3)
async def vanish_auto(client, message: Message):
    if not await get_feature("vanish_mode", False):
        return
    if message.text and message.text.startswith((".", "!", "/")):
        return
    await asyncio.sleep(8)
    try:
        await message.delete()
    except Exception:
        pass
