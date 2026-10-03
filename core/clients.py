import sys
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, STRING_SESSION, ASSISTANT_SESSION

if not STRING_SESSION:
    print("[FATAL] STRING_SESSION missing in .env — userbot cannot start.")
    sys.exit(1)

# Main userbot client (personal account — all commands run here)
app = Client(
    name="userbot-session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    parse_mode=ParseMode.HTML,
    in_memory=True,
)

# Optional assistant (2nd account for VC — avoids tying main account to every call)
assistant = None
if ASSISTANT_SESSION:
    assistant = Client(
        name="userbot-assistant",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=ASSISTANT_SESSION,
        in_memory=True,
    )

# Client used by PyTgCalls for voice chats
call_client = assistant if assistant else app

# Back-compat: some old modules may still import `bot` — always None (pure userbot)
bot = None
