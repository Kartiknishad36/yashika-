"""
PyTgCalls on main userbot account only.
"""
from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, StreamEnded

from core.clients import app

_pytg: PyTgCalls | None = None
_started = False
_QUEUES: dict[int, list[dict]] = {}
_CURRENT: dict[int, dict] = {}


def get_pytgcalls(client=None) -> PyTgCalls:
    global _pytg
    if _pytg is None:
        _pytg = PyTgCalls(app)
        _register_handlers(_pytg)
    return _pytg


def _register_handlers(pytg: PyTgCalls):
    @pytg.on_update(fl.stream_end())
    async def _on_stream_end(_: PyTgCalls, update: StreamEnded):
        chat_id = update.chat_id
        queue = _QUEUES.setdefault(chat_id, [])
        _CURRENT.pop(chat_id, None)

        if queue:
            next_track = queue.pop(0)
            _CURRENT[chat_id] = next_track
            try:
                await play_track(
                    app,
                    chat_id,
                    next_track["stream_url"],
                    video=next_track.get("video", False),
                )
                try:
                    await app.send_message(
                        chat_id, f"⏭ Now playing: <b>{next_track['title']}</b>"
                    )
                except Exception:
                    pass
            except Exception as e:
                _CURRENT.pop(chat_id, None)
                await stop_stream(app, chat_id)
                try:
                    await app.send_message(chat_id, f"❌ Next failed: `{e}`")
                except Exception:
                    pass
        else:
            await stop_stream(app, chat_id)
            try:
                await app.send_message(chat_id, "⏹ Queue finished.")
            except Exception:
                pass


async def ensure_started(client=None):
    global _started
    if not _started:
        await get_pytgcalls().start()
        _started = True


def get_queue(client, chat_id: int) -> list:
    return _QUEUES.setdefault(chat_id, [])


def get_current(client) -> dict:
    return _CURRENT


async def play_track(client, chat_id: int, stream_url: str, video: bool = False):
    await ensure_started()
    pytgcalls = get_pytgcalls()

    if video:
        stream = MediaStream(
            stream_url,
            audio_parameters=AudioQuality.HIGH,
            video_parameters=VideoQuality.SD_480p,
        )
    else:
        stream = MediaStream(
            stream_url,
            audio_parameters=AudioQuality.HIGH,
            video_flags=MediaStream.Flags.IGNORE,
        )
    await pytgcalls.play(chat_id, stream)


async def stop_stream(client, chat_id: int):
    _QUEUES.pop(chat_id, None)
    _CURRENT.pop(chat_id, None)
    try:
        await get_pytgcalls().leave_call(chat_id)
    except Exception:
        pass


async def pause_stream(client, chat_id: int):
    await get_pytgcalls().pause(chat_id)


async def resume_stream(client, chat_id: int):
    await get_pytgcalls().resume(chat_id)


async def mute_stream(client, chat_id: int):
    await get_pytgcalls().mute(chat_id)


async def unmute_stream(client, chat_id: int):
    await get_pytgcalls().unmute(chat_id)
