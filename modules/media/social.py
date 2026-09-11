"""
Social download (userbot):
  .insta <url>   — Instagram post/reel
  .tiktok <url>  — TikTok
  .fb <url>      — Facebook video
  .social <url>  — auto

yt-dlp + cookies optional. IG/TT often break without cookies / login.
"""
import os
import tempfile
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import COOKIES_PATH
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
MAX_UPLOAD = 45 * 1024 * 1024


def _cookies():
    p = COOKIES_PATH or "cookies.txt"
    return p if os.path.exists(p) else None


async def _dl_url(url: str) -> tuple[str, str]:
    import yt_dlp

    tmpdir = tempfile.mkdtemp(prefix="soc_")
    outtmpl = os.path.join(tmpdir, "%(id)s.%(ext)s")

    def _run():
        opts = {
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "retries": 3,
            "format": "best[height<=720]/best",
        }
        c = _cookies()
        if c:
            opts["cookiefile"] = c
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if "entries" in (info or {}) and info["entries"]:
                info = info["entries"][0]
            title = (info or {}).get("title") or "social"
            path = ydl.prepare_filename(info)
            # sometimes ext changes
            if not os.path.exists(path):
                for f in os.listdir(tmpdir):
                    fp = os.path.join(tmpdir, f)
                    if os.path.isfile(fp):
                        return fp, title
            return path, title

    return await asyncio.to_thread(_run)


async def _send_file(client, message: Message, path: str, title: str, status: Message):
    size = os.path.getsize(path)
    if size > MAX_UPLOAD:
        await status.edit_text(f"❌ Too big ({size // 1024 // 1024}MB).")
        return
    ext = os.path.splitext(path)[1].lower()
    await status.edit_text("📤 Uploading...")
    cap = f"📥 {title[:200]}"
    if ext in (".mp3", ".m4a", ".ogg", ".wav"):
        await client.send_audio(message.chat.id, path, caption=cap)
    elif ext in (".jpg", ".jpeg", ".png", ".webp"):
        await client.send_photo(message.chat.id, path, caption=cap)
    else:
        await client.send_video(
            message.chat.id, path, caption=cap, supports_streaming=True
        )
    await status.delete()


async def _handle(client, message: Message, url: str):
    st = await message.reply_text("⏳ Downloading...")
    path = None
    try:
        path, title = await _dl_url(url)
        if not path or not os.path.exists(path):
            await st.edit_text("❌ Download fail (cookies / private / site block).")
            return
        await _send_file(client, message, path, title, st)
    except Exception as e:
        await st.edit_text(
            f"❌ `{e}`\n\nTip: fresh cookies.txt / public link try karo."
        )
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


@app.on_message(filters.command(["insta", "ig"], prefixes=PREFIXES))
@sudo_only
async def insta_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("Usage: `.insta https://www.instagram.com/reel/...`")
        return
    await _handle(client, message, parts[1].strip())


@app.on_message(filters.command(["tiktok", "tt"], prefixes=PREFIXES))
@sudo_only
async def tiktok_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("Usage: `.tiktok https://www.tiktok.com/...`")
        return
    await _handle(client, message, parts[1].strip())


@app.on_message(filters.command(["fb", "facebook"], prefixes=PREFIXES))
@sudo_only
async def fb_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("Usage: `.fb https://facebook.com/...`")
        return
    await _handle(client, message, parts[1].strip())


@app.on_message(filters.command(["social"], prefixes=PREFIXES))
@sudo_only
async def social_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("Usage: `.social <url>`")
        return
    await _handle(client, message, parts[1].strip())
