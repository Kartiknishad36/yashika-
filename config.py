import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv(".env")


def _int(name: str, default: int = 0) -> int:
    """Empty / invalid env → default, no crash."""
    val = os.environ.get(name, "")
    if val is None or str(val).strip() == "":
        return default
    try:
        return int(str(val).strip())
    except (TypeError, ValueError):
        return default


def _str(name: str, default: str = "") -> str:
    val = os.environ.get(name, default)
    if val is None:
        return default
    return str(val).strip()


# ===================== Telegram Core =====================
API_ID = _int("API_ID", 0)
API_HASH = _str("API_HASH", "")
BOT_TOKEN = _str("BOT_TOKEN", "")
STRING_SESSION = _str("STRING_SESSION", "")
ASSISTANT_SESSION = _str("ASSISTANT_SESSION", "")

# Optional: assistant numeric id (manual invite / logs). 0 = unused
ASSISTANT_ID = _int("ASSISTANT_ID", 0)

# ===================== Owner =====================
OWNER_ID = _int("OWNER_ID", 0)
_log = _str("LOG_GROUP_ID", "")
LOG_GROUP_ID = int(_log) if _log.lstrip("-").isdigit() else None

# ===================== Music (yt-dlp + cookies) =====================
COOKIES_PATH = _str("COOKIES_PATH", "cookies.txt")
BASE_URL = _str("BASE_URL", "")
API_KEY = _str("API_KEY", "")

# ===================== AI (Gemini chatbot) =====================
GEMINI_API_KEY = _str("GEMINI_API_KEY", "")
# 2.5-flash = fast & usually available; override in .env if needed
GEMINI_MODEL = _str("GEMINI_MODEL", "gemini-3.6-flash")

# ===================== Bot identity / UI =====================
BOT_NAME = _str("BOT_NAME", "Yashika")
BOT_USERNAME = _str("BOT_USERNAME", "").lstrip("@")
OWNER_USERNAME = _str("OWNER_USERNAME", "").lstrip("@")
SUPPORT_CHAT = _str("SUPPORT_CHAT", "https://t.me/YourSupport")
UPDATE_CHANNEL = _str("UPDATE_CHANNEL", "https://t.me/YourUpdates")

START_PIC = _str("START_PIC", "assets/start.jpg")
PING_PIC = _str("PING_PIC", "assets/ping.jpg")

# Userbot command prefixes (string ".!" → list ['.', '!'])
_pref = _str("PREFIXES", ".!")
PREFIXES = list(_pref) if _pref else [".", "!"]
