import os
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import get_all_chats

PREFIXES = [".", "!"]
OUT = "downloads"
os.makedirs(OUT, exist_ok=True)

@app.on_message(filters.command("idbackup", prefixes=PREFIXES))
@sudo_only
async def idbackup_cmd(client, message: Message):
    try:
        chats = await get_all_chats() or []
    except Exception:
        chats = []
    path = os.path.join(OUT, "chat_ids_backup.txt")
    with open(path, "w", encoding="utf-8") as f:
        for cid in chats:
            f.write(f"{cid}\n")
    await message.reply_document(path, caption=f"💾 IDs: `{len(chats)}`")
    try:
        os.remove(path)
    except Exception:
        pass
