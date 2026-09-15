from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]

@app.on_message(filters.command("autokick", prefixes=PREFIXES) & filters.group)
@sudo_only
async def autokick_cmd(client, message: Message):
    cid = message.chat.id
    if len(message.command) < 2:
        on = await get_chat_flag(cid, "autokick", False)
        words = await get_chat_flag(cid, "autokick_words", []) or []
        return await message.reply_text(
            f"Autokick: **{'ON' if on else 'OFF'}**\nWords: `{', '.join(words) or '—'}`\n"
            f"`·autokick on|off|list`\n`·autokick add word`\n`·autokick del word`"
        )
    arg = message.command[1].lower()
    words = list(await get_chat_flag(cid, "autokick_words", []) or [])
    if arg in ("on", "off"):
        await set_chat_flag(cid, "autokick", arg == "on")
        return await message.reply_text(f"Autokick {arg.upper()}")
    if arg == "list":
        return await message.reply_text("Words:\n" + ("\n".join(f"• {w}" for w in words) or "—"))
    if arg == "add" and len(message.command) > 2:
        w = message.command[2].lower()
        if w not in words:
            words.append(w)
        await set_chat_flag(cid, "autokick_words", words)
        return await message.reply_text(f"✅ Added `{w}`")
    if arg == "del" and len(message.command) > 2:
        w = message.command[2].lower()
        words = [x for x in words if x != w]
        await set_chat_flag(cid, "autokick_words", words)
        return await message.reply_text(f"✅ Removed `{w}`")

@app.on_message(filters.group & filters.incoming & filters.text & ~filters.me, group=6)
async def autokick_watch(client, message: Message):
    if not message.from_user or not message.text:
        return
    cid = message.chat.id
    if not await get_chat_flag(cid, "autokick", False):
        return
    words = await get_chat_flag(cid, "autokick_words", []) or []
    low = message.text.lower()
    if not any(w in low for w in words):
        return
    try:
        await message.delete()
        await client.ban_chat_member(cid, message.from_user.id)
        await client.unban_chat_member(cid, message.from_user.id)
        await client.send_message(cid, f"👢 Autokick: {message.from_user.mention}")
    except Exception:
        pass
