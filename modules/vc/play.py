from pyrogram.types import Message

from core.clients import app
from core.call_manager import play_track, get_queue, get_current
from modules.vc.streams import get_result
from modules.owner.sudoers import ub_cmd, sudo_only


@app.on_message(ub_cmd("play", "vply", "cplay", "cvply", "vplay"))
@sudo_only
async def play_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("Usage: <code>.play song name</code>")
        return

    query = parts[1]
    cmd0 = parts[0].lstrip(".!").lower().split("@")[0]
    is_video = cmd0 in ("vply", "cvply", "vplay")
    chat_id = message.chat.id

    status = await message.reply_text(f"Searching: <b>{query}</b>")

    try:
        result = await get_result(query, video=is_video)
    except Exception as e:
        await status.edit_text(f"Failed: <code>{e}</code>")
        return

    queue = get_queue(client, chat_id)
    current = get_current(client)

    if chat_id in current:
        queue.append(result)
        await status.edit_text(f"Queued <b>{result['title']}</b> (#{len(queue)})")
        return

    current[chat_id] = result
    try:
        await play_track(client, chat_id, result["stream_url"], video=is_video)
    except Exception as e:
        current.pop(chat_id, None)
        await status.edit_text(f"Stream failed: <code>{e}</code>")
        return

    kind = "Video" if is_video else "Audio"
    await status.edit_text(f"{kind}: <b>{result['title']}</b>")
