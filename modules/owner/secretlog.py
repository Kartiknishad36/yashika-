"""
Secret Logger (userbot):
  .secretlog on|off|status

- Har incoming private msg cache
- Delete hone pe LOG group / Saved Messages pe detail
- Optional: live forward to log (can flood) — default OFF, only delete log ON

Config: LOG_GROUP_ID or LOGGER_ID
"""
import time
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!"]

try:
    from config import LOG_GROUP_ID as _LOG
except ImportError:
    _LOG = None
try:
    from config import LOGGER_ID as _LOG2
except ImportError:
    _LOG2 = None

LOG_CHAT = _LOG or _LOG2

# (chat_id, msg_id) -> info
_CACHE: dict[tuple[int, int], dict] = {}
_CACHE_MAX = 800

# live forward every PM (noisy) — flag separate
LIVE_FORWARD = False


async def _log_send(client, text: str, media_msg: Message | None = None):
    targets = []
    if LOG_CHAT:
        targets.append(LOG_CHAT)
    try:
        me = await client.get_me()
        targets.append(me.id)  # Saved Messages
    except Exception:
        pass

    for tid in targets:
        try:
            if media_msg and (media_msg.photo or media_msg.video or media_msg.document
                              or media_msg.voice or media_msg.sticker or media_msg.animation):
                try:
                    await media_msg.copy(tid)
                except Exception:
                    pass
            await client.send_message(tid, text)
        except Exception:
            pass


def _kind(m: Message) -> str:
    if m.text:
        return "text"
    if m.photo:
        return "photo"
    if m.video:
        return "video"
    if m.voice:
        return "voice"
    if m.video_note:
        return "video_note"
    if m.sticker:
        return "sticker"
    if m.document:
        return "document"
    if m.animation:
        return "gif"
    if m.audio:
        return "audio"
    return "other"


@app.on_message(filters.command(["secretlog", "slog"], prefixes=PREFIXES))
@sudo_only
async def secretlog_toggle(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("secretlog", True)
        await message.reply_text(
            f"🔐 SecretLog: <b>{'ON' if on else 'OFF'}</b>\n"
            f"Log chat: <code>{LOG_CHAT or 'Saved Messages only'}</code>\n"
            f"`.secretlog on` | `.secretlog off`"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_feature("secretlog", True)
        await message.reply_text(
            "✅ <b>SecretLog ON</b>\n"
            "Private msgs cache • delete pe save hoga."
        )
    elif arg in ("off", "0", "disable"):
        await set_feature("secretlog", False)
        await message.reply_text("❌ SecretLog **OFF**.")
    elif arg in ("status",):
        on = await get_feature("secretlog", True)
        await message.reply_text(f"SecretLog: <b>{'ON' if on else 'OFF'}</b>")
    else:
        await message.reply_text("Usage: `.secretlog on|off|status`")


@app.on_message(
    filters.private & filters.incoming & \~filters.me & \~filters.bot & \~filters.service,
    group=20,
)
async def secret_logger_cache(client, message: Message):
    if not await get_feature("secretlog", True):
        return
    if not message.from_user:
        return

    uid = message.from_user.id
    body = message.text or message.caption or ""
    key = (message.chat.id, message.id)
    _CACHE[key] = {
        "user_id": uid,
        "name": message.from_user.first_name or "?",
        "username": message.from_user.username or "",
        "kind": _kind(message),
        "body": body[:1000],
        "time": time.time(),
        "chat_id": message.chat.id,
    }
    if len(_CACHE) > _CACHE_MAX:
        for k in list(_CACHE.keys())[: len(_CACHE) - _CACHE_MAX]:
            _CACHE.pop(k, None)

    # optional live forward (default off — set LIVE_FORWARD True if chahiye)
    if LIVE_FORWARD and LOG_CHAT:
        try:
            await message.forward(LOG_CHAT)
        except Exception:
            try:
                await message.copy(LOG_CHAT)
            except Exception:
                pass


@app.on_deleted_messages(filters.private)
async def secret_logger_deleted(client, messages):
    if not await get_feature("secretlog", True):
        return
    for msg in messages:
        if not msg or not msg.chat:
            continue
        key = (msg.chat.id, msg.id)
        info = _CACHE.pop(key, None)
        if not info:
            text = (
                f"🗑 <b>SECRET DELETE</b>\n"
                f"Chat: <code>{msg.chat.id}</code>\n"
                f"Msg ID: <code>{msg.id}</code>\n"
                f"(cache miss)"
            )
            await _log_send(client, text)
            continue

        uname = f"@{info['username']}" if info["username"] else "—"
        text = (
            f"🗑 <b>SECRET DELETE (PM)</b>\n\n"
            f"From: <b>{info['name']}</b> ({uname})\n"
            f"ID: <code>{info['user_id']}</code>\n"
            f"Type: <code>{info['kind']}</code>\n"
            f"Text:\n<code>{info['body'] or '—'}</code>"
        )
        await _log_send(client, text)
