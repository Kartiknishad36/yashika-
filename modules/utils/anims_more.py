"""
More animations: moon sun party congo birthday loading variants
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


async def _play(m: Message, frames, d=0.4):
    msg = await m.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(d)
        try:
            await msg.edit_text(f)
        except Exception:
            break


@app.on_message(filters.command("moon", prefixes=PREFIXES))
@sudo_only
async def moon_cmd(c, m):
    await _play(m, ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘", "🌕 Full Moon"])


@app.on_message(filters.command("sun", prefixes=PREFIXES))
@sudo_only
async def sun_cmd(c, m):
    await _play(m, ["🌌", "🌅", "🌤", "☀️", "☀️ Bright Day"])


@app.on_message(filters.command("party", prefixes=PREFIXES))
@sudo_only
async def party_cmd(c, m):
    await _play(m, ["🎉", "🎊", "🎈", "🎉🎊🎈", "🥳 Party Time!"])


@app.on_message(filters.command("congo", prefixes=PREFIXES))
@sudo_only
async def congo_cmd(c, m):
    await _play(m, ["·", "✨", "🎉", "🎊 Congratulations! 🎊"])


@app.on_message(filters.command("birthday", prefixes=PREFIXES))
@sudo_only
async def bday_cmd(c, m):
    who = m.command[1] if len(m.command) > 1 else "Friend"
    if m.reply_to_message and m.reply_to_message.from_user:
        who = m.reply_to_message.from_user.mention
    await _play(m, [
        "🎂", "🎂✨", "🎉🎂🎉",
        f"🎂 Happy Birthday {who}! 🎈",
    ])


@app.on_message(filters.command(["fireanim", "fire"], prefixes=PREFIXES))
@sudo_only
async def fire_cmd(c, m):
    await _play(m, ["·", "🔥", "🔥🔥", "🔥🔥🔥", "💥"])


@app.on_message(filters.command(["heartanim", "hearts"], prefixes=PREFIXES))
@sudo_only
async def hearts_cmd(c, m):
    await _play(m, ["❤️", "🧡", "💛", "💚", "💙", "💜", "💖"], 0.3)
