"""
GF-BF premium animations
"""
import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def _who(message: Message) -> str:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.mention
    if len(message.command) > 1:
        return message.command[1]
    return "My Love"


async def _anim(message, frames, delay=0.5):
    msg = await message.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(delay)
        try:
            await msg.edit_text(f)
        except Exception:
            break


@app.on_message(filters.command("propose", prefixes=PREFIXES))
@sudo_only
async def propose_cmd(client, message: Message):
    gf = _who(message)
    await _anim(message, [
        "·", "•", "❤️", "💖",
        f"Hey {gf}...",
        f"Hey {gf} ❤️",
        f"🌹 {gf} 🌹",
        f"💍 {gf}, Will You Be Mine? 💍",
        f"❤️ {gf} ❤️\n💍 Say Yes 💍\n🌹🌹🌹",
    ])


@app.on_message(filters.command(["iloveu", "ily"], prefixes=PREFIXES))
@sudo_only
async def ily_cmd(client, message: Message):
    gf = _who(message)
    colors = ["❤️", "🧡", "💛", "💚", "💙", "💜", "💖"]
    frames = [f"{c} I Love You {gf} {c}" for c in colors]
    frames.append(f"🌈 I Love You {gf} ❤️‍🔥")
    await _anim(message, frames, 0.35)


@app.on_message(filters.command("rainbow", prefixes=PREFIXES))
@sudo_only
async def rainbow_cmd(client, message: Message):
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "I Love You"
    colors = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "💖"]
    frames = [f"{c} {text} {c}" for c in colors]
    frames.append(f"🌈 {text} 🌈")
    await _anim(message, frames, 0.35)


@app.on_message(filters.command(["lovecalc", "lovepercent"], prefixes=PREFIXES))
@sudo_only
async def lovecalc_cmd(client, message: Message):
    a = _who(message)
    b = message.command[2] if len(message.command) > 2 else "You"
    pct = random.randint(40, 100)
    await _anim(message, [
        "💕 Calculating...",
        "💕 10%", "💕 40%", "💕 70%",
        f"💞 {a} + {b}\nLove: <b>{pct}%</b> 💘",
    ])


@app.on_message(filters.command("sorry", prefixes=PREFIXES))
@sudo_only
async def sorry_cmd(client, message: Message):
    gf = _who(message)
    await _anim(message, [
        "·", "🥺", "Sorry...",
        f"Sorry {gf} 💔",
        f"Please maaf kar do {gf} 🙏❤️",
        f"❤️ {gf} ❤️\nI am really sorry 🥺",
    ])


@app.on_message(filters.command(["manau", "patchup"], prefixes=PREFIXES))
@sudo_only
async def manau_cmd(client, message: Message):
    gf = _who(message)
    await _anim(message, [
        "💔", "💔💔", "❤️‍🩹",
        f"Please {gf}...",
        f"❤️ {gf} wapas aa jao ❤️",
        f"💖 Patch-up complete? 🤞",
    ])


@app.on_message(filters.command("missu", prefixes=PREFIXES))
@sudo_only
async def missu_cmd(client, message: Message):
    gf = _who(message)
    await _anim(message, [
        "·", "💭", f"Missing {gf}...",
        f"I Miss You {gf} 🤍",
        f"💗 I Miss You {gf} 💗",
    ])


@app.on_message(filters.command("ring", prefixes=PREFIXES))
@sudo_only
async def ring_cmd(client, message: Message):
    gf = _who(message)
    await _anim(message, [
        "·", "•", "💍", "💍✨",
        f"💍 For {gf}",
        f"💍 {gf}, accept this ring? 🌹",
    ])


@app.on_message(filters.command(["heartlock", "lockheart"], prefixes=PREFIXES))
@sudo_only
async def heartlock_cmd(client, message: Message):
    gf = _who(message)
    await _anim(message, [
        "❤️", "🔐❤️", "🔒❤️",
        f"❤️ Locked with {gf} 🔒",
    ])
