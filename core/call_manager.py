"""
Per-client PyTgCalls management — every account has its OWN VC engine.

Previously there was a single global PyTgCalls instance bound to one
client (assistant or app), so music from a clone/login'd account actually
played through the ORIGINAL account's voice-chat connection. Now each
client (main app, or any account added via .login/.clone) gets its own
PyTgCalls instance, lazily created and started on first use, so every
logged-in account can independently join/play in voice chats.

Special case: the main `app` client still delegates to `assistant` (if
configured via ASSISTANT_SESSION) to avoid tying up the main account —
this matches the original design. Any OTHER client (a clone or a
.login'd account) always uses itself, since that's the whole point of
that account being logged in separately.
"""

Features added:
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

# id(client) -> PyTgCalls instance
_INSTANCES: dict[int, PyTgCalls] = {}
# id(client) -> bool, whether .start() has been called
_STARTED: dict[int, bool] = {}

# id(client) -> {chat_id: [queued track dicts]}
_QUEUES: dict[int, dict[int, list[dict]]] = {}
# id(client) -> {chat_id: currently playing track dict}
_CURRENT: dict[int, dict[int, dict]] = {}


def _resolve_call_client(client):
    """Only the main `app` delegates to `assistant` (if configured)."""
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
    """Send full user info when someone joins or leaves the VC."""
    chat_id = update.chat_id
    user_id = update.participant.user_id

    # Ignore self (bot / assistant)
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
    """Register stream_end + join/leave handlers."""

    # Auto next song / Auto leave
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

    # User JOINS VC
    @pytg.on_update(fl.call_participant(GroupCallParticipant.Action.JOINED))
    async def _on_join(_: PyTgCalls, update: UpdatedGroupCallParticipant):
        await _send_vc_user_info(client, update, is_join=True)

    # User LEAVES VC
    @pytg.on_update(fl.call_participant(GroupCallParticipant.Action.LEFT))
    async def _on_leave(_: PyTgCalls, update: UpdatedGroupCallParticipant):
        await _send_vc_user_info(client, update, is_join=False)


async def ensure_started(client):
    """Starts this client's PyTgCalls instance once, lazily on first use."""
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
    """Join / change stream in a chat's VC."""
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
