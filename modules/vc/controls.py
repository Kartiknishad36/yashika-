from pyrogram.types import Message
from database.mongo import set_vcinfo_enabled, get_vcinfo_enabled

from core.clients import app
from core.call_manager import (
    pause_stream, resume_stream, stop_stream, mute_stream, unmute_stream,
    play_track, get_queue, get_current,
)
from modules.owner.sudoers import ub_cmd, sudo_only


@app.on_message(ub_cmd("pause"))
@sudo_only
async def pause_cmd(client, message: Message):
    await pause_stream(client, message.chat.id)
    await message.reply_text("Paused.")


@app.on_message(ub_cmd("resume"))
@sudo_only
async def resume_cmd(client, message: Message):
    await resume_stream(client, message.chat.id)
    await message.reply_text("Resumed.")


@app.on_message(ub_cmd("vmute"))
@sudo_only
async def mute_cmd(client, message: Message):
    await mute_stream(client, message.chat.id)
    await message.reply_text("VC muted.")


@app.on_message(ub_cmd("vunmute"))
@sudo_only
async def unmute_cmd(client, message: Message):
    await unmute_stream(client, message.chat.id)
    await message.reply_text("VC unmuted.")


@app.on_message(ub_cmd("stop", "end"))
@sudo_only
async def stop_cmd(client, message: Message):
    await stop_stream(client, message.chat.id)
    await message.reply_text("Stopped and left VC.")


@app.on_message(ub_cmd("skip"))
@sudo_only
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


@app.on_message(ub_cmd("queue"))
@sudo_only
async def queue_cmd(client, message: Message):
    chat_id = message.chat.id
    queue = get_queue(client, chat_id)
    current = get_current(client)
    lines = ["<b>Queue</b>"]
    if chat_id in current:
        lines.append(f"Now: <b>{current[chat_id].get('title', '?')}</b>")
    if not queue:
        lines.append("Empty.")
    else:
        for i, t in enumerate(queue[:15], 1):
            lines.append(f"{i}. {t.get('title', '?')}")
    await message.reply_text("\n".join(lines))


@app.on_message(ub_cmd("vcinfo"))
@sudo_only
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
