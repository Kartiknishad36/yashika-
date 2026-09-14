"""
.setname .setbio .setpfp .delpfp .block .unblock
"""
import os

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
OUT = "downloads"
os.makedirs(OUT, exist_ok=True)


@app.on_message(filters.command("setname", prefixes=PREFIXES))
@sudo_only
async def setname_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.setname First | Last</code>")
        return
    raw = message.text.split(None, 1)[1]
    if "|" in raw:
        first, last = raw.split("|", 1)
    else:
        parts = raw.split(None, 1)
        first, last = parts[0], (parts[1] if len(parts) > 1 else "")
    try:
        await client.update_profile(first_name=first.strip()[:64], last_name=last.strip()[:64])
        await message.reply_text(f"✅ Name: <b>{first.strip()} {last.strip()}</b>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command("setbio", prefixes=PREFIXES))
@sudo_only
async def setbio_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.setbio your bio</code>")
        return
    bio = message.text.split(None, 1)[1][:70]
    try:
        await client.update_profile(bio=bio)
        await message.reply_text(f"✅ Bio:\n<code>{bio}</code>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command("setpfp", prefixes=PREFIXES))
@sudo_only
async def setpfp_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not (r.photo or r.document):
        await message.reply_text("Photo pe reply + <code>.setpfp</code>")
        return
    path = None
    try:
        path = await client.download_media(r, file_name=OUT + "/")
        await client.set_profile_photo(photo=path)
        await message.reply_text("✅ Profile photo set")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


@app.on_message(filters.command("delpfp", prefixes=PREFIXES))
@sudo_only
async def delpfp_cmd(client, message: Message):
    try:
        photos = []
        async for p in client.get_chat_photos("me", limit=1):
            photos.append(p.file_id)
        if not photos:
            await message.reply_text("Koi DP nahi.")
            return
        await client.delete_profile_photos(photos[0])
        await message.reply_text("✅ Latest DP deleted")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command("block", prefixes=PREFIXES))
@sudo_only
async def block_cmd(client, message: Message):
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 1 and message.command[1].isdigit():
        uid = int(message.command[1])
    if not uid:
        await message.reply_text("Reply / ID: <code>.block</code>")
        return
    try:
        await client.block_user(uid)
        await message.reply_text(f"🚫 Blocked <code>{uid}</code>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command("unblock", prefixes=PREFIXES))
@sudo_only
async def unblock_cmd(client, message: Message):
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 1 and message.command[1].isdigit():
        uid = int(message.command[1])
    if not uid:
        await message.reply_text("Reply / ID: <code>.unblock</code>")
        return
    try:
        await client.unblock_user(uid)
        await message.reply_text(f"✅ Unblocked <code>{uid}</code>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
