"""
.filter add hello | Hi there {mention}!
.filter del hello
.filters
"""
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]


async def _get_map(chat_id: int) -> dict:
    data = await get_chat_flag(chat_id, "word_filters", {}) or {}
    if not isinstance(data, dict):
        return {}
    return data


@app.on_message(filters.command(["filter", "filters"], prefixes=PREFIXES) & filters.group)
@sudo_only
async def filter_cmd(client, message: Message):
    chat_id = message.chat.id
    cmd0 = message.command[0].lower()

    if cmd0 == "filters" or len(message.command) < 2:
        mp = await _get_map(chat_id)
        if not mp:
            await message.reply_text("No filters.\n<code>.filter add hi | Hello!</code>")
            return
        lines = [f"• <code>{k}</code> → {v[:40]}" for k, v in mp.items()]
        await message.reply_text("🔤 <b>Filters</b>\n" + "\n".join(lines))
        return

    sub = message.command[1].lower()
    mp = await _get_map(chat_id)

    if sub in ("add", "set"):
        raw = message.text.split(None, 2)
        if len(raw) < 3 or "|" not in raw[2]:
            await message.reply_text("Usage: <code>.filter add keyword | reply text</code>")
            return
        key, reply = raw[2].split("|", 1)
        key, reply = key.strip().lower(), reply.strip()
        mp[key] = reply
        await set_chat_flag(chat_id, "word_filters", mp)
        await message.reply_text(f"✅ Filter <code>{key}</code>")
        return

    if sub in ("del", "remove", "rm"):
        if len(message.command) < 3:
            await message.reply_text("Usage: <code>.filter del keyword</code>")
            return
        key = message.command[2].lower()
        mp.pop(key, None)
        await set_chat_flag(chat_id, "word_filters", mp)
        await message.reply_text(f"✅ Removed <code>{key}</code>")
        return

    await message.reply_text("Usage: add / del / .filters")


@app.on_message(filters.group & filters.incoming & filters.text & \~filters.me, group=9)
async def filter_watch(client, message: Message):
    if not message.text or not message.from_user:
        return
    mp = await _get_map(message.chat.id)
    if not mp:
        return
    low = message.text.lower()
    for key, reply in mp.items():
        if key in low:
            text = reply.replace(
                "{mention}",
                message.from_user.mention if message.from_user else "",
            )
            try:
                await message.reply_text(text)
            except Exception:
                pass
            return
