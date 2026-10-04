"""
Auto-reply — per chat only.

  .autoreply on     → is DM/group me ON
  .autoreply off    → is chat me OFF
  .autoreply set <text>
  .autoreply        → status is chat ka
"""
import time

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import get_chat_flag, set_chat_flag

PREFIXES = [".", "!"]
DEFAULT_TEXT = "I am busy right now, will reply later."
COOLDOWN = 20
_LAST: dict[tuple[int, int], float] = {}


@app.on_message(filters.command("autoreply", prefixes=PREFIXES))
@sudo_only
async def autoreply_cmd(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = bool(await get_chat_flag(chat_id, "autoreply", False))
        text = await get_chat_flag(chat_id, "autoreply_text", DEFAULT_TEXT)
        await message.reply_text(
            f"**AutoReply** this chat: **{'ON' if on else 'OFF'}**\n"
            f"Text: `{text}`\n\n"
            f"`.autoreply on` / `.autoreply off`\n"
            f"`.autoreply set your message`"
        )
        return

    arg = message.command[1].lower()
    if arg in ("on", "enable", "1"):
        await set_chat_flag(chat_id, "autoreply", True)
        await message.reply_text("**AutoReply ON** — only this chat.")
        return
    if arg in ("off", "disable", "0"):
        await set_chat_flag(chat_id, "autoreply", False)
        await message.reply_text("**AutoReply OFF** — this chat.")
        return
    if arg == "set" and len(message.command) > 2:
        text = message.text.split(None, 2)[2][:500]
        await set_chat_flag(chat_id, "autoreply_text", text)
        await set_chat_flag(chat_id, "autoreply", True)
        await message.reply_text(f"Saved + ON:\n`{text}`")
        return

    await message.reply_text("Usage: `.autoreply on|off|set <text>`")


@app.on_message(
    filters.incoming & ~filters.me & ~filters.bot & ~filters.service,
    group=17,
)
async def auto_replier(client, message: Message):
    if not message.chat or not message.from_user:
        return
    chat_id = message.chat.id
    try:
        on = bool(await get_chat_flag(chat_id, "autoreply", False))
    except Exception:
        return
    if not on:
        return

    text0 = message.text or message.caption or ""
    if text0.startswith((".", "!", "/")):
        return

    uid = message.from_user.id
    key = (chat_id, uid)
    now = time.time()
    if now - _LAST.get(key, 0) < COOLDOWN:
        return
    _LAST[key] = now

    try:
        reply_text = await get_chat_flag(chat_id, "autoreply_text", DEFAULT_TEXT)
        await message.reply_text(str(reply_text or DEFAULT_TEXT))
    except Exception:
        pass
