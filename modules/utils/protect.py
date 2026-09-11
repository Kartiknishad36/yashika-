"""
Protect Content (userbot):
  .protect on|off     — mode flag (status)
  .protect            — reply to msg: us copy ko protect_content=True se bhejo
  .psend <text>       — naya text protected bhejo

Protected = forward / save / copy restrict (client support ke hisaab se).
"""
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!"]


@app.on_message(filters.command(["protect"], prefixes=PREFIXES))
@sudo_only
async def protect_cmd(client, message: Message):
    # .protect on|off
    if len(message.command) > 1 and message.command[1].lower() in (
        "on", "off", "1", "0", "enable", "disable", "status",
    ):
        arg = message.command[1].lower()
        if arg in ("status",):
            on = await get_feature("protect_content", False)
            await message.reply_text(
                f"Protect mode flag: **{'ON' if on else 'OFF'}**\n"
                f"Use reply + `.protect` or `.psend` to send protected."
            )
            return
        enable = arg in ("on", "1", "enable")
        await set_feature("protect_content", enable)
        await message.reply_text(
            f"{'✅' if enable else '❌'} Protect flag **{'ON' if enable else 'OFF'}**.\n"
            f"Protected msg: reply `.protect` | `.psend text`"
        )
        return

    # reply → copy protected
    if message.reply_to_message:
        try:
            await message.reply_to_message.copy(
                message.chat.id,
                protect_content=True,
            )
            try:
                await message.delete()
            except Exception:
                pass
        except Exception as e:
            await message.reply_text(f"❌ Protect copy fail: `{e}`")
        return

    await message.reply_text(
        "Usage:\n"
        "`.protect on|off` — flag\n"
        "Reply + `.protect` — protected copy\n"
        "`.psend hello` — protected text"
    )


@app.on_message(filters.command(["psend"], prefixes=PREFIXES))
@sudo_only
async def psend_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("Usage: `.psend your text`")
        return
    text = parts[1]
    try:
        await client.send_message(
            message.chat.id,
            text,
            protect_content=True,
        )
        try:
            await message.delete()
        except Exception:
            pass
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@app.on_message(filters.command(["pfile"], prefixes=PREFIXES))
@sudo_only
async def pfile_cmd(client, message: Message):
    """Reply to photo/video/doc → re-send protected."""
    r = message.reply_to_message
    if not r:
        await message.reply_text("Reply to a media with `.pfile`")
        return
    try:
        await r.copy(message.chat.id, protect_content=True)
        try:
            await message.delete()
        except Exception:
            pass
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")
