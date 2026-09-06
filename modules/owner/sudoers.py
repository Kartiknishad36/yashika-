"""
Auth decorators.

sudo_only:
  - client ka khud ka account (me.id)  → commands chale
  - ya config OWNER_ID                 → owner hamesha control kar sake
  - baaki users                        → silent ignore (no reply)

owner_only:
  - sirf OWNER_ID (addsudo / delsudo etc.)

Multi-login: har clone client apna me.id check karta hai.
"""
import functools
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID
from database.mongo import add_sudo, remove_sudo, get_sudoers

SUDO_USERS: set[int] = {OWNER_ID}


async def load_sudoers():
    SUDO_USERS.clear()
    SUDO_USERS.add(OWNER_ID)
    for uid in await get_sudoers():
        SUDO_USERS.add(uid)


def sudo_only(func):
    """
    Allow:
      1) message.from_user.id == client.get_me().id
      2) message.from_user.id == OWNER_ID
    Else silent return.
    """
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user:
            return
        uid = message.from_user.id
        try:
            me = await client.get_me()
        except Exception:
            return
        if uid != me.id and uid != OWNER_ID:
            return
        return await func(client, message, *args, **kwargs)
    return wrapper


def owner_only(func):
    """Sirf .env wala OWNER_ID."""
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user or message.from_user.id != OWNER_ID:
            return
        return await func(client, message, *args, **kwargs)
    return wrapper


@app.on_message(filters.command("addsudo", prefixes=[".", "!"]))
@owner_only
async def addsudo_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("Reply to a user or give ID: `.addsudo <id>`")
        return
    target = (
        message.reply_to_message.from_user.id
        if message.reply_to_message
        else int(message.command[1])
    )
    await add_sudo(target)
    SUDO_USERS.add(target)
    await message.reply_text(f"✅ Added `{target}` to sudo list.")


@app.on_message(filters.command("delsudo", prefixes=[".", "!"]))
@owner_only
async def delsudo_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("Reply to a user or give ID: `.delsudo <id>`")
        return
    target = (
        message.reply_to_message.from_user.id
        if message.reply_to_message
        else int(message.command[1])
    )
    await remove_sudo(target)
    SUDO_USERS.discard(target)
    await message.reply_text(f"✅ Removed `{target}` from sudo list.")


@app.on_message(filters.command("sudolist", prefixes=[".", "!"]))
@owner_only
async def sudolist_cmd(client, message: Message):
    text = (
        "👑 <b>Sudo list</b>\n\n"
        + "\n".join(f"• <code>{uid}</code>" for uid in sorted(SUDO_USERS))
        + "\n\nCommands: account (`me.id`) ya OWNER_ID."
    )
    await message.reply_text(text)
