"""
Protect Content (userbot)

  .protect on|off|status
  reply + .protect / .pcopy / .pfile  → protected copy
  .psend <text>                       → protected text

protect_content=True → forward/save/copy restrict (Telegram client support).
"""
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only
from database.mongo import set_feature, get_feature


async def _copy_protected(client, message: Message, src: Message):
    try:
        await src.copy(message.chat.id, protect_content=True)
        try:
            await message.delete()
        except Exception:
            pass
        return True
    except Exception as e:
        await message.reply_text(f"❌ Protect fail: <code>{e}</code>")
        return False


@app.on_message(ub_cmd("protect"))
@sudo_only
async def protect_cmd(client, message: Message):
    parts = (message.text or "").split()

    # on / off / status
    if len(parts) > 1 and parts[1].lower() in (
        "on", "off", "1", "0", "enable", "disable", "status",
    ):
        arg = parts[1].lower()
        if arg == "status":
            on = await get_feature("protect_content", False)
            await message.reply_text(
                f"╔══ 🛡 <b>PROTECT</b> ══╗\n"
                f"Flag: <b>{'ON ✅' if on else 'OFF ❌'}</b>\n\n"
                f"<code>.protect on|off</code>\n"
                f"Reply + <code>.protect</code>\n"
                f"<code>.psend text</code>\n"
                f"Reply + <code>.pfile</code>\n"
                f"╚══════════════╝"
            )
            return
        enable = arg in ("on", "1", "enable")
        await set_feature("protect_content", enable)
        await message.reply_text(
            f"{'✅' if enable else '❌'} Protect flag <b>{'ON' if enable else 'OFF'}</b>\n"
            f"Send: reply <code>.protect</code> | <code>.psend text</code>"
        )
        return

    # reply → protected copy
    if message.reply_to_message:
        await _copy_protected(client, message, message.reply_to_message)
        return

    on = await get_feature("protect_content", False)
    await message.reply_text(
        f"╔══ 🛡 <b>PROTECT CONTENT</b> ══╗\n\n"
        f"Flag: <b>{'ON' if on else 'OFF'}</b>\n\n"
        f"• <code>.protect on|off|status</code>\n"
        f"• Reply + <code>.protect</code> — protected copy\n"
        f"• Reply + <code>.pcopy</code> / <code>.pfile</code>\n"
        f"• <code>.psend your text</code>\n\n"
        f"<i>Protected = save/forward limit (client dependent)</i>\n"
        f"╚════════════════╝"
    )


@app.on_message(ub_cmd("psend", "ptext"))
@sudo_only
async def psend_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("Usage: <code>.psend your text here</code>")
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
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(ub_cmd("pfile", "pcopy", "pmedia"))
@sudo_only
async def pfile_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        await message.reply_text("Reply to media/msg + <code>.pfile</code>")
        return
    await _copy_protected(client, message, r)
