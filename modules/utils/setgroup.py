"""
.setgrouppic  (reply photo)
.setgrouptitle <name>
.setgroupdesc <text>
"""
import os
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
OUT = "downloads"
os.makedirs(OUT, exist_ok=True)


@app.on_message(filters.command(["setgrouppic", "setgpic"], prefixes=PREFIXES) & filters.group)
@sudo_only
async def setgpic(client, message: Message):
    r = message.reply_to_message
    if not r or not (r.photo or r.document):
        await message.reply_text("Photo pe reply + <code>.setgrouppic</code>")
        return
    path = None
    try:
        path = await client.download_media(r, file_name=OUT + "/")
        await client.set_chat_photo(message.chat.id, photo=path)
        await message.reply_text("✅ Group photo updated")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


@app.on_message(filters.command(["setgrouptitle", "setgtitle"], prefixes=PREFIXES) & filters.group)
@sudo_only
async def setgtitle(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.setgrouptitle New Name</code>")
        return
    title = message.text.split(None, 1)[1][:128]
    try:
        await client.set_chat_title(message.chat.id, title)
        await message.reply_text(f"✅ Title: <b>{title}</b>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command(["setgroupdesc", "setgdesc"], prefixes=PREFIXES) & filters.group)
@sudo_only
async def setgdesc(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.setgroupdesc About...</code>")
        return
    desc = message.text.split(None, 1)[1][:255]
    try:
        await client.set_chat_description(message.chat.id, desc)
        await message.reply_text("✅ Description updated")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
