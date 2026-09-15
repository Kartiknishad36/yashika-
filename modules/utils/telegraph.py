import os, mimetypes
import aiohttp
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
TG_ON = True
OUT = "downloads"
os.makedirs(OUT, exist_ok=True)

async def _upload_file(path: str) -> str:
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    data = aiohttp.FormData()
    data.add_field("file", open(path, "rb"), filename=os.path.basename(path), content_type=mime)
    async with aiohttp.ClientSession() as session:
        async with session.post("https://telegra.ph/upload", data=data, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            js = await resp.json()
    if isinstance(js, list) and js and "src" in js[0]:
        return "https://telegra.ph" + js[0]["src"]
    raise RuntimeError(str(js)[:200])

@app.on_message(filters.command("tgmode", prefixes=PREFIXES))
@sudo_only
async def tgmode_cmd(client, message: Message):
    global TG_ON
    if len(message.command) < 2:
        return await message.reply_text(f"TG: **{'ON' if TG_ON else 'OFF'}**")
    TG_ON = message.command[1].lower() in ("on", "1")
    await message.reply_text(f"Telegraph {'ON' if TG_ON else 'OFF'}")

@app.on_message(filters.command(["tg", "telegraph", "tgraph"], prefixes=PREFIXES))
@sudo_only
async def telegraph_cmd(client, message: Message):
    if not TG_ON:
        return await message.reply_text("`·tgmode on`")
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply_text("Reply photo + `·tg`")
    status = await message.reply_text("☁️ Uploading…")
    path = None
    try:
        path = await client.download_media(message.reply_to_message, file_name=OUT + "/")
        url = await _upload_file(path)
        await status.edit_text(f"✅ {url}")
    except Exception as e:
        await status.edit_text(f"❌ `{e}`")
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
