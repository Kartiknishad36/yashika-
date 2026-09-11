"""
YouTube / generic download (userbot):
  .ytmp3 <url|query>   — audio mp3
  .ytmp4 <url|query>   — video mp4 (max \~50MB try)
  .dl <url>            — best effort video

Uses yt-dlp + optional cookies.txt (COOKIES_PATH from config).
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
MAX_UPLOAD = 45 * 1024 * 1024  # \~45MB soft limit for TG


def _cookies():
    p = COOKIES_PATH or "cookies.txt"
    return p if os.path.exists(p) else None


def _ydl_opts(outtmpl: str, audio: bool) -> dict:
    opts = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "retries": 3,
        "extractor_args": {
            "youtube": {"player_client": ["android", "ios", "web"]}
        },
    }
    c = _cookies()
    if c:
        opts["cookiefile"] = c
    if audio:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    else:
        opts["format"] = "best[height<=720]/best"
    return opts


async def _download(query: str, audio: bool) -> tuple[str, str]:
    """Returns (file_path, title)."""
    import yt_dlp

    tmpdir = tempfile.mkdtemp(prefix="dl_")
    outtmpl = os.path.join(tmpdir, "%(title).80s.%(ext)s")

    def _run():
        opts = _ydl_opts(outtmpl, audio)
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if "entries" in info and info["entries"]:
                info = info["entries"][0]
            title = info.get("title") or "file"
            path = ydl.prepare_filename(info)
            if audio:
                base, _ = os.path.splitext(path)
                mp3 = base + ".mp3"
                if os.path.exists(mp3):
                    path = mp3
            return path, title

    return await asyncio.to_thread(_run)


@app.on_message(filters.command(["ytmp3", "song"], prefixes=PREFIXES))
@sudo_only
async def ytmp3_cmd(client, message: Message):
    q = message.text.split(None, 1)
    if len(q) < 2:
        await message.reply_text("Usage: `.ytmp3 song name or URL`")
        return
    query = q[1].strip()
    st = await message.reply_text("⏳ Downloading audio...")
    try:
        path, title = await _download(query, audio=True)
        if not os.path.exists(path):
            await st.edit_text("❌ File not found after download.")
            return
        size = os.path.getsize(path)
        if size > MAX_UPLOAD:
            await st.edit_text(f"❌ File too big ({size // 1024 // 1024}MB).")
            try:
                os.remove(path)
            except Exception:
                pass
            return
        await st.edit_text("📤 Uploading...")
        await client.send_audio(
            message.chat.id,
            path,
            title=title[:64],
            caption=f"🎵 {title}",
        )
        await st.delete()
    except Exception as e:
        await st.edit_text(f"❌ `{e}`")
    finally:
        try:
            if "path" in dir() and path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


@app.on_message(filters.command(["ytmp4", "video"], prefixes=PREFIXES))
@sudo_only
async def ytmp4_cmd(client, message: Message):
    q = message.text.split(None, 1)
    if len(q) < 2:
        await message.reply_text("Usage: `.ytmp4 name or URL`")
        return
    query = q[1].strip()
    st = await message.reply_text("⏳ Downloading video...")
    path = None
    try:
        path, title = await _download(query, audio=False)
        if not os.path.exists(path):
            await st.edit_text("❌ File not found.")
            return
        size = os.path.getsize(path)
        if size > MAX_UPLOAD:
            await st.edit_text(
                f"❌ Too big ({size // 1024 // 1024}MB). Try shorter video."
            )
            return
        await st.edit_text("📤 Uploading...")
        await client.send_video(
            message.chat.id,
            path,
            caption=f"🎬 {title}",
            supports_streaming=True,
        )
        await st.delete()
    except Exception as e:
        await st.edit_text(f"❌ `{e}`")
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


@app.on_message(filters.command(["dl"], prefixes=PREFIXES))
@sudo_only
async def dl_cmd(client, message: Message):
    """Generic URL download (video preferred)."""
    q = message.text.split(None, 1)
    if len(q) < 2:
        await message.reply_text("Usage: `.dl <url>`")
        return
    message.text = f".ytmp4 {q[1]}"  # reuse — simpler call
    await ytmp4_cmd(client, message)
