"""Fun ASCII / emoji commands"""
import asyncio

from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

FRAME_DELAY = 0.5

CAT_ANIMATION = [
    "🐈",
    "🐈 Walking...",
    "╱|、\n( .. )\n |、˜〵\nじしˍ,)ノ",
    "╱|、\n( > < )\n |、˜〵\nじしˍ,)ノ",
    "╱|、\n(˚ˎ 。7\n |、˜〵\nじしˍ,)ノ",
    "╱|、\n(˚ˎ 。7  Meow!\n |、˜〵\nじしˍ,)ノ",
]

FLOWER_BLOOM = ["🌱", "🌿", "🌷", "🌹"]

ROSE_ART = "🌹🌹🌹\n  🌹  \n  🌹  \n FOR YOU "

HACKER_ART = (
    "[ SYSTEM ACCESS ]\n"
    "> bypass firewall...\n"
    "> decrypt keys...\n"
    "> ROOT OK\n"
    "SYSTEM HACKED"
)

HEART_FRAMES = [
    "❤️", "❤️🧡", "❤️🧡💛", "❤️🧡💛💚",
    "❤️🧡💛💚💙", "❤️🧡💛💚💙💜", "❤️❤️❤️",
]


async def _animate(status: Message, frames: list):
    for frame in frames:
        try:
            await status.edit_text(f"<code>{frame}</code>")
        except Exception:
            pass
        await asyncio.sleep(FRAME_DELAY)


@app.on_message(ub_cmd("cat"))
@sudo_only
async def cat_cmd(client, message: Message):
    print("[fun] .cat")
    status = await message.reply_text("🐈")
    await _animate(status, CAT_ANIMATION)


@app.on_message(ub_cmd("rose"))
@sudo_only
async def rose_cmd(client, message: Message):
    print("[fun] .rose")
    status = await message.reply_text("🌱")
    await _animate(status, FLOWER_BLOOM)
    try:
        await status.edit_text(f"<code>{ROSE_ART}</code>\n🌹 <b>FOR YOU!</b>")
    except Exception:
        await message.reply_text("🌹 FOR YOU!")


@app.on_message(ub_cmd("hacker", "hack"))
@sudo_only
async def hacker_cmd(client, message: Message):
    print("[fun] .hacker")
    status = await message.reply_text("💻 Hacking...")
    await asyncio.sleep(FRAME_DELAY)
    try:
        await status.edit_text(f"<code>{HACKER_ART}</code>")
    except Exception:
        await message.reply_text("💻 SYSTEM HACKED!")


@app.on_message(ub_cmd("heart"))
@sudo_only
async def heart_cmd(client, message: Message):
    print("[fun] .heart")
    status = await message.reply_text("❤️")
    await _animate(status, HEART_FRAMES)


@app.on_message(ub_cmd("butterfly"))
@sudo_only
async def butterfly_cmd(client, message: Message):
    await message.reply_text("🦋 Fly high!")


@app.on_message(ub_cmd("error"))
@sudo_only
async def error_cmd(client, message: Message):
    await message.reply_text("⚠️ FATAL ERROR DETECTED!")
