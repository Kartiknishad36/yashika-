"""
Anti-Delete / Ghost (group):
  Koi message delete kare → bot bata de (cached text/media type).

  .antidelete on|off
  .antidelete status

Userbot ko messages history dikhni chahiye; cache recent msgs in-memory.
"""
import time
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]

# (chat_id, msg_id) -> info
_CACHE: dict[tuple[int, int], dict] = {}
_CACHE_MAX = 3000


def cmd(name):
    return filters.command(name, prefixes=PREFIXES) & filters.group


def _kind(message: Message) -> str:
    if message.text:
        return "text"
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.voice:
        return "voice"
    if message.video_note:
        return "video_note"
    if message.sticker:
        return "sticker"
    if message.document:
        return "document"
    if message.animation:
        return "gif"
    if message.audio:
        return "audio"
    return "other"


@app.on_message(cmd("antidelete"))
@sudo_only
async def antidelete_toggle(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await get_chat_flag(chat_id, "antidelete", False)
        await message.reply_text(
            f"Anti-Delete is **{'ON' if on else 'OFF'}** here.\n"
            f"`.antidelete on` | `.antidelete off`"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_chat_flag(chat_id, "antidelete", True)
        await message.reply_text(
            "✅ Anti-Delete **ON** — deleted msgs ka alert aayega."
        )
    elif arg in ("off", "0", "disable"):
        await set_chat_flag(chat_id, "antidelete", False)
        await message.reply_text("❌ Anti-Delete **OFF**.")
    elif arg in ("status", "stat"):
        on = await get_chat_flag(chat_id, "antidelete", False)
        await message.reply_text(f"Anti-Delete: **{'ON' if on else 'OFF'}**")
    else:
        await message.reply_text("Usage: `.antidelete on|off|status`")


# Cache group messages (only if feature might be used — always light cache)
@app.on_message(filters.group & filters.incoming & \~filters.service, group=6)
async def antidelete_cache(client, message: Message):
    if not message.from_user:
        return
    # only cache if enabled (saves RAM)
    if not await get_chat_flag(message.chat.id, "antidelete", False):
        return

    body = message.text or message.caption or ""
    key = (message.chat.id, message.id)
    _CACHE[key] = {
        "user_id": message.from_user.id,
        "name": message.from_user.first_name or "?",
        "username": message.from_user.username or "",
        "kind": _kind(message),
        "body": body[:800],
        "time": time.time(),
    }
    if len(_CACHE) > _CACHE_MAX:
        # drop oldest keys
        for k in list(_CACHE.keys())[: len(_CACHE) - _CACHE_MAX]:
            _CACHE.pop(k, None)


@app.on_deleted_messages(filters.group)
async def antidelete_alert(client, messages):
    for msg in messages:
        if not msg or not msg.chat:
            continue
        chat_id = msg.chat.id
        if not await get_chat_flag(chat_id, "antidelete", False):
            continue

        key = (chat_id, msg.id)
        info = _CACHE.pop(key, None)

        if info:
            uname = f"@{info['username']}" if info["username"] else "—"
            text = (
                f"👻 <b>MESSAGE DELETED</b>\n\n"
                f"User: <b>{info['name']}</b> ({uname})\n"
                f"ID: <code>{info['user_id']}</code>\n"
                f"Type: <code>{info['kind']}</code>\n"
                f"Content:\n<code>{info['body'] or '—'}</code>"
            )
        else:
            text = (
                f"👻 <b>MESSAGE DELETED</b>\n\n"
                f"Msg id: <code>{msg.id}</code>\n"
                f"(cache miss — bot ne pehle nahi dekha)"
            )

        try:
            await client.send_message(chat_id, text)
        except Exception:
            pass
