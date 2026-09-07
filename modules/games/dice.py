""" Telegram built-in: /dice /dart /basket /football /bowling /slot """
from pyrogram import filters
from pyrogram.types import Message

from core.clients import bot

if bot is None:
    raise RuntimeError("modules.games.dice needs BOT_TOKEN")

PREFIXES = ["/", ".", "!"]

# emoji → command names
_GAMES = {
    "dice": "🎲",
    "dart": "🎯",
    "basket": "🏀",
    "football": "⚽",
    "bowling": "🎳",
    "slot": "🎰",
}


@bot.on_message(filters.command(list(_GAMES.keys()), prefixes=PREFIXES))
async def dice_games_cmd(client, message: Message):
    cmd = message.command[0].lower().lstrip("./!")
    emoji = _GAMES.get(cmd, "🎲")
    await message.reply_dice(emoji=emoji)
