import os
from dotenv import load_dotenv

load_dotenv()


def _str(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


def _int(key: str, default: int = 0) -> int:
    try:
        return int(os.getenv(key) or default)
    except (TypeError, ValueError):
        return default


def _bool(key: str, default: bool = False) -> bool:
    v = (os.getenv(key) or "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


API_ID = _int("API_ID", 0)
API_HASH = _str("API_HASH", "")
STRING_SESSION = _str("STRING_SESSION", "")
BOT_TOKEN = _str("BOT_TOKEN", "")
OWNER_ID = _int("OWNER_ID", 0)

MONGO_URI = _str("MONGO_URI", "") or _str("MONGODB_URI", "")
MONGO_DB = _str("MONGO_DB", "yashika")

_log = _str("LOG_GROUP_ID", "")
LOG_GROUP_ID = int(_log) if _log.lstrip("-").isdigit() else 0

BOT_NAME = _str("BOT_NAME", "Yashika")
BOT_USERNAME = _str("BOT_USERNAME", "").lstrip("@")
OWNER_USERNAME = _str("OWNER_USERNAME", "").lstrip("@")
SUPPORT_CHAT = _str("SUPPORT_CHAT", "")
UPDATE_CHANNEL = _str("UPDATE_CHANNEL", "")
PREFIXES = _str("PREFIXES", ".!")

AUTO_DELETE = _bool("AUTO_DELETE", True)
try:
    DELETE_DELAY = float(os.getenv("DELETE_DELAY") or "1.5")
except ValueError:
    DELETE_DELAY = 1.5

BASE_URL = _str("BASE_URL", "")
API_KEY = _str("API_KEY", "")
COOKIES_PATH = _str("COOKIES_PATH", "cookies.txt")
NUMLOOKUP_API_KEY = _str("NUMLOOKUP_API_KEY", "")
START_PIC = _str("START_PIC", "")
PING_PIC = _str("PING_PIC", "")
