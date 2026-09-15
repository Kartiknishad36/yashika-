import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
AUTOBIO_ON = False
INTERVAL = 30
TEMPLATE = "⚡ {name} | {time} | {date}"
_TASK = None

def _render(name: str) -> str:
    now = datetime.now()
    return (
        TEMPLATE.replace("{name}", name)
        .replace("{time}", now.strftime("%I:%M %p"))
        .replace("{date}", now.strftime("%d %b"))
        .replace("{day}", now.strftime("%A"))
    )[:70]

async def _loop(client):
    global AUTOBIO_ON
    while AUTOBIO_ON:
        try:
            me = await client.get_chat("me")
            name = (me.first_name or "User").split("|")[0].strip()
            await client.update_profile(bio=_render(name))
        except Exception as e:
            print(f"[AutoBio] {e}")
        await asyncio.sleep(max(30, INTERVAL))

@app.on_message(filters.command("autobio", prefixes=PREFIXES))
@sudo_only
async def autobio_cmd(client, message: Message):
    global AUTOBIO_ON, INTERVAL, TEMPLATE, _TASK
    if len(message.command) < 2:
        return await message.reply_text(
            f"AutoBio: **{'ON' if AUTOBIO_ON else 'OFF'}** | `{INTERVAL}s`\n`{TEMPLATE}`\n"
            f"`·autobio on|off|now`\n`·autobio time 30`\n`·autobio set text {{name}} {{time}}`"
        )
    arg = message.command[1].lower()
    if arg in ("on", "1"):
        AUTOBIO_ON = True
        if not _TASK or _TASK.done():
            _TASK = asyncio.create_task(_loop(client))
        return await message.reply_text("✅ AutoBio ON")
    if arg in ("off", "0"):
        AUTOBIO_ON = False
        if _TASK and not _TASK.done():
            _TASK.cancel()
        return await message.reply_text("❌ AutoBio OFF")
    if arg == "time" and len(message.command) > 2:
        INTERVAL = max(30, int(message.command[2]))
        return await message.reply_text(f"Interval `{INTERVAL}s`")
    if arg == "set" and len(message.command) > 2:
        TEMPLATE = message.text.split(None, 2)[2][:70]
        return await message.reply_text(f"Template: `{TEMPLATE}`")
    if arg == "now":
        me = await client.get_chat("me")
        name = (me.first_name or "User").split("|")[0].strip()
        bio = _render(name)
        await client.update_profile(bio=bio)
        return await message.reply_text(f"✅ `{bio}`")
