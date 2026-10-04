from pyrogram.types import Message
from pyrogram.errors import RPCError

from core.clients import app
from database.mongo import add_warn, get_warns, reset_warns
from modules.owner.sudoers import ub_cmd, sudo_only

MAX_WARNS = 3


def _target_from(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        return u.id, u.first_name or str(u.id)
    parts = (message.text or "").split()
    if len(parts) > 1 and parts[1].lstrip("-").isdigit():
        return int(parts[1]), parts[1]
    return None, None


@app.on_message(ub_cmd("warn"))
@sudo_only
async def warn_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.warn id [reason]</code>")
        return
    parts = (message.text or "").split()
    if message.reply_to_message:
        reason = " ".join(parts[1:]) if len(parts) > 1 else "No reason"
    else:
        reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason"

    count = await add_warn(message.chat.id, target, reason)
    if count >= MAX_WARNS:
        try:
            await client.ban_chat_member(message.chat.id, target)
            await reset_warns(message.chat.id, target)
            await message.reply_text(f"<b>{name}</b> hit {MAX_WARNS} warns → banned.")
        except RPCError as e:
            await message.reply_text(f"Warn max but ban fail: <code>{e}</code>")
        return
    await message.reply_text(
        f"Warned <b>{name}</b> ({count}/{MAX_WARNS})\nReason: {reason}"
    )


@app.on_message(ub_cmd("unwarn"))
@sudo_only
async def unwarn_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.unwarn id</code>")
        return
    warns = await get_warns(message.chat.id, target)
    if not warns:
        await message.reply_text(f"{name} has no warns.")
        return
    warns.pop()
    await reset_warns(message.chat.id, target)
    for r in warns:
        await add_warn(message.chat.id, target, r)
    await message.reply_text(f"Removed one warn from <b>{name}</b> ({len(warns)}/{MAX_WARNS})")


@app.on_message(ub_cmd("warns"))
@sudo_only
async def warns_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        target = message.from_user.id if message.from_user else 0
        name = message.from_user.first_name if message.from_user else "You"
    warns = await get_warns(message.chat.id, target)
    if not warns:
        await message.reply_text(f"<b>{name}</b> has no warns.")
        return
    text = f"<b>{name}</b> — {len(warns)}/{MAX_WARNS} warns\n\n"
    for i, r in enumerate(warns, 1):
        text += f"{i}. {r}\n"
    await message.reply_text(text)


@app.on_message(ub_cmd("resetwarns"))
@sudo_only
async def resetwarns_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.resetwarns id</code>")
        return
    await reset_warns(message.chat.id, target)
    await message.reply_text(f"Cleared warns for <b>{name}</b>.")
