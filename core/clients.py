import sys
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, STRING_SESSION

if not STRING_SESSION:
    print("[FATAL] STRING_SESSION missing in .env — userbot cannot start.")
    sys.exit(1)

# Single client: commands + VC + music
app = Client(
    name="userbot-session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    parse_mode=ParseMode.HTML,
    in_memory=True,
    workers=8,
    sleep_threshold=120,
    max_concurrent_transmissions=2,
)

assistant = None
call_client = app
bot = None
