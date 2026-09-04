"""
Per-client PyTgCalls management — every account has its OWN VC engine.

Features:
- Auto play next song when current ends
- Auto leave VC when queue is empty
- Notify in group when someone joins VC (full user info)
- Notify in group when someone leaves VC (full user info)
"""

from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import (
    MediaStream,
    AudioQuality,
    VideoQuality,
    StreamEnded,
    GroupCallParticipant,
    UpdatedGroupCallParticipant,
)

from core.clients import app, assistant

_INSTANCES: dict[int, PyTgCalls] = {}
_STARTED: dict[int, bool] = {}
_QUEUES: dict[int, dict[int, list[dict]]] = {}
_CURRENT: dict[int, dict[int, dict]] = {}


def _resolve_call_client(client):
    if client is app and assistant is not None:
        return assistant
    return client


def get_pytgcalls(client) -> PyTgCalls:
    call_client = _resolve_call_client(client)
    key = id(call_client)
    if key not in _INSTANCES:
        pytg = PyTgCalls(call_client)
        _INSTANCES[key] = pytg
        _register_handlers(pytg, client)
    return _INSTANCES[key]


async def _send_vc_user_info(client, update: UpdatedGroupCallParticipant, is_join: bool):
    chat_id = update.chat_id
    user_id = update.participant.user_id

    try:
        me = await client.get_me()
        if user_id == me.id:
            return
    except Exception:
        pass

    event_text = "Joined Voice Chat" if is_join else "Left Voice Chat"
    emoji = "🎤" if is_join else "🚪"

    try:
        user = await client.get_users(user_id)
    except Exception:
        try:
            await client.send_message(
                chat_id,
                f"{emoji} <b>{event_text}</b>\n\n"
                f"👤 User ID: <code>{user_id}</code>",
            )
        except Exception:
            pass
        return

    full_name = (user.first_name or "") + (f" {user.last_name}" if user.last_name else "")
    username = f"@{user.username}" if user.username else "None"
    mention = getattr(user, "mention", full_name)
    is_premium = getattr(user, "is_premium", False)
    is_bot = user.is_bot
    dc_id = getattr(user, "dc_id", "N/A")

    text = (
        f"{emoji} <b>{event_text}</b>\n\n"
        f"👤 <b>Name:</b> {mention}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Username:</b> {username}\n"
        f"⭐ <b>Premium:</b> {'Yes' if is_premium else 'No'}\n"
        f"🤖 <b>Bot:</b> {'Yes' if is_bot else 'No'}\n"
        f"📡 <b>DC ID:</b> {dc_id}"
    )

    try:
        await client.send_message(chat_id, text)
    except Exception:
        pass


def _register_handlers(pytg: PyTgCalls, client):

    @pytg.on_update(fl.stream_end())
    async def _on_stream_end(_: PyTgCalls, update: StreamEnded):
        chat_id = update.chat_id
        queue = get_queue(client, chat_id)
        current = get_current(client)

        current.pop(chat_id, None)

        if queue:
            next_track = queue.pop(0)
            current[chat_id] = next_track
            try:
                await play_track(
                    client,
                    chat_id,
                    next_track["stream_url"],
                    video=next_track.get("video", False),
                )
                try:
                    await client.send_message(
                        chat_id,
                        f"⏭ Now playing: <b>{next_track['title']}</b>",
                    )
                except Exception:
                    pass
            except Exception as e:
                current.pop(chat_id, None)
                await stop_stream(client, chat_id)
                try:
                    await client.send_message(
                        chat_id, f"❌ Failed to play next: `{e}`"
                    )
                except Exception:
                    pass
        else:
            await stop_stream(client, chat_id)
            try:
                await client.send_message(
                    chat_id, "⏹ Queue finished. Left the voice chat."
                )
            except Exception:
                pass

    @pytg.on_update(fl.call_participant(GroupCallParticipant.Action.JOINED))
    async def _on_join(_: PyTgCalls, update: UpdatedGroupCallParticipant):
        await _send_vc_user_info(client, update, is_join=True)

    @pytg.on_update(fl.call_participant(GroupCallParticipant.Action.LEFT))
    async def _on_leave(_: PyTgCalls, update: UpdatedGroupCallParticipant):
        await _send_vc_user_info(client, update, is_join=False)


async def ensure_started(client):
    call_client = _resolve_call_client(client)
    key = id(call_client)
    if not _STARTED.get(key):
        await get_pytgcalls(client).start()
        _STARTED[key] = True


def get_queue(client, chat_id: int) -> list:
    key = id(_resolve_call_client(client))
    return _QUEUES.setdefault(key, {}).setdefault(chat_id, [])


def get_current(client) -> dict:
    key = id(_resolve_call_client(client))
    return _CURRENT.setdefault(key, {})


async def play_track(client, chat_id: int, stream_url: str, video: bool = False):
    await ensure_started(client)
    pytgcalls = get_pytgcalls(client)

    if video:
        stream = MediaStream(
            stream_url,
            audio_parameters=AudioQuality.STUDIO,
            video_parameters=VideoQuality.SD_480p,
        )
    else:
        stream = MediaStream(
            stream_url,
            audio_parameters=AudioQuality.STUDIO,
            video_flags=MediaStream.Flags.IGNORE,
        )
    await pytgcalls.play(chat_id, stream)


async def stop_stream(client, chat_id: int):
    key = id(_resolve_call_client(client))
    _QUEUES.get(key, {}).pop(chat_id, None)
    _CURRENT.get(key, {}).pop(chat_id, None)
    try:
        await get_pytgcalls(client).leave_call(chat_id)
    except Exception:
        pass


async def pause_stream(client, chat_id: int):
    await get_pytgcalls(client).pause(chat_id)


async def resume_stream(client, chat_id: int):
    await get_pytgcalls(client).resume(chat_id)


async def mute_stream(client, chat_id: int):
    await get_pytgcalls(client).mute(chat_id)


async def unmute_stream(client, chat_id: int):
    await get_pytgcalls(client).unmute(chat_id)
