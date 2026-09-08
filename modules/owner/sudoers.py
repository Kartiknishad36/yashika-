"""
Auth decorators.

sudo_only:
  - client me.id  (apna userbot account)
  - OWNER_ID
  - SUDO_USERS list
  → silent ignore baaki

owner_or_sudo:
  - OWNER_ID ya sudo list
  → broadcast / admin-style bot cmds

owner_only:
  - sirf OWNER_ID (addsudo / delsudo)
"""
import functools
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app, bot
from config import OWNER_ID
from database.mongo import add_sudo, remove_sudo, get_sudoers

SUDO_USERS: set[int] = {OWNER_ID}


async def load_sudoers():
    SUDO_USERS.clear()
    SUDO_USERS.add(OWNER_ID)
    for uid in await get_sudoers():
        SUDO_USERS.add(uid)


def sudo_only(func):
    """me.id | OWNER_ID | sudo list — userbot cmds (.play etc.)."""
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user:
            return
        uid = message.from_user.id
        if uid == OWNER_ID or uid in SUDO_USERS:
            return await func(client, message, *args, **kwargs)
        try:
            me = await client.get_me()
            if uid == me.id:
                return await func(client, message, *args, **kwargs)
        except Exception:
            return
        return  # silent
    return wrapper


def owner_or_sudo(func):
    """OWNER_ID ya sudo — broadcast etc. (group/DM)."""
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user:
            return
        uid = message.from_user.id
        if uid != OWNER_ID and uid not in SUDO_USERS:
            await message.reply_text("❌ Sirf OWNER / sudo.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper


def owner_only(func):
    """Sirf .env OWNER_ID."""
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user or message.from_user.id != OWNER_ID:
            return
        return await func(client, message, *args, **kwargs)
    return wrapper


# ---------- sudo management (OWNER only) ----------
@app.on_message(filters.command(["addsudo"], prefixes=["/", ".", "!"]))
@owner_only
async def addsudo_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("Reply to user or: `.addsudo <id>`")
        return
    try:
        target = (
            message.reply_to_message.from_user.id
            if message.reply_to_message and message.reply_to_message.from_user
            else int(message.command[1])
        )
    except (ValueError, IndexError, AttributeError):
        await message.reply_text("Invalid ID.")
        return
    await add_sudo(target)
    SUDO_USERS.add(target)
    await message.reply_text(f"✅ Added `{target}` to sudo.")


@app.on_message(filters.command(["delsudo"], prefixes=["/", ".", "!"]))
@owner_only
async def delsudo_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("Reply to user or: `.delsudo <id>`")
        return
    try:
        target = (
            message.reply_to_message.from_user.id
            if message.reply_to_message and message.reply_to_message.from_user
            else int(message.command[1])
        )
    except (ValueError, IndexError, AttributeError):
        await message.reply_text("Invalid ID.")
        return
    if target == OWNER_ID:
        await message.reply_text("OWNER ko sudo se hata nahi sakte.")
        return
    await remove_sudo(target)
    SUDO_USERS.discard(target)
    await message.reply_text(f"✅ Removed `{target}` from sudo.")


@app.on_message(filters.command(["sudolist"], prefixes=["/", ".", "!"]))
@owner_only
async def sudolist_cmd(client, message: Message):
    lines = "\n".join(f"• <code>{uid}</code>" for uid in sorted(SUDO_USERS))
    await message.reply_text(
        f"👑 <b>Sudo list</b>\n\n{lines}\n\n"
        f"<b>OWNER:</b> <code>{OWNER_ID}</code>"
    )
