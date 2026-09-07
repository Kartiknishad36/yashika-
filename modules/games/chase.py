"""
/chase — join
/chasestart — start
Bot random target choose karta hai; /catch reply se catch
"""
import random
from pyrogram import filters
from pyrogram.types import Message

from core.clients import bot

if bot is None:
    raise RuntimeError("modules.games.chase needs BOT_TOKEN")

PREFIXES = ["/", ".", "!"]

# chat_id -> {players: set, names: dict, target: int|None, running: bool}
_CHASE: dict[int, dict] = {}


@bot.on_message(filters.command("chase", prefixes=PREFIXES) & filters.group)
async def chase_join(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user
    if not user:
        return
    g = _CHASE.setdefault(
        chat_id, {"players": set(), "names": {}, "target": None, "running": False}
    )
    if g["running"]:
        await message.reply_text("Chase already running.")
        return
    g["players"].add(user.id)
    g["names"][user.id] = user.first_name or str(user.id)
    await message.reply_text(
        f"🏃 {user.mention} joined chase!\n"
        f"Players: {len(g['players'])}\n"
        f"`/chasestart` to begin"
    )


@bot.on_message(filters.command("chasestart", prefixes=PREFIXES) & filters.group)
async def chase_start(client, message: Message):
    chat_id = message.chat.id
    g = _CHASE.get(chat_id)
    if not g or len(g["players"]) < 2:
        await message.reply_text("Kam se kam 2 players (`/chase`).")
        return
    if g["running"]:
        await message.reply_text("Already running.")
        return
    target = random.choice(list(g["players"]))
    g["target"] = target
    g["running"] = True
    tname = g["names"].get(target, str(target))
    await message.reply_text(
        f"🏃 <b>Chase started!</b>\n"
        f"Target is hiding among players...\n"
        f"Reply to someone with `/catch` to catch them!\n"
        f"<i>(Target id secret — try your luck)</i>"
    )
    # optional: whisper only in logs; target not announced for fun
    _ = tname


@bot.on_message(filters.command("catch", prefixes=PREFIXES) & filters.group)
async def chase_catch(client, message: Message):
    chat_id = message.chat.id
    g = _CHASE.get(chat_id)
    if not g or not g.get("running"):
        await message.reply_text("Koi chase active nahi.")
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("Reply to a player: `/catch`")
        return
    victim = message.reply_to_message.from_user
    if victim.id == g["target"]:
        await message.reply_text(
            f"🎯 {message.from_user.mention} caught "
            f"<b>{g['names'].get(victim.id, victim.first_name)}</b>!\n"
            f"🏆 Chase over."
        )
        _CHASE.pop(chat_id, None)
    else:
        await message.reply_text("Miss! Galat person.")
