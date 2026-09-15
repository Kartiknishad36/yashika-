import time
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
AUTOREPLY_ON = False
REPLY_TEXT = "I am busy right now, will reply later ❤️"
REPLY_USERS = set()
COOLDOWN = 30
_LAST = {}

@app.on_message(filters.command("autoreply", prefixes=PREFIXES))
@sudo_only
async def autoreply_cmd(client, message: Message):
    global AUTOREPLY_ON, REPLY_TEXT, COOLDOWN
    if len(message.command) < 2:
        return await message.reply_text(
            f"AutoReply: **{'ON' if AUTOREPLY_ON else 'OFF'}**\n`{REPLY_TEXT}`\n"
            f"`·autoreply on|off`\n`·autoreply set text`\n`·autoreply cooldown 30`"
        )
    arg = message.command[1].lower()
    if arg in ("on", "off"):
        AUTOREPLY_ON = arg == "on"
        return await message.reply_text(f"AutoReply {arg.upper()}")
    if arg == "set" and len(message.command) > 2:
        REPLY_TEXT = message.text.split(None, 2)[2][:500]
        AUTOREPLY_ON = True
        return await message.reply_text(f"✅ `{REPLY_TEXT}`")
    if arg == "cooldown" and len(message.command) > 2:
        COOLDOWN = max(5, int(message.command[2]))
        return await message.reply_text(f"Cooldown `{COOLDOWN}s`")

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot & ~filters.service, group=17)
async def auto_replier(client, message: Message):
    if not AUTOREPLY_ON or not message.from_user:
        return
    uid = message.from_user.id
    if REPLY_USERS and uid not in REPLY_USERS:
        return
    text = message.text or message.caption or ""
    if text.startswith((".", "!", "/")):
        return
    now = time.time()
    if now - _LAST.get(uid, 0) < COOLDOWN:
        return
    _LAST[uid] = now
    try:
        await message.reply_text(REPLY_TEXT)
    except Exception:
        pass
