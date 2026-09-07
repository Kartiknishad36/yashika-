import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv(".env")

# ===================== Telegram Core =====================
API_ID = int(os.environ.get("API_ID", 0) or 0)
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")
ASSISTANT_SESSION = os.environ.get("ASSISTANT_SESSION", "")

# ===================== Owner =====================
OWNER_ID = int(os.environ.get("OWNER_ID", 0) or 0)
LOG_GROUP_ID = (
    int(os.environ["LOG_GROUP_ID"])
    if os.environ.get("LOG_GROUP_ID")
    else None
)

# ===================== Music (yt-dlp + cookies) =====================
COOKIES_PATH = os.environ.get("COOKIES_PATH", "cookies.txt")
# Optional legacy (sirf purane API streams ke liye)
BASE_URL = os.environ.get("BASE_URL", "")
API_KEY = os.environ.get("API_KEY", "")

# ===================== AI (Gemini chatbot) =====================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

# ===================== Bot identity / UI =====================
BOT_NAME = os.environ.get("BOT_NAME", "Yashika")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "").lstrip("@")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "").lstrip("@")
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "https://t.me/YourSupport")
UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/YourUpdates")

# Start / ping images (local path or https URL)
START_PIC = os.environ.get("START_PIC", "assets/start.jpg")
PING_PIC = os.environ.get("PING_PIC", "assets/ping.jpg")

# Command prefixes for userbot-style cmds (app client)
PREFIXES = list(os.environ.get("PREFIXES", ".!"))
