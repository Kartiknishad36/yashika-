"""
Yashika Music resolver

1) If BASE_URL + API_KEY set → external stream API (fast, no full download)
2) Else yt-dlp + cookies.txt

Env:
  BASE_URL=https://your-api.example.com
  API_KEY=your_key
  COOKIES_PATH=cookies.txt
"""
import os
import asyncio
import hashlib

import aiohttp
from yt_dlp import YoutubeDL

try:
    from youtubesearchpython.__future__ import VideosSearch
except Exception:
    VideosSearch = None

try:
    from config import COOKIES_PATH, BASE_URL, API_KEY
except ImportError:
    COOKIES_PATH = os.environ.get("COOKIES_PATH", "cookies.txt")
    BASE_URL = os.environ.get("BASE_URL", "")
    API_KEY = os.environ.get("API_KEY", "")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _cookies_file() -> str | None:
    path = COOKIES_PATH or "cookies.txt"
    if path and os.path.isfile(path):
        return path
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for p in ("cookies.txt", os.path.join(root, "cookies.txt")):
        if os.path.isfile(p):
            return p
    return None


async def _api_result(query: str, video: bool = False) -> dict | None:
    """Fast path via BASE_URL API — same idea as common music APIs."""
    base = (BASE_URL or "").rstrip("/")
    key = API_KEY or ""
    if not base or not key:
        return None

    endpoints = [
        f"{base}/song",
        f"{base}/yt",
        f"{base}/search",
        f"{base}/api/song",
    ]
    params_list = [
        {"query": query, "api_key": key},
        {"q": query, "key": key},
        {"query": query, "api": key},
        {"song": query, "api_key": key},
    ]

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for url in endpoints:
            for params in params_list:
                try:
                    async with session.get(url, params=params) as resp:
                        if resp.status != 200:
                            continue
                        data = await resp.json(content_type=None)
                        if not isinstance(data, dict):
                            continue
                        # unwrap common shapes
                        for key_name in ("result", "data", "results", "song"):
                            if isinstance(data.get(key_name), dict):
                                data = data[key_name]
                                break
                            if isinstance(data.get(key_name), list) and data[key_name]:
                                data = data[key_name][0]
                                break

                        stream = (
                            data.get("stream_url")
                            or data.get("audio")
                            or data.get("url")
                            or data.get("link")
                            or data.get("download_url")
                        )
                        if video:
                            stream = (
                                data.get("video_url")
                                or data.get("video")
                                or stream
                            )
                        title = data.get("title") or data.get("name") or query
                        thumb = data.get("thumbnail") or data.get("thumb") or ""
                        if stream and isinstance(stream, str) and stream.startswith("http"):
                            print(f"[music-api] OK: {title}")
                            return {
                                "title": title,
                                "stream_url": stream,
                                "thumbnail": thumb,
                                "video": video,
                            }
                except Exception as e:
                    print(f"[music-api] {url} fail: {e}")
                    continue
    return None


async def _search_video_id(query: str) -> tuple[str, str, str]:
    if VideosSearch is None:
        raise ValueError("youtube-search-python not installed")
    search = VideosSearch(query, limit=1)
    result = await search.next()
    if not result.get("result"):
        raise ValueError(f"No results: {query}")
    item = result["result"][0]
    return item["id"], item.get("title", query), (item.get("thumbnails") or [{}])[-1].get("url", "")


def _ydl_opts(want_video: bool, outtmpl: str) -> dict:
    opts = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "retries": 3,
        "fragment_retries": 3,
        "extractor_args": {"youtube": {"player_client": ["android", "ios"]}},
    }
    cookies = _cookies_file()
    if cookies:
        opts["cookiefile"] = cookies
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
        if name.startswith(prefix) and os.path.getsize(os.path.join(DOWNLOAD_DIR, name)) > 0:
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
    raise RuntimeError("Download failed — check cookies.txt + ffmpeg")


async def _download_url(url: str, want_video: bool) -> tuple[str, str]:
    key = hashlib.md5(url.encode()).hexdigest()[:12]
    ext_hint = "mp4" if want_video else "mp3"
    cached = os.path.join(DOWNLOAD_DIR, f"{key}.{ext_hint}")
    if os.path.exists(cached) and os.path.getsize(cached) > 0:
        return url, cached
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
    raise RuntimeError("URL download failed")


def _is_youtube_url(q: str) -> bool:
    q = q.lower()
    return "youtube.com" in q or "youtu.be" in q


async def get_result(query: str, video: bool = False) -> dict:
    query = (query or "").strip()
    if not query:
        raise ValueError("Empty query")

    # 1) Fast API
    api = await _api_result(query, video=video)
    if api:
        return api

    # 2) yt-dlp
    if _is_youtube_url(query):
        title, path = await _download_url(query, video)
        return {"title": title, "stream_url": path, "thumbnail": "", "video": video}

    vidid, title, thumb = await _search_video_id(query)
    path = await _download_id(vidid, video)
    return {"title": title, "stream_url": path, "thumbnail": thumb, "video": video}
