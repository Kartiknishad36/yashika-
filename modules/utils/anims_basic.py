"""
.hackanim .loading .typinganim .boom .heartbeat
"""
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


async def _play(message: Message, frames: list[str], delay: float = 0.45):
    msg = await message.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(delay)
        try:
            await msg.edit_text(f)
        except Exception:
            break
    return msg


@app.on_message(filters.command(["hackanim", "hack"], prefixes=PREFIXES))
@sudo_only
async def hack_cmd(client, message: Message):
    target = message.command[1] if len(message.command) > 1 else "Target"
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.mention
    await _play(
        message,
        [
            f"Hacking {target}…",
            "10%  [▰▱▱▱▱▱▱▱]",
            "45%  [▰▰▰▰▱▱▱▱]",
            "80%  [▰▰▰▰▰▰▰▱]",
            f"✅ Hacked {target}\nPassword: ******** 😂\n<i>just for fun</i>",
        ],
    )


@app.on_message(filters.command("loading", prefixes=PREFIXES))
@sudo_only
async def loading_cmd(client, message: Message):
    await _play(
        message,
        ["▱▱▱▱▱ 0%", "▰▱▱▱▱ 20%", "▰▰▱▱▱ 40%", "▰▰▰▱▱ 60%", "▰▰▰▰▱ 80%", "✅ 100% Done"],
        0.35,
    )


@app.on_message(filters.command(["typinganim", "type"], prefixes=PREFIXES))
@sudo_only
async def type_cmd(client, message: Message):
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "Premium Userbot"
    msg = await message.reply_text("▌")
    cur = ""
    for ch in text[:80]:
        cur += ch
        await asyncio.sleep(0.12)
        try:
            await msg.edit_text(cur + "▌")
        except Exception:
            break
    await msg.edit_text(cur)


@app.on_message(filters.command("boom", prefixes=PREFIXES))
@sudo_only
async def boom_cmd(client, message: Message):
    await _play(message, ["3️⃣", "2️⃣", "1️⃣", "💥 BOOM!"])


@app.on_message(filters.command("heartbeat", prefixes=PREFIXES))
@sudo_only
async def heartbeat_cmd(client, message: Message):
    frames = ["❤️", "🤍", "❤️", "🤍", "💖", "I Love You ❤️‍🔥"]
    await _play(message, frames, 0.3)
