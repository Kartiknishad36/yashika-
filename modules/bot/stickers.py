"""
Member sticker bheje → same pack se random sticker wapas.
Group: adult packs skip (blacklist).
DM: koi bhi pack OK.
"""
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

from core.clients import bot

if bot is None:
    raise RuntimeError("stickers needs BOT_TOKEN")

# Group mein in words wale packs skip
_ADULT_WORDS = (
    "nsfw", "adult", "porn", "xxx", "sex", "hentai", "18+", "nude",
    "boob", "pussy", "dick", "cum", "onlyfans", "erotic", "lewd",
)

# Romantic / safe-ish hints (optional boost — still same pack)
_ROMANTIC_WORDS = (
    "love", "kiss", "romantic", "heart", "couple", "cute", "hug", "date",
)


def _is_adult_pack(title: str, short_name: str) -> bool:
    blob = f"{title or ''} {short_name or ''}".lower()
    return any(w in blob for w in _ADULT_WORDS)


@bot.on_message(filters.sticker & filters.incoming, group=35)
async def sticker_echo(client, message: Message):
    if not message.sticker or not message.from_user:
        return
    if message.from_user.is_bot:
        return

    st = message.sticker
    set_name = st.set_name
    if not set_name:
        return  # not from a pack

    is_private = message.chat.type == ChatType.PRIVATE

    try:
        sset = await client.get_sticker_set(set_name)
    except Exception:
        return

    title = getattr(sset, "title", "") or ""
    if not is_private and _is_adult_pack(title, set_name):
        # group: adult pack — ignore (no reply)
        return

    stickers = list(getattr(sset, "stickers", []) or [])
    if not stickers:
        return

    pick = random.choice(stickers)
    try:
        await message.reply_sticker(pick.file_id)
    except Exception:
        pass
