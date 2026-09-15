"""
Premium Animation Pack
  .hack .moon .loveanim .type .bomb .heart ...
  .animlist — saari commands

Note: 1 minute continuous edit = FLOOD_WAIT. Frames \~0.6–0.9s (safe).
"""
import asyncio
import functools

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!", "/"]
DELAY = 0.65  # safe; zyada = flood


async def _animate(message: Message, frames: list[str], delay: float = DELAY):
    """Reply once, then edit frames (premium style)."""
    try:
        msg = await message.reply_text(f"✨ <code>{frames[0]}</code>")
    except Exception:
        return
    for frame in frames[1:]:
        await asyncio.sleep(delay)
        try:
            await msg.edit_text(f"✨ <code>{frame}</code>")
        except Exception:
            # flood / message deleted
            break
    await asyncio.sleep(0.4)
    try:
        # final without code wrap if last is fancy
        last = frames[-1]
        await msg.edit_text(f"━━━━━━━━━━━━━━\n{last}\n━━━━━━━━━━━━━━")
    except Exception:
        pass


def anim_handler(frames: list[str], delay: float = DELAY):
    async def _cmd(client, message: Message):
        await _animate(message, frames, delay)
    return _cmd


# ---------- Featured (longer / richer) ----------

@app.on_message(filters.command(["hack", "hackanim"], prefixes=PREFIXES))
@sudo_only
async def hack_anim(client, message: Message):
    target = "Target"
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.first_name or "User"
    elif len(message.command) > 1:
        target = message.command[1]
    frames = [
        f"🔐 Initializing hack on {target}...",
        "📡 Connecting secure channel...",
        "10%  [▰▱▱▱▱▱▱▱▱▱]",
        "25%  [▰▰▰▱▱▱▱▱▱▱]",
        "40%  [▰▰▰▰▱▱▱▱▱▱]",
        "55%  [▰▰▰▰▰▱▱▱▱▱]",
        "70%  [▰▰▰▰▰▰▰▱▱▱]",
        "85%  [▰▰▰▰▰▰▰▰▱▱]",
        "95%  [▰▰▰▰▰▰▰▰▰▱]",
        "100% [▰▰▰▰▰▰▰▰▰▰]",
        f"✅ Access granted\n🎯 {target}\n🔑 Password: •••••• 😂\n\n<i>Just for fun — not real</i>",
    ]
    await _animate(message, frames, 0.7)


@app.on_message(filters.command("moon", prefixes=PREFIXES))
@sudo_only
async def moon_anim(client, message: Message):
    moons = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    frames = moons + moons + ["🌕 Full Moon ✨"]
    await _animate(message, frames, 0.55)


@app.on_message(filters.command(["loveanim", "loveu"], prefixes=PREFIXES))
@sudo_only
async def love_anim(client, message: Message):
    # .love often used by shayari — alag naam
    frames = ["🤍", "💙", "💚", "💛", "🧡", "❤️", "💖", "💝", "💞", "❤️‍🔥", "I Love You ❤️"]
    await _animate(message, frames, 0.45)


@app.on_message(filters.command(["type", "typewriter"], prefixes=PREFIXES))
@sudo_only
async def type_anim(client, message: Message):
    text = (
        message.text.split(None, 1)[1]
        if len(message.command) > 1
        else "I Love You"
    )[:60]
    msg = await message.reply_text("⌨️ ▌")
    out = ""
    for ch in text:
        out += ch
        await asyncio.sleep(0.18)
        try:
            await msg.edit_text(f"⌨️ <code>{out}</code>▌")
        except Exception:
            return
    await asyncio.sleep(0.3)
    try:
        await msg.edit_text(f"━━━━━━━━━━━━━━\n{out}\n━━━━━━━━━━━━━━")
    except Exception:
        pass


@app.on_message(filters.command("loading", prefixes=PREFIXES))
@sudo_only
async def loading_anim(client, message: Message):
    frames = [
        "▱▱▱▱▱▱▱▱ 0%",
        "▰▱▱▱▱▱▱▱ 12%",
        "▰▰▱▱▱▱▱▱ 25%",
        "▰▰▰▱▱▱▱▱ 37%",
        "▰▰▰▰▱▱▱▱ 50%",
        "▰▰▰▰▰▱▱▱ 62%",
        "▰▰▰▰▰▰▱▱ 75%",
        "▰▰▰▰▰▰▰▱ 87%",
        "▰▰▰▰▰▰▰▰ 100%",
        "✅ Loaded",
    ]
    await _animate(message, frames, 0.6)


# ---------- Bulk pack (closure-safe) ----------

ANIMS: dict[str, list[str]] = {
    "bomb": ["💣 3", "💣 2", "💣 1", "💥 BOOM", "💨 Smoke...", "😂 Fake bomb"],
    "heart": ["🤍", "💙", "💚", "💛", "🧡", "❤️", "💖", "I ❤️ U"],
    "kill": ["🎯 Locking...", "🔫 Aimed", "💀 Boom", "😂 Fake KO"],
    "police": ["🚨 Alert", "🚔 Coming...", "🏃 Run!", "😂 Drama over"],
    "earth": ["🌍", "🌎", "🌏", "🌐", "My World ❤️"],
    "rain": ["☁️", "🌧", "⛈️", "🌦️", "Baarish ✨"],
    "plane": ["✈️", "·✈️", "··✈️", "···✈️", "Gone ✈️"],
    "clock": ["🕛", "🕐", "🕑", "🕒", "🕓", "Time flies ⏳"],
    "snake": ["🐍", "·🐍", "··🐍", "···🐍", "Bite! 😂"],
    "star": ["⭐", "🌟", "✨", "💫", "You are a star ✨"],
    "fire": ["·", "🔥", "🔥🔥", "🔥🔥🔥", "Full Fire 🔥"],
    "cool": ["·", "😎", "Cool...", "😎✅"],
    "cry": ["😢", "😭", "😭😭", "Ab has ❤️"],
    "laugh": ["😂", "🤣", "😂🤣", "LOL 😂"],
    "angry": ["😐", "😡", "🤬", "Calm down 🙏"],
    "sleep": ["😮‍💨", "😴", "💤", "💤💤", "Good night"],
    "run": ["·", "🏃", "🏃💨", "Too fast"],
    "dance": ["·", "💃", "🕺", "💃🕺", "Party"],
    "think": ["·", "🤔", "Thinking...", "Idea 💡"],
    "ok": ["·", "👌", "OK", "Done ✅"],
    "hi": ["·", "Hi", "Hiii", "Hello 👋"],
    "bye": ["·", "Bye", "Bye bye", "See you 👋"],
    "wtf": ["W", "WT", "WTF", "😳"],
    "lol": ["L", "LO", "LOL", "😂😂"],
    "pro": ["Pro", "Pro Max", "Ultra Pro 😎"],
    "noob": ["Noob?", "Noobda", "Practice 💪"],
    "king": ["·", "👑", "King", "King 👑"],
    "queen": ["·", "👸", "Queen", "My Queen ❤️"],
    "money": ["·", "💸", "💰", "💵 Paisa"],
    "study": ["·", "📚", "Padhai...", "Topper 😎"],
    "game": ["·", "🎮", "Gaming...", "Winner 🏆"],
    "music": ["·", "🎵", "🎶", "🎧 Music On"],
    "coffee": ["·", "☕", "Sip...", "☕☕"],
    "tea": ["·", "🍵", "Chai garam", "Chai lover"],
    "cake": ["·", "🎂", "🎉", "Happy Birthday 🎂"],
    "gift": ["·", "🎁", "Open...", "🎁❤️"],
    "ball": ["·", "⚽", "Shoot...", "GOAL ⚽"],
    "bat": ["·", "🏏", "Shot!", "SIX 💥"],
    "car": ["·", "🚗", "💨", "Race 🏎️"],
    "bike": ["·", "🏍️", "Vroom", "🏍️💨"],
    "train": ["·", "🚂", "Chuk chuk", "🚂💨"],
    "rocket": ["·", "🚀", "Launch...", "🚀🌕"],
    "sun": ["🌌", "🌅", "🌤", "☀️ Good Morning"],
    "night": ["·", "🌙", "✨", "Good Night 🌙"],
    "party": ["·", "🎉", "🎊", "🎈", "🥳 Party!"],
    "boom": ["3️⃣", "2️⃣", "1️⃣", "💥 BOOM!"],
    "heartbeat": ["❤️", "🤍", "❤️", "🤍", "💖 Beating"],
    "congo": ["·", "✨", "🎉", "Congratulations 🎊"],
}


def _register():
    for name, frames in ANIMS.items():
        # IMPORTANT: default-arg bind frames (closure fix)
        async def _cmd(client, message: Message, fr=frames):
            await _animate(message, fr)

        _cmd.__name__ = f"anim_{name}"
        app.on_message(filters.command(name, prefixes=PREFIXES))(sudo_only(_cmd))


_register()


@app.on_message(filters.command(["animlist", "anims"], prefixes=PREFIXES))
@sudo_only
async def animlist_cmd(client, message: Message):
    featured = "hack moon loveanim type loading"
    bulk = " ".join(f".{k}" for k in sorted(ANIMS.keys()))
    await message.reply_text(
        "🎬 <b>ANIMATION PACK</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"<b>Featured:</b> {featured}\n\n"
        f"<b>More:</b>\n<code>{bulk}</code>\n"
        "━━━━━━━━━━━━━━\n"
        "<i>Premium edit frames · flood-safe delay</i>"
                   )
