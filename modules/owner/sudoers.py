"""
Auth decorators — pure userbot

sudo_only: outgoing (own cmds) | me.id | OWNER_ID | SUDO_USERS
owner_or_sudo: OWNER_ID | sudo
owner_only: OWNER_ID only
"""
import functools
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID
from database.mongo import add_sudo, remove_sudo, get_sudoers

SUDO_USERS: set = {OWNER_ID} if OWNER_ID else set()


async def load_sudoers():
    SUDO_USERS.clear()
    if OWNER_ID:
        SUDO_USERS.add(OWNER_ID)
    try:
        for uid in await get_sudoers():
            SUDO_USERS.add(uid)
    except Exception:
        pass
    # always treat the running account as allowed once we know id
    try:
        me = await app.get_me()
        if me:
            SUDO_USERS.add(me.id)
    except Exception:
        pass


def sudo_only(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        # Own account commands (userbot types .help) = always allow
        if getattr(message, "outgoing", False):
            return await func(client, message, *args, **kwargs)

        if not message.from_user:
            return
        uid = message.from_user.id

        if OWNER_ID and uid == OWNER_ID:
            return await func(client, message, *args, **kwargs)
        if uid in SUDO_USERS:
            return await func(client, message, *args, **kwargs)

        try:
            me = await client.get_me()
            if me and uid == me.id:
                SUDO_USERS.add(me.id)
                return await func(client, message, *args, **kwargs)
        except Exception:
            pass
        return

    return wrapper


def owner_or_sudo(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if getattr(message, "outgoing", False):
            return await func(client, message, *args, **kwargs)
        if not message.from_user:
            return
        uid = message.from_user.id
        if uid != OWNER_ID and uid not in SUDO_USERS:
            try:
                me = await client.get_me()
                if me and uid == me.id:
                    return await func(client, message, *args, **kwargs)
            except Exception:
                pass
            await message.reply_text("❌ Sirf OWNER / sudo.")
            return
        return await func(client, message, *args, **kwargs)

    return wrapper


def owner_only(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if getattr(message, "outgoing", False):
            return await func(client, message, *args, **kwargs)
        if not message.from_user:
            return
        uid = message.from_user.id
        if OWNER_ID and uid == OWNER_ID:
            return await func(client, message, *args, **kwargs)
        try:
            me = await client.get_me()
            if me and uid == me.id:
                return await func(client, message, *args, **kwargs)
        except Exception:
            pass
        return

    return wrapper


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
