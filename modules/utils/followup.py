import asyncio
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!"]
_SCHEDULED = set()

@app.on_message(filters.command("followup", prefixes=PREFIXES))
@sudo_only
async def followup_cmd(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("followup", False)
        txt = await get_feature("followup_text", "Follow-up: baat karni thi 🙂")
        hrs = await get_feature("followup_hours", 24)
        return await message.reply_text(
            f"FollowUp: **{'ON' if on else 'OFF'}** | `{hrs}`h\n`{txt}`\n"
            f"`·followup on|off`\n`·followup set text`\n`·followup hours 24`"
        )
    arg = message.command[1].lower()
    if arg in ("on", "off"):
        await set_feature("followup", arg == "on")
        return await message.reply_text(f"FollowUp {arg.upper()}")
    if arg == "set" and len(message.command) > 2:
        await set_feature("followup_text", message.text.split(None, 2)[2][:500])
        return await message.reply_text("✅ Text set")
    if arg == "hours" and len(message.command) > 2:
        await set_feature("followup_hours", max(1, int(message.command[2])))
        return await message.reply_text("✅ Hours set")

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot, group=17)
async def followup_watch(client, message: Message):
    if not await get_feature("followup", False) or not message.from_user:
        return
    uid = message.from_user.id
    if uid in _SCHEDULED:
        return
    _SCHEDULED.add(uid)
    hrs = int(await get_feature("followup_hours", 24) or 24)
    text = await get_feature("followup_text", "Follow-up: baat karni thi 🙂")

    async def _job():
        await asyncio.sleep(hrs * 3600)
        try:
            await client.send_message(uid, text)
        except Exception:
            pass
        _SCHEDULED.discard(uid)

    asyncio.create_task(_job())
