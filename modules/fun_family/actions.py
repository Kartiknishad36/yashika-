"""
/kiss /hug /slap /kick /pat /sex  — reply to user
GIF URLs public samples (replace with own if chaho)
"""
import random
from pyrogram import filters
from pyrogram.types import Message

from core.clients import bot

if bot is None:
    raise RuntimeError("modules.fun_family.actions needs BOT_TOKEN")

PREFIXES = ["/", ".", "!"]

# Public demo GIFs — apne links se replace kar sakte ho
ACTIONS = {
    "kiss": {
        "verb": "kissed",
        "emoji": "💋",
        "gifs": [
            "https://media.giphy.com/media/G3va31mwDXvIU/giphy.gif",
            "https://media.giphy.com/media/11k3oaUjJS4aA/giphy.gif",
        ],
    },
    "hug": {
        "verb": "hugged",
        "emoji": "🤗",
        "gifs": [
            "https://media.giphy.com/media/lrr9rHuoJOE0w/giphy.gif",
            "https://media.giphy.com/media/3ZnBrMqG6y1Yc/giphy.gif",
        ],
    },
    "slap": {
        "verb": "slapped",
        "emoji": "👋",
        "gifs": [
            "https://media.giphy.com/media/Zau0rrF8HwlBC/giphy.gif",
            "https://media.giphy.com/media/jLeyv1z3zqSxq/giphy.gif",
        ],
    },
    "kick": {
        "verb": "kicked",
        "emoji": "🦵",
        "gifs": [
            "https://media.giphy.com/media/u2LJ0n4T1zJZm/giphy.gif",
        ],
    },
    "pat": {
        "verb": "patted",
        "emoji": "✋",
        "gifs": [
            "https://media.giphy.com/media/5tmRHwRlwiWBc/giphy.gif",
        ],
    },
    "sex": {
        "verb": "got naughty with",
        "emoji": "🔥",
        "gifs": [
            "https://media.giphy.com/media/0Sgd09SceJAsg/giphy.gif",
        ],
    },
}


@bot.on_message(filters.command(list(ACTIONS.keys()) + ["gif"], prefixes=PREFIXES))
async def action_cmd(client, message: Message):
    cmd = message.command[0].lower().lstrip("./!")
    if cmd == "gif":
        # random any action gif
        key = random.choice(list(ACTIONS.keys()))
        data = ACTIONS[key]
        caption = f"{data['emoji']} random gif"
    else:
        data = ACTIONS[cmd]
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text(f"Reply to someone: `/{cmd}`")
            return
        a = message.from_user.mention
        b = message.reply_to_message.from_user.mention
        caption = f"{data['emoji']} {a} {data['verb']} {b}"

    gif = random.choice(data["gifs"])
    try:
        await message.reply_animation(gif, caption=caption)
    except Exception:
        await message.reply_text(caption)
