from pyrogram import filters
from pyrogram.types import Message
from database.mongo import set_vcinfo_enabled, get_vcinfo_enabled

from core.clients import app
from core.call_manager import (
    pause_stream, resume_stream, stop_stream, mute_stream, unmute_stream,
    play_track, get_queue, get_current,
)
from modules.owner.sudoers import ub_cmd


@app.on_message(ub_cmd("pause") & filters.me)
async def pause_cmd(client, message: Message):
    await pause_stream(client, message.chat.id)
    await message.reply_text("Paused.")


@app.on_message(ub_cmd("resume") & filters.me)
async def resume_cmd(client, message: Message):
    await resume_stream(client, message.chat.id)
    await message.reply_text("Resumed.")


@app.on_message(ub_cmd("vmute") & filters.me)
async def mute_cmd(client, message: Message):
    await mute_stream(client, message.chat.id)
    await message.reply_text("VC muted.")


@app.on_message(ub_cmd("vunmute") & filters.me)
async def unmute_cmd(client, message: Message):
    await unmute_stream(client, message.chat.id)
    await message.reply_text("VC unmuted.")


@app.on_message(ub_cmd("stop", "end") & filters.me)
async def stop_cmd(client, message: Message):
    await stop_stream(client, message.chat.id)
    await message.reply_text("Stopped and left VC.")


@app.on_message(ub_cmd("skip") & filters.me)
async def skip_cmd(client, message: Message):
    chat_id = message.chat.id
    queue = get_queue(client, chat_id)
    current = get_current(client)
    if not queue:
        await stop_stream(client, chat_id)
        await message.reply_text("Queue empty, stopped.")
        return
    next_track = queue.pop(0)
    current[chat_id] = next_track
    try:
        await play_track(
            client, chat_id, next_track["stream_url"],
            video=next_track.get("video", False),
        )
        await message.reply_text(f"Now: <b>{next_track['title']}</b>")
    except Exception as e:
        await message.reply_text(f"Skip failed: <code>{e}</code>")


@app.on_message(ub_cmd("vcinfo") & filters.me)
async def vcinfo_cmd(client, message: Message):
    chat_id = message.chat.id
    parts = (message.text or "").split()
    args = parts[1:] if len(parts) > 1 else []
    if not args:
        on = await get_vcinfo_enabled(chat_id)
        await message.reply_text(
            f"VC Info: <b>{'ON' if on else 'OFF'}</b>\n"
            f"<code>.vcinfo on</code> | <code>.vcinfo off</code>"
        )
        return
    action = args[0].lower()
    if action in ("on", "enable", "1", "true"):
        await set_vcinfo_enabled(chat_id, True)
        await message.reply_text("VC Info <b>ON</b>")
    elif action in ("off", "disable", "0", "false"):
        await set_vcinfo_enabled(chat_id, False)
        await message.reply_text("VC Info <b>OFF</b>")
    else:
        await message.reply_text("Usage: <code>.vcinfo on|off</code>")
