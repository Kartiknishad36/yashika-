"""
.ghostmod on|off|status
OWNER + sudo.

ON  → account status offline (appear offline)
OFF → normal online updates again

Note: Telegram clients still control blue-ticks partially;
yeh offline status + feature flag set karta hai.
"""
from pyrogram import filters, raw
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!"]


@app.on_message(filters.command(["ghostmod", "ghost"], prefixes=PREFIXES))
@sudo_only
async def ghostmod_cmd(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("ghostmod", False)
        await message.reply_text(
            f"👻 Ghostmod: <b>{'ON' if on else 'OFF'}</b>\n"
            f"`.ghostmod on` | `.ghostmod off`"
        )
        return

    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_feature("ghostmod", True)
        try:
            await client.invoke(raw.functions.account.UpdateStatus(offline=True))
        except Exception:
            pass
        await message.reply_text(
            "👻 <b>Ghostmod ON</b>\nOffline status set."
        )
    elif arg in ("off", "0", "disable"):
        await set_feature("ghostmod", False)
        try:
            await client.invoke(raw.functions.account.UpdateStatus(offline=False))
        except Exception:
            pass
        await message.reply_text("👻 Ghostmod **OFF**.")
    elif arg in ("status",):
        on = await get_feature("ghostmod", False)
        await message.reply_text(f"Ghostmod: <b>{'ON' if on else 'OFF'}</b>")
    else:
        await message.reply_text("Usage: `.ghostmod on|off|status`")
