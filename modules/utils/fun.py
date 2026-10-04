"""
Fun ASCII / emoji commands — userbot safe (filters.me + ub_cmd)
"""
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd

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

ROSE_ART = (
    "🌹🌹🌹\n"
    "  🌹  \n"
    "  🌹  \n"
    " FOR YOU "
)

HACKER_ART = (
    "[ SYSTEM ACCESS ]\n"
    "> bypass firewall...\n"
    "> decrypt keys...\n"
    "> ROOT OK\n"
    "SYSTEM HACKED"
)

HEART_FRAMES = [
    "❤️",
    "❤️🧡",
    "❤️🧡💛",
    "❤️🧡💛💚",
    "❤️🧡💛💚💙",
    "❤️🧡💛💚💙💜",
    "❤️❤️❤️",
]


async def _animate(status: Message, frames: list):
    for frame in frames:
        try:
            await status.edit_text(f"<code>{frame}</code>")
        except Exception:
            pass
        await asyncio.sleep(FRAME_DELAY)


@app.on_message(ub_cmd("cat") & filters.me)
async def cat_cmd(client, message: Message):
    print("[fun] .cat")
    status = await message.reply_text("🐈")
    await _animate(status, CAT_ANIMATION)


@app.on_message(ub_cmd("rose") & filters.me)
async def rose_cmd(client, message: Message):
    print("[fun] .rose")
    status = await message.reply_text("🌱")
    await _animate(status, FLOWER_BLOOM)
    try:
        await status.edit_text(f"<code>{ROSE_ART}</code>\n🌹 <b>FOR YOU!</b>")
    except Exception:
        await message.reply_text("🌹 FOR YOU!")


@app.on_message(ub_cmd("hacker", "hack") & filters.me)
async def hacker_cmd(client, message: Message):
    print("[fun] .hacker")
    status = await message.reply_text("💻 Hacking...")
    await asyncio.sleep(FRAME_DELAY)
    try:
        await status.edit_text(f"<code>{HACKER_ART}</code>")
    except Exception:
        await message.reply_text("💻 SYSTEM HACKED!")


@app.on_message(ub_cmd("heart") & filters.me)
async def heart_cmd(client, message: Message):
    print("[fun] .heart")
    status = await message.reply_text("❤️")
    await _animate(status, HEART_FRAMES)


@app.on_message(ub_cmd("butterfly") & filters.me)
async def butterfly_cmd(client, message: Message):
    await message.reply_text("🦋 Fly high!")


@app.on_message(ub_cmd("error") & filters.me)
async def error_cmd(client, message: Message):
    await message.reply_text("⚠️ FATAL ERROR DETECTED!")
