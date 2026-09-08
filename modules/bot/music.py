"""
Bot-side music — members: /play /vplay /skip /stop /pause /resume /queue

VC client = ASSISTANT_SESSION if set, else STRING_SESSION (app).
Before play: bot tries to invite assistant into the group (needs Add Users right).
"""
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import (
    UserAlreadyParticipant,
    UserPrivacyRestricted,
    ChatAdminRequired,
    RPCError,
)

from core.clients import bot, app, assistant
from core.call_manager import (
    play_track,
    stop_stream,
    pause_stream,
    resume_stream,
    get_queue,
    get_current,
    ensure_started,
)
from modules.vc.streams import get_result

if bot is None:
    raise RuntimeError("modules.bot.music needs BOT_TOKEN")

PREFIXES = ["/", ".", "!"]


def _vc_client():
    """Account that actually joins the voice chat."""
    return assistant if assistant is not None else app


def _is_video_cmd(cmd: str) -> bool:
    c = cmd.lower().lstrip("./!")
    return c in ("vplay", "vply", "cvplay", "cvply", "video")


async def ensure_assistant_in_group(chat_id: int) -> tuple[bool, str]:
    """
    Bot invites the VC account (assistant/app) into the group.
    Returns (ok, message).
    """
    vc = _vc_client()
    try:
        me_vc = await vc.get_me()
    except Exception as e:
        return False, f"VC account get_me failed: `{e}`"

    # Already in chat?
    try:
        member = await bot.get_chat_member(chat_id, me_vc.id)
        if member and getattr(member, "status", None) is not None:
            status = str(member.status).lower()
            if "left" not in status and "banned" not in status and "kicked" not in status:
                return True, "already_in"
    except RPCError:
        pass  # not in group → try add

    # Invite
    try:
        await bot.add_chat_members(chat_id, me_vc.id)
        return True, "invited"
    except UserAlreadyParticipant:
        return True, "already_in"
    except UserPrivacyRestricted:
        return False, (
            "❌ Assistant privacy ki wajah se add nahi hua.\n"
            "Assistant account → Settings → Privacy → Groups → Everybody\n"
            "ya us account ko manually group mein add karo."
        )
    except ChatAdminRequired:
        return False, (
            "❌ Bot ko **Add Users** admin right do, "
            "tab assistant auto-invite hoga.\n"
            "Ya assistant ko manually group mein daalo."
        )
    except RPCError as e:
        return False, f"❌ Invite failed: `{e}`\nAssistant ko manually add karo."


@bot.on_message(
    filters.command(
        ["play", "vplay", "vply", "cplay", "cvplay", "cvply"],
        prefixes=PREFIXES,
    )
    & filters.group
)
async def bot_play_cmd(client, message: Message):
    if not message.from_user:
        return

    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text(
            "Usage:\n`/play song name`\n`/vplay song name` — video"
        )
        return

    query = parts[1].strip()
    is_video = _is_video_cmd(parts[0])
    chat_id = message.chat.id
    vc = _vc_client()

    status = await message.reply_text("⏳ Preparing...")

    # 1) Ensure assistant/userbot is in the group
    ok, info = await ensure_assistant_in_group(chat_id)
    if not ok:
        await status.edit_text(info)
        return
    if info == "invited":
        try:
            await status.edit_text("✅ Assistant added — searching...")
        except Exception:
            pass

    # 2) Download
    try:
        await status.edit_text("🔎 Searching...")
    except Exception:
        pass

    try:
        result = await get_result(query, video=is_video)
    except Exception as e:
        await status.edit_text(f"❌ Search/download failed:\n`{e}`")
        return

    title = result["title"]
    stream_url = result["stream_url"]
    video = result.get("video", is_video)

    queue = get_queue(vc, chat_id)
    current = get_current(vc)

    track = {
        "title": title,
        "stream_url": stream_url,
        "video": video,
        "requested_by": message.from_user.id,
    }

    if chat_id in current and current.get(chat_id):
        queue.append(track)
        await status.edit_text(
            f"➕ Queued: <b>{title}</b>\nPosition: <code>{len(queue)}</code>"
        )
        return

    current[chat_id] = track
    try:
        await ensure_started(vc)
        await play_track(vc, chat_id, stream_url, video=video)
        await status.edit_text(f"▶️ Playing: <b>{title}</b>")
    except Exception as e:
        current.pop(chat_id, None)
        await status.edit_text(f"❌ Play failed:\n`{e}`")


@bot.on_message(filters.command(["skip", "next"], prefixes=PREFIXES) & filters.group)
async def bot_skip_cmd(client, message: Message):
    chat_id = message.chat.id
    vc = _vc_client()
    queue = get_queue(vc, chat_id)
    current = get_current(vc)

    if not queue:
        await stop_stream(vc, chat_id)
        await message.reply_text("⏭ Queue empty — stopped.")
        return

    next_track = queue.pop(0)
    current[chat_id] = next_track
    try:
        await play_track(
            vc, chat_id, next_track["stream_url"], video=next_track.get("video", False)
        )
        await message.reply_text(f"⏭ Now: <b>{next_track['title']}</b>")
    except Exception as e:
        await message.reply_text(f"❌ Skip failed: `{e}`")


@bot.on_message(filters.command(["stop", "end"], prefixes=PREFIXES) & filters.group)
async def bot_stop_cmd(client, message: Message):
    await stop_stream(_vc_client(), message.chat.id)
    await message.reply_text("⏹ Stopped — left VC.")


@bot.on_message(filters.command("pause", prefixes=PREFIXES) & filters.group)
async def bot_pause_cmd(client, message: Message):
    try:
        await pause_stream(_vc_client(), message.chat.id)
        await message.reply_text("⏸ Paused.")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@bot.on_message(filters.command("resume", prefixes=PREFIXES) & filters.group)
async def bot_resume_cmd(client, message: Message):
    try:
        await resume_stream(_vc_client(), message.chat.id)
        await message.reply_text("▶️ Resumed.")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@bot.on_message(filters.command(["queue", "q"], prefixes=PREFIXES) & filters.group)
async def bot_queue_cmd(client, message: Message):
    vc = _vc_client()
    chat_id = message.chat.id
    current = get_current(vc).get(chat_id)
    queue = get_queue(vc, chat_id)

    if not current and not queue:
        await message.reply_text("Queue empty.")
        return

    lines = []
    if current:
        lines.append(f"▶️ <b>Now:</b> {current.get('title', '?')}")
    for i, t in enumerate(queue, 1):
        lines.append(f"{i}. {t.get('title', '?')}")
    await message.reply_text("\n".join(lines))
