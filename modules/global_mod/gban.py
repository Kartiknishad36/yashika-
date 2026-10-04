from pyrogram.types import Message
from pyrogram.errors import RPCError

from core.clients import app
from database.mongo import gban_user, ungban_user, get_gban_list, get_all_chats
from modules.owner.sudoers import ub_cmd, sudo_only


def _target_reason(message: Message):
    parts = (message.text or "").split()
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
        reason = " ".join(parts[1:]) if len(parts) > 1 else "No reason"
        return target, reason
    if len(parts) > 1 and parts[1].lstrip("-").isdigit():
        target = int(parts[1])
        reason = " ".join(parts[2:]) or "No reason"
        return target, reason
    return None, None


@app.on_message(ub_cmd("gban"))
@sudo_only
async def gban_cmd(client, message: Message):
    target, reason = _target_reason(message)
    if not target:
        await message.reply_text("Reply or <code>.gban id [reason]</code>")
        return
    await gban_user(target, reason)
    status = await message.reply_text(f"Globally banning <code>{target}</code>…")
    chats = await get_all_chats()
    banned_in = 0
    for chat_id in chats:
        try:
            await client.ban_chat_member(chat_id, target)
            banned_in += 1
        except RPCError:
            continue
    await status.edit_text(
        f"Gbanned <code>{target}</code> in <b>{banned_in}</b> chat(s).\nReason: {reason}"
    )


@app.on_message(ub_cmd("ungban"))
@sudo_only
async def ungban_cmd(client, message: Message):
    target, _ = _target_reason(message)
    if not target:
        await message.reply_text("Reply or <code>.ungban id</code>")
        return
    await ungban_user(target)
    status = await message.reply_text(f"Removing gban <code>{target}</code>…")
    chats = await get_all_chats()
    n = 0
    for chat_id in chats:
        try:
            await client.unban_chat_member(chat_id, target)
            n += 1
        except RPCError:
            continue
    await status.edit_text(f"Ungbanned <code>{target}</code> in <b>{n}</b> chat(s).")


@app.on_message(ub_cmd("gbanlist"))
@sudo_only
async def gbanlist_cmd(client, message: Message):
    entries = await get_gban_list()
    if not entries:
        await message.reply_text("Gban list empty.")
        return
    text = "<b>Global Ban List</b>\n\n"
    for e in entries[:50]:
        text += f"• <code>{e['user_id']}</code> — {e.get('reason', '—')}\n"
    await message.reply_text(text)
