"""
.welcome on/off
.setwelcome <text> — {name} {mention} {chat} {id}
"""
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from database.mongo import (
    set_welcome_enabled, get_welcome_enabled,
    set_welcome_text, get_welcome_text,
)
from modules.owner.sudoers import ub_cmd, sudo_only


def _format(text: str, chat_title: str, user) -> str:
    mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
    return (
        text.replace("{name}", user.first_name or "")
        .replace("{mention}", mention)
        .replace("{chat}", chat_title)
        .replace("{id}", str(user.id))
    )


@app.on_message(ub_cmd("welcome"))
@sudo_only
async def welcome_toggle_cmd(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) < 2 or parts[1].lower() not in ("on", "off"):
        current = await get_welcome_enabled(message.chat.id)
        await message.reply_text(
            f"Usage: <code>.welcome on</code> / <code>.welcome off</code>\n"
            f"Currently: <b>{'ON' if current else 'OFF'}</b>"
        )
        return
    enabled = parts[1].lower() == "on"
    await set_welcome_enabled(message.chat.id, enabled)
    await message.reply_text(f"Welcome <b>{'ON' if enabled else 'OFF'}</b>")


@app.on_message(ub_cmd("setwelcome"))
@sudo_only
async def setwelcome_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        current = await get_welcome_text(message.chat.id)
        await message.reply_text(
            "Usage: <code>.setwelcome text</code>\n"
            "Placeholders: {name} {mention} {chat} {id}\n\n"
            f"Current:\n{current}"
        )
        return
    await set_welcome_text(message.chat.id, parts[1])
    await message.reply_text("Welcome message updated.")


@app.on_message(filters.new_chat_members)
async def new_member_welcome(client, message: Message):
    chat_id = message.chat.id
    if not await get_welcome_enabled(chat_id):
        return
    text_template = await get_welcome_text(chat_id)
    chat_title = message.chat.title or "the group"
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        text = _format(text_template, chat_title, user)
        try:
            await client.send_message(chat_id, text)
        except Exception:
            pass
