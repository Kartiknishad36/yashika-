"""
.qr <text>
"""
import os
import io

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
OUT = "downloads"
os.makedirs(OUT, exist_ok=True)


@app.on_message(filters.command(["qr", "qrcode"], prefixes=PREFIXES))
@sudo_only
async def qr_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.qr https://t.me/...</code>")
        return
    text = message.text.split(None, 1)[1][:500]
    try:
        import qrcode
        img = qrcode.make(text)
        path = os.path.join(OUT, "qr.png")
        img.save(path)
        await message.reply_photo(path, caption=f"📱 QR\n<code>{text[:100]}</code>")
        os.remove(path)
    except ImportError:
        await message.reply_text("Install: <code>pip install qrcode[pil]</code>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
