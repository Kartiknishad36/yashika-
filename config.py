import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv(".env")

# ===================== Telegram Core =====================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")
ASSISTANT_SESSION = os.environ.get("ASSISTANT_SESSION", "")

# ===================== Owner =====================
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
LOG_GROUP_ID = (
    int(os.environ.get("LOG_GROUP_ID", 0))
    if os.environ.get("LOG_GROUP_ID")
    else None
)

# ===================== Music (yt-dlp + cookies) =====================
# Netscape cookies file for YouTube (project root by default)
COOKIES_PATH = os.environ.get("COOKIES_PATH", "cookies.txt")

# Optional legacy API keys (unused if streams.py is cookies-based)
BASE_URL = os.environ.get("BASE_URL", "")
API_KEY = os.environ.get("API_KEY", "")

# ===================== Misc =====================
BOT_NAME = os.environ.get("BOT_NAME", "MyUB")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
PREFIXES = list(os.environ.get("PREFIXES", ".!"))

# ===================== Bot public links (Baka-style UI) =====================
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "https://t.me/YourSupport")
UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/YourUpdates")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "")  # without @
