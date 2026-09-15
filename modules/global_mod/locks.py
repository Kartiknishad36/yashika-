"""
.lock all|media|sticker|link|gif|forward
.unlock same
.lock status
"""
from pyrogram import filters
from pyrogram.types import Message, ChatPermissions

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]

LOCK_KEYS = {
    "media": "lock_media",
    "sticker": "lock_sticker",
    "link": "lock_link",
    "gif": "lock_gif",
    "forward": "lock_forward",
    "all": "lock_all",
}


@app.on_message(filters.command(["lock", "unlock"], prefixes=PREFIXES) & filters.group)
@sudo_only
async def lock_cmd(client, message: Message):
    chat_id = message.chat.id
    action = message.command[0].lower()  # lock / unlock
    if len(message.command) < 2:
        lines = []
        for name, key in LOCK_KEYS.items():
            on = await get_chat_flag(chat_id, key, False)
            lines.append(f"• {name}: <b>{'ON' if on else 'OFF'}</b>")
        await message.reply_text(
            "🔒 <b>Locks</b>\n" + "\n".join(lines) + "\n\n"
            "<code>.lock media|sticker|link|gif|forward|all</code>\n"
            "<code>.unlock …</code>"
        )
        return

    what = message.command[1].lower()
    if what not in LOCK_KEYS:
        await message.reply_text("Unknown lock type.")
        return

    val = action == "lock"
    if what == "all":
        for k in LOCK_KEYS.values():
            await set_chat_flag(chat_id, k, val)
    else:
        await set_chat_flag(chat_id, LOCK_KEYS[what], val)

    await message.reply_text(f"{'🔒' if val else '🔓'} <b>{what}</b> {'locked' if val else 'unlocked'}")


@app.on_message(filters.group & filters.incoming & ~filters.me & ~filters.service, group=7)
async def lock_watch(client, message: Message):
    if not message.from_user:
        return
    chat_id = message.chat.id

    if await get_chat_flag(chat_id, "lock_all", False):
        try:
            await message.delete()
        except Exception:
            pass
        return

    if await get_chat_flag(chat_id, "lock_media", False) and (
        message.photo or message.video or message.document or message.audio or message.voice
    ):
        try:
            await message.delete()
        except Exception:
            pass
        return

    if await get_chat_flag(chat_id, "lock_sticker", False) and message.sticker:
        try:
            await message.delete()
        except Exception:
            pass
        return

    if await get_chat_flag(chat_id, "lock_gif", False) and message.animation:
        try:
            await message.delete()
        except Exception:
            pass
        return

    if await get_chat_flag(chat_id, "lock_forward", False) and message.forward_date:
        try:
            await message.delete()
        except Exception:
            pass
        return

    if await get_chat_flag(chat_id, "lock_link", False) and message.text:
        t = message.text.lower()
        if "http://" in t or "https://" in t or "t.me/" in t:
            try:
                await message.delete()
            except Exception:
                pass
