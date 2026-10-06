import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv(".env")


def _int(name: str, default: int = 0) -> int:
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


# Telegram userbot
API_ID = _int("API_ID", 0)
API_HASH = _str("API_HASH", "")
STRING_SESSION = _str("STRING_SESSION", "")

# Legacy (ignored — no separate assistant)
ASSISTANT_SESSION = ""
ASSISTANT_ID = 0
BOT_TOKEN = _str("BOT_TOKEN", "")

OWNER_ID = _int("OWNER_ID", 0)
_log = _str("LOG_GROUP_ID", "")
LOG_GROUP_ID = int(_log) if _log.lstrip("-").isdigit() else None

# Music API (Yashika) + yt-dlp fallback
COOKIES_PATH = _str("COOKIES_PATH", "cookies.txt")
BASE_URL = _str("BASE_URL", "")
API_KEY = _str("API_KEY", "")

# Optional number lookup (apilayer / numverify style)
NUMLOOKUP_API_KEY = _str("NUMLOOKUP_API_KEY", "")

# Branding
BOT_NAME = _str("BOT_NAME", "Yashika")
BOT_USERNAME = _str("BOT_USERNAME", "").lstrip("@")
OWNER_USERNAME = _str("OWNER_USERNAME", "KARTIK_NISHAD_3").lstrip("@")
SUPPORT_CHAT = _str("SUPPORT_CHAT", "https://t.me/+Ml99kT7JCMo0OTdl")
UPDATE_CHANNEL = _str("UPDATE_CHANNEL", "https://t.me/ye_duniya_ek_sapna_he")

START_PIC = _str("START_PIC", "")
PING_PIC = _str("PING_PIC", "")

_pref = _str("PREFIXES", ".!")
PREFIXES = list(_pref) if _pref else [".", "!"]
