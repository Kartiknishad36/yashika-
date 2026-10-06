"""bot = BotFather token | app = userbot STRING_SESSION (optional)."""
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, STRING_SESSION, BOT_TOKEN

bot = None
if BOT_TOKEN and API_ID and API_HASH:
    bot = Client(
        name="yashika_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        in_memory=True,
        parse_mode=ParseMode.HTML,
        workers=4,
        sleep_threshold=60,
    )

app = None
if STRING_SESSION and API_ID and API_HASH:
    app = Client(
        name="yashika_ub",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        in_memory=True,
        parse_mode=ParseMode.HTML,
        workers=4,
        sleep_threshold=60,
        max_concurrent_transmissions=2,
    )

# aliases used by older modules
assistant = bot
call_client = app
