"""
YouTube audio/video via yt-dlp + cookies.txt (no external music API).

Flow:
  query → YouTube search (or direct link) → yt-dlp download with cookies → local file

Put cookies.txt in project root, or set COOKIES_PATH in .env.
ffmpeg must be installed on the server for audio extract.
"""
import os
import asyncio
import hashlib
from yt_dlp import YoutubeDL
from youtubesearchpython.__future__ import VideosSearch

try:
    from config import COOKIES_PATH
except ImportError:
    COOKIES_PATH = os.environ.get("COOKIES_PATH", "cookies.txt")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _cookies_file() -> str | None:
    path = COOKIES_PATH or "cookies.txt"
    if path and os.path.isfile(path):
        return path
    alt = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "cookies.txt",
    )
    if os.path.isfile(alt):
        return alt
    # project root (one more level up from modules/)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    alt2 = os.path.join(root, "cookies.txt")
    if os.path.isfile(alt2):
        return alt2
    return None


async def _search_video_id(query: str) -> tuple[str, str, str]:
    """Returns (video_id, title, thumbnail)."""
    search = VideosSearch(query, limit=1)
    result = await search.next()
    if not result.get("result"):
        raise ValueError(f"No results found for query: {query}")
    item = result["result"][0]
    vidid = item["id"]
    title = item.get("title", query)
    thumbs = item.get("thumbnails") or []
    thumb = thumbs[-1]["url"] if thumbs else ""
    return vidid, title, thumb


def _ydl_opts(want_video: bool, outtmpl: str) -> dict:
    opts = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "retries": 5,
        "fragment_retries": 5,
        "skip_unavailable_fragments": True,
        # Fix: "The page needs to be reloaded"
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "web"],
            }
        },
    }
    cookies = _cookies_file()
    if cookies:
        opts["cookiefile"] = cookies
        print(f"[yt-dlp] Using cookies: {cookies}")
    else:
        print("[yt-dlp] WARNING: no cookies.txt found")

    if want_video:
        opts["format"] = "best[height<=480]/bestaudio/best"
    else:
        opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    return opts


def _find_output(prefix: str) -> str | None:
    if not os.path.isdir(DOWNLOAD_DIR):
        return None
    for name in os.listdir(DOWNLOAD_DIR):
        if name.startswith(prefix) and os.path.getsize(
            os.path.join(DOWNLOAD_DIR, name)
        ) > 0:
            return os.path.join(DOWNLOAD_DIR, name)
    return None


async def _download_id(vidid: str, want_video: bool) -> str:
    ext_hint = "mp4" if want_video else "mp3"
    cached = os.path.join(DOWNLOAD_DIR, f"{vidid}.{ext_hint}")
    if os.path.exists(cached) and os.path.getsize(cached) > 0:
        return cached

    found = _find_output(vidid)
    if found:
        return found

    url = f"https://www.youtube.com/watch?v={vidid}"
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{vidid}.%(ext)s")
    opts = _ydl_opts(want_video, outtmpl)

    def _run():
        with YoutubeDL(opts) as ydl:
            ydl.download([url])

    await asyncio.to_thread(_run)

    if os.path.exists(cached) and os.path.getsize(cached) > 0:
        return cached
    found = _find_output(vidid)
    if found:
        return found
    raise RuntimeError(
        "Download failed. Check cookies.txt is valid and ffmpeg is installed."
    )


async def _download_url(url: str, want_video: bool) -> tuple[str, str]:
    """Returns (title, file_path)."""
    key = hashlib.md5(url.encode()).hexdigest()[:12]
    ext_hint = "mp4" if want_video else "mp3"
    cached = os.path.join(DOWNLOAD_DIR, f"{key}.{ext_hint}")
    if os.path.exists(cached) and os.path.getsize(cached) > 0:
        return url, cached

    found = _find_output(key)
    if found:
        return url, found

    outtmpl = os.path.join(DOWNLOAD_DIR, f"{key}.%(ext)s")
    opts = _ydl_opts(want_video, outtmpl)
    title = url

    def _run():
        nonlocal title
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info:
                title = info.get("title") or url

    await asyncio.to_thread(_run)

    if os.path.exists(cached) and os.path.getsize(cached) > 0:
        return title, cached
    found = _find_output(key)
    if found:
        return title, found
    raise RuntimeError("URL download failed. Check cookies.txt / ffmpeg.")


def _is_youtube_url(q: str) -> bool:
    q = q.lower()
    return "youtube.com" in q or "youtu.be" in q


async def get_result(query: str, video: bool = False) -> dict:
    """
    Main entry. Returns:
      {title, stream_url, thumbnail, video}
    stream_url = local file path (MediaStream accepts local paths).
    """
    query = (query or "").strip()
    if not query:
        raise ValueError("Empty query")

    if _is_youtube_url(query):
        title, path = await _download_url(query, video)
        print(f"[yt-dlp] Ready: {title} -> {path}")
        return {
            "title": title,
            "stream_url": path,
            "thumbnail": "",
            "video": video,
        }

    vidid, title, thumb = await _search_video_id(query)
    path = await _download_id(vidid, video)
    print(f"[yt-dlp] Ready: {title} -> {path}")
    return {
        "title": title,
        "stream_url": path,
        "thumbnail": thumb,
        "video": video,
  }
