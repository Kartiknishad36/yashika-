"""
Simple Ludo-style race: /ludo join | /ludo start | /ludo roll
First to 20 wins.
"""
import random
from pyrogram import filters
from pyrogram.types import Message

from core.clients import bot

if bot is None:
    raise RuntimeError("modules.games.ludo needs BOT_TOKEN")

PREFIXES = ["/", ".", "!"]
WIN_AT = 20

# chat_id -> {pos: {uid: int}, names: {}, order: [], turn: int, running: bool}
_LUDO: dict[int, dict] = {}


@bot.on_message(filters.command("ludo", prefixes=PREFIXES) & filters.group)
async def ludo_cmd(client, message: Message):
    chat_id = message.chat.id
    args = message.command[1:] if len(message.command) > 1 else []
    user = message.from_user
    if not user:
        return

    if not args or args[0].lower() == "join":
        g = _LUDO.setdefault(
            chat_id,
            {"pos": {}, "names": {}, "order": [], "turn": 0, "running": False},
        )
        if g["running"]:
            await message.reply_text("Ludo already running.")
            return
        if user.id in g["pos"]:
            await message.reply_text("Already joined.")
            return
        g["pos"][user.id] = 0
        g["names"][user.id] = user.first_name or str(user.id)
        g["order"].append(user.id)
        await message.reply_text(
            f"🎲 {user.mention} joined Ludo!\n"
            f"Players: {len(g['order'])}\n"
            f"`/ludo start` when ready"
        )
        return

    action = args[0].lower()
    g = _LUDO.get(chat_id)

    if action == "start":
        if not g or len(g["order"]) < 2:
            await message.reply_text("Kam se kam 2 players.")
            return
        g["running"] = True
        g["turn"] = 0
        for uid in g["pos"]:
            g["pos"][uid] = 0
        first = g["names"][g["order"][0]]
        await message.reply_text(
            f"🎲 Ludo started! First to <b>{WIN_AT}</b> wins.\n"
            f"Turn: <b>{first}</b> — `/ludo roll`"
        )
        return

    if action == "roll":
        if not g or not g["running"]:
            await message.reply_text("No active ludo. `/ludo join`")
            return
        uid = g["order"][g["turn"] % len(g["order"])]
        if user.id != uid:
            await message.reply_text(
                f"Not your turn. Waiting for <b>{g['names'][uid]}</b>."
            )
            return
        dice = random.randint(1, 6)
        g["pos"][uid] = g["pos"].get(uid, 0) + dice
        pos = g["pos"][uid]
        name = g["names"][uid]
        if pos >= WIN_AT:
            await message.reply_text(
                f"🎲 {name} rolled <b>{dice}</b> → position {pos}\n"
                f"🏆 <b>{name}</b> wins!"
            )
            _LUDO.pop(chat_id, None)
            return
        g["turn"] += 1
        nxt = g["order"][g["turn"] % len(g["order"])]
        await message.reply_text(
            f"🎲 {name} rolled <b>{dice}</b> → <b>{pos}/{WIN_AT}</b>\n"
            f"Next: <b>{g['names'][nxt]}</b> `/ludo roll`"
        )
        return

    if action == "stop":
        _LUDO.pop(chat_id, None)
        await message.reply_text("Ludo stopped.")
        return

    await message.reply_text(
        "`/ludo join` | `/ludo start` | `/ludo roll` | `/ludo stop`"
      )
