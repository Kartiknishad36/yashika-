"""
Auth decorators.

sudo_only  → sirf TAB jab command USI account se aaye jo client chal raha hai
             (filters.me jaisa). Group/DM mein kisi aur ke command = silent ignore.

owner_only → sirf config OWNER_ID (bot owner / server owner).
             addsudo / delsudo jaise management commands ke liye.

Note: multi-login sessions mein har client apna me.id check karta hai,
isliye koi ek session dusre session ke commands nahi chala sakta.
"""
import functools
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID
from database.mongo import add_sudo, remove_sudo, get_sudoers

# Optional list — sirf bot-side management / future use.
# Userbot commands ab SUDO_USERS pe depend nahi karti.
SUDO_USERS: set[int] = {OWNER_ID}


async def load_sudoers():
    SUDO_USERS.clear()
    SUDO_USERS.add(OWNER_ID)
    for uid in await get_sudoers():
        SUDO_USERS.add(uid)


def sudo_only(func):
    """
    Sirf apna account:
      message.from_user.id == client.get_me().id
    Warna silent return — koi reply nahi.
    """
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user:
            return
        try:
            me = await client.get_me()
        except Exception:
            return
        if message.from_user.id != me.id:
            return  # dusra user — ignore
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
    # Ab userbot commands ke liye zaroori nahi, lekin login-bot access
    # list rakhni ho toh rakho.
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
    await message.reply_text(
        f"✅ Added `{target}` to sudo list.\n"
        f"Note: userbot commands ab sirf har account khud se chalte hain."
    )


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
        "👑 <b>Sudo list</b> (login/management helpers)\n\n"
        + "\n".join(f"• <code>{uid}</code>" for uid in sorted(SUDO_USERS))
        + "\n\nUserbot cmds = sirf apna account (`me.id`)."
    )
    await message.reply_text(text)
