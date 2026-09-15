import time
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!"]

@app.on_message(filters.command(["leadsaver", "leads"], prefixes=PREFIXES))
@sudo_only
async def leadsaver_cmd(client, message: Message):
    if message.command[0].lower() == "leads" or (
        len(message.command) > 1 and message.command[1].lower() == "list"
    ):
        data = await get_feature("leads", []) or []
        if not data:
            return await message.reply_text("No leads.")
        lines = [
            f"• `{x.get('id')}` {x.get('name')} @{x.get('username') or '—'}"
            for x in data[-30:]
        ]
        return await message.reply_text("📋 **Leads**\n" + "\n".join(lines))
    if len(message.command) < 2:
        on = await get_feature("leadsaver", False)
        return await message.reply_text(
            f"LeadSaver: **{'ON' if on else 'OFF'}**\n`·leadsaver on|off`\n`·leads`"
        )
    arg = message.command[1].lower()
    await set_feature("leadsaver", arg in ("on", "1", "enable"))
    await message.reply_text(f"LeadSaver {'ON' if arg in ('on', '1') else 'OFF'}")

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot, group=16)
async def lead_watch(client, message: Message):
    if not await get_feature("leadsaver", False) or not message.from_user:
        return
    u = message.from_user
    data = list(await get_feature("leads", []) or [])
    data = [x for x in data if x.get("id") != u.id]
    data.append({
        "id": u.id,
        "name": u.first_name or "",
        "username": u.username or "",
        "ts": int(time.time()),
    })
    await set_feature("leads", data[-200:])
