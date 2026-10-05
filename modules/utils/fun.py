"""Fun ASCII — filters.me for reliable userbot"""
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd

FRAME_DELAY = 0.4

CAT_ANIMATION = ["🐈", "🐈 Walking...", "Meow!"]
FLOWER_BLOOM = ["🌱", "🌿", "🌷", "🌹"]
ROSE_ART = "🌹🌹🌹\n  🌹\n FOR YOU"
HACKER_ART = "[ SYSTEM ACCESS ]\n> ROOT OK\nSYSTEM HACKED"
HEART_FRAMES = ["❤️", "❤️🧡", "❤️🧡💛", "❤️❤️❤️"]


async def _animate(status: Message, frames: list):
    for frame in frames:
        try:
            await status.edit_text(frame)
        except Exception:
            pass
        await asyncio.sleep(FRAME_DELAY)


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]cat(\s|$)"), group=-8)
async def cat_cmd(client, message: Message):
    print("[fun] .cat")
    status = await message.reply_text("🐈")
    await _animate(status, CAT_ANIMATION)


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]rose(\s|$)"), group=-8)
async def rose_cmd(client, message: Message):
    print("[fun] .rose")
    status = await message.reply_text("🌱")
    await _animate(status, FLOWER_BLOOM)
    try:
        await status.edit_text(f"{ROSE_ART}\n🌹 <b>FOR YOU!</b>")
    except Exception:
        await message.reply_text("🌹 FOR YOU!")


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!](hacker|hack)(\s|$)"), group=-8)
async def hacker_cmd(client, message: Message):
    print("[fun] .hacker")
    status = await message.reply_text("💻 Hacking...")
    await asyncio.sleep(FRAME_DELAY)
    try:
        await status.edit_text(f"<code>{HACKER_ART}</code>")
    except Exception:
        await message.reply_text("💻 HACKED!")


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]heart(\s|$)"), group=-8)
async def heart_cmd(client, message: Message):
    status = await message.reply_text("❤️")
    await _animate(status, HEART_FRAMES)


@app.on_message(ub_cmd("butterfly", "error"), group=-8)
async def misc_fun(client, message: Message):
    cmd = (message.text or "")[1:].split()[0].lower()
    if cmd == "butterfly":
        await message.reply_text("🦋 Fly high!")
    else:
        await message.reply_text("⚠️ FATAL ERROR DETECTED!")
