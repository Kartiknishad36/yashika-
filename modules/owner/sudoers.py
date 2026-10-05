"""
Auth + userbot-safe command filter

ub_cmd("play", "rose") — text parse for . / ! commands
sudo_only / owner_or_sudo / owner_only

Also patches pyrogram filters.command so legacy modules work.
"""
import functools
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID
from database.mongo import add_sudo, remove_sudo, get_sudoers

SUDO_USERS: set = {OWNER_ID} if OWNER_ID else set()
ME_ID: int = 0


async def load_sudoers():
    SUDO_USERS.clear()
    if OWNER_ID:
        SUDO_USERS.add(OWNER_ID)
    try:
        for uid in await get_sudoers():
            SUDO_USERS.add(uid)
    except Exception:
        pass


def set_me_id(uid: int):
    global ME_ID
    ME_ID = int(uid)
    SUDO_USERS.add(ME_ID)


def ub_cmd(*names):
    """Match .cmd / !cmd — sets message.command for handlers."""
    want = {n.lower().lstrip(".!") for n in names}

    async def _filter(_, __, message: Message):
        text = (message.text or message.caption or "").strip()
        if not text or text[0] not in ".!/":
            return False
        parts = text[1:].split()
        if not parts:
            return False
        cmd = parts[0].lower().split("@")[0]
        if cmd not in want:
            return False
        try:
            message.command = list(parts)
            message.command[0] = cmd
        except Exception:
            pass
        return True

    return filters.create(_filter)


def _is_self(message: Message) -> bool:
    if getattr(message, "outgoing", False):
        return True
    uid = message.from_user.id if message.from_user else None
    if uid is None:
        return False
    if ME_ID and uid == ME_ID:
        return True
    if OWNER_ID and uid == OWNER_ID:
        return True
    if uid in SUDO_USERS:
        return True
    return False


def sudo_only(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if _is_self(message):
            return await func(client, message, *args, **kwargs)
        if not message.from_user:
            return
        uid = message.from_user.id
        if OWNER_ID and uid == OWNER_ID:
            return await func(client, message, *args, **kwargs)
        if uid in SUDO_USERS:
            return await func(client, message, *args, **kwargs)
        if ME_ID and uid == ME_ID:
            return await func(client, message, *args, **kwargs)
        try:
            me = await client.get_me()
            if me and uid == me.id:
                set_me_id(me.id)
                return await func(client, message, *args, **kwargs)
        except Exception:
            pass
        return

    return wrapper


def owner_or_sudo(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if _is_self(message):
            return await func(client, message, *args, **kwargs)
        if not message.from_user:
            return
        uid = message.from_user.id
        if uid != OWNER_ID and uid not in SUDO_USERS and uid != ME_ID:
            await message.reply_text("Sirf OWNER / sudo.")
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
        if ME_ID and uid == ME_ID:
            return await func(client, message, *args, **kwargs)
        return

    return wrapper


@app.on_message(ub_cmd("addsudo"))
@owner_only
async def addsudo_cmd(client, message: Message):
    parts = (message.text or "").split()
    if not message.reply_to_message and len(parts) < 2:
        await message.reply_text("Reply to user or: <code>.addsudo id</code>")
        return
    try:
        target = (
            message.reply_to_message.from_user.id
            if message.reply_to_message and message.reply_to_message.from_user
            else int(parts[1])
        )
    except (ValueError, IndexError, AttributeError):
        await message.reply_text("Invalid ID.")
        return
    await add_sudo(target)
    SUDO_USERS.add(target)
    await message.reply_text(f"Added <code>{target}</code> to sudo.")


@app.on_message(ub_cmd("delsudo"))
@owner_only
async def delsudo_cmd(client, message: Message):
    parts = (message.text or "").split()
    if not message.reply_to_message and len(parts) < 2:
        await message.reply_text("Reply to user or: <code>.delsudo id</code>")
        return
    try:
        target = (
            message.reply_to_message.from_user.id
            if message.reply_to_message and message.reply_to_message.from_user
            else int(parts[1])
        )
    except (ValueError, IndexError, AttributeError):
        await message.reply_text("Invalid ID.")
        return
    if target == OWNER_ID:
        await message.reply_text("OWNER ko sudo se hata nahi sakte.")
        return
    await remove_sudo(target)
    SUDO_USERS.discard(target)
    await message.reply_text(f"Removed <code>{target}</code> from sudo.")


@app.on_message(ub_cmd("sudolist"))
@owner_only
async def sudolist_cmd(client, message: Message):
    lines = "\n".join(f"• <code>{uid}</code>" for uid in sorted(SUDO_USERS))
    await message.reply_text(
        f"<b>Sudo list</b>\n\n{lines}\n\n"
        f"<b>OWNER:</b> <code>{OWNER_ID}</code>"
    )


# Make filters.command work for pure userbot (must load BEFORE other modules)
try:
    _orig_command = filters.command

    def _ub_command(commands, prefixes=None, case_sensitive=False):
        if isinstance(commands, str):
            commands = [commands]
        names = [str(c).lower().lstrip("./!") for c in commands]
        return ub_cmd(*names)

    filters.command = _ub_command
    print("[sudoers] filters.command → ub_cmd patch ON")
except Exception as _e:
    print(f"[sudoers] patch skip: {_e}")
