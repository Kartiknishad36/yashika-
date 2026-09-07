"""
/bomb — join game, /bombstart — start, timer eliminates random players
"""
import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message

from core.clients import bot

if bot is None:
    raise RuntimeError("modules.games.bomb needs BOT_TOKEN")

PREFIXES = ["/", ".", "!"]

# chat_id -> {"players": set[int], "names": dict, "running": bool}
_GAMES: dict[int, dict] = {}


@bot.on_message(filters.command("bomb", prefixes=PREFIXES) & filters.group)
async def bomb_join(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user
    if not user:
        return
    g = _GAMES.setdefault(chat_id, {"players": set(), "names": {}, "running": False})
    if g["running"]:
        await message.reply_text("Game already running.")
        return
    g["players"].add(user.id)
    g["names"][user.id] = user.first_name or str(user.id)
    await message.reply_text(
        f"💣 {user.mention} joined bomb!\n"
        f"Players: {len(g['players'])}\n"
        f"Start: `/bombstart`"
    )


@bot.on_message(filters.command("bombstart", prefixes=PREFIXES) & filters.group)
async def bomb_start(client, message: Message):
    chat_id = message.chat.id
    g = _GAMES.get(chat_id)
    if not g or len(g["players"]) < 2:
        await message.reply_text("Kam se kam 2 players (`/bomb` se join).")
        return
    if g["running"]:
        await message.reply_text("Already running.")
        return

    g["running"] = True
    players = list(g["players"])
    await message.reply_text(f"💣 Bomb started with {len(players)} players!")

    while len(players) > 1:
        await asyncio.sleep(3)
        victim = random.choice(players)
        players.remove(victim)
        name = g["names"].get(victim, str(victim))
        await client.send_message(
            chat_id,
            f"💥 <b>{name}</b> eliminated! Remaining: {len(players)}",
        )

    winner_id = players[0]
    winner = g["names"].get(winner_id, str(winner_id))
    await client.send_message(chat_id, f"🏆 Winner: <b>{winner}</b>")
    _GAMES.pop(chat_id, None)
