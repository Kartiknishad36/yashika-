"""
Secret Logger — default OFF
  .secretlog on|off|status
"""
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

LOG_CHAT = _LOG
_CACHE: dict[tuple[int, int], dict] = {}
_CACHE_MAX = 400


async def _log_send(client, text: str):
    if not LOG_CHAT:
        print("[secretlog] LOG_GROUP_ID not set")
        return
    try:
        await client.send_message(LOG_CHAT, text)
    except Exception as e:
        print(f"[secretlog] {e}")


def _kind(m: Message) -> str:
    if m.text:
        return "text"
    if m.photo:
        return "photo"
    if m.video:
        return "video"
    if m.voice:
        return "voice"
    if m.sticker:
        return "sticker"
    return "other"


@app.on_message(filters.command(["secretlog", "slog"], prefixes=PREFIXES))
@sudo_only
async def secretlog_toggle(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("secretlog", False)
        await message.reply_text(
            f"SecretLog: <b>{'ON' if on else 'OFF'}</b>\n"
            f"<code>.secretlog on</code> | <code>.secretlog off</code>"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_feature("secretlog", True)
        await message.reply_text("<b>SecretLog ON</b>")
    elif arg in ("off", "0", "disable"):
        await set_feature("secretlog", False)
        await message.reply_text("<b>SecretLog OFF</b>")
    else:
        await message.reply_text("Usage: <code>.secretlog on|off</code>")


@app.on_message(
    filters.private & filters.incoming & ~filters.me & ~filters.bot & ~filters.service,
    group=20,
)
async def secret_logger_cache(client, message: Message):
    if not await get_feature("secretlog", False):
        return
    if not message.from_user:
        return
    body = message.text or message.caption or ""
    key = (message.chat.id, message.id)
    _CACHE[key] = {
        "user_id": message.from_user.id,
        "name": message.from_user.first_name or "?",
        "username": message.from_user.username or "",
        "kind": _kind(message),
        "body": body[:800],
    }
    if len(_CACHE) > _CACHE_MAX:
        for k in list(_CACHE.keys())[:50]:
            _CACHE.pop(k, None)


@app.on_deleted_messages(filters.private)
async def secret_logger_deleted(client, messages):
    if not await get_feature("secretlog", False):
        return
    for msg in messages:
        if not msg or not msg.chat:
            continue
        info = _CACHE.pop((msg.chat.id, msg.id), None)
        if not info:
            continue
        uname = f"@{info['username']}" if info["username"] else "—"
        await _log_send(
            client,
            f"<b>SECRET DELETE</b>\n"
            f"From: <b>{info['name']}</b> ({uname})\n"
            f"ID: <code>{info['user_id']}</code>\n"
            f"Type: <code>{info['kind']}</code>\n"
            f"<code>{info['body'] or '—'}</code>",
        )
