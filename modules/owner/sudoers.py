"""
Userbot auth + command filter
Commands ONLY from YOUR account (outgoing messages).
"""
import functools
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID
from database.mongo import add_sudo, remove_sudo, get_sudoers

SUDO_USERS: set = {OWNER_ID} if OWNER_ID else set()
ME_ID: int = 0

KNOWN_CMDS = {
    "ping", "alive", "id", "help", "menu", "cmds", "commands", "helpanim", "uptime",
    "ban", "unban", "kick", "mute", "unmute", "promote", "demote", "pin", "unpin",
    "tagall", "tag", "tagallstop", "tagstop", "tagadmins", "tagme",
    "gban", "ungban", "gbanlist", "warn", "unwarn", "warns", "resetwarns",
    "broadcast", "gcast", "dmcast", "clone", "clonemode", "back",
    "welcome", "setwelcome", "vcwelcome", "afk", "unafk",
    "calc", "time", "weather", "tr", "nuinfo", "qr", "paste",
    "cat", "rose", "hacker", "hack", "error", "fuck", "butterfly", "love",
    "moon", "chand", "heart", "heartart", "yourmom", "myson", "funhelp", "arts",
    "info", "whois", "user", "msginfo", "chatinfo", "groupinfo", "common",
    "protect", "psend", "pfile", "kang", "dp", "dpsave",
    "track", "trackadd", "trackdel", "antilink", "antidelete", "antiflood",
    "save", "get", "notes", "bal", "daily", "rob",
    "approve", "unapprove", "approved",
    "login", "addsession", "cancellogin", "mylogin",
    "sessions", "sessioninfo", "sessionstop", "sessionstart", "sinfo",
    "addsudo", "delsudo", "sudolist",
    "play", "skip", "stop", "pause", "resume", "queue",
    "about", "version", "restart", "logs", "runtime",
}


async def load_sudoers():
    global ME_ID
    SUDO_USERS.clear()
    if OWNER_ID:
        SUDO_USERS.add(OWNER_ID)
    if ME_ID:
        SUDO_USERS.add(ME_ID)
    try:
        for uid in await get_sudoers():
            SUDO_USERS.add(uid)
    except Exception:
        pass


def set_me_id(uid: int):
    global ME_ID
    ME_ID = int(uid)
    SUDO_USERS.add(ME_ID)
    print(f"[sudoers] ME_ID set to {ME_ID}")


def _is_self(message: Message) -> bool:
    if getattr(message, "outgoing", False):
        return True
    try:
        uid = message.from_user.id if message.from_user else None
    except Exception:
        uid = None
    if uid is None:
        return False
    if ME_ID and uid == ME_ID:
        return True
    if OWNER_ID and uid == OWNER_ID:
        return True
    return False


def ub_cmd(*names):
    """Match .cmd !cmd /cmd on YOUR outgoing messages only."""
    want = {str(n).lower().lstrip(".!/") for n in names}

    async def _filter(_, __, message: Message):
        if not getattr(message, "outgoing", False):
            if not _is_self(message):
                return False
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


def is_allowed(message: Message) -> bool:
    return _is_self(message)


def sudo_only(func):
    """Always run for matched ub_cmd; show errors to chat."""

    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            print(f"[cmd:{func.__name__}] {type(e).__name__}: {e}")
            try:
                await message.reply_text(
                    f"❌ <b>Error</b>\n<code>{type(e).__name__}: {e}</code>"
                )
            except Exception:
                pass

    return wrapper


def owner_or_sudo(func):
    return sudo_only(func)


def owner_only(func):
    return sudo_only(func)


@app.on_message(ub_cmd("addsudo"), group=-5)
@owner_only
async def addsudo_cmd(client, message: Message):
    parts = (message.text or "").split()
    if not message.reply_to_message and len(parts) < 2:
        await message.reply_text("❌ Usage: reply + <code>.addsudo</code> ya <code>.addsudo id</code>")
        return
    try:
        target = (
            message.reply_to_message.from_user.id
            if message.reply_to_message and message.reply_to_message.from_user
            else int(parts[1])
        )
    except Exception:
        await message.reply_text("❌ Invalid ID")
        return
    await add_sudo(target)
    SUDO_USERS.add(target)
    await message.reply_text(f"✅ Sudo added <code>{target}</code>")


@app.on_message(ub_cmd("delsudo"), group=-5)
@owner_only
async def delsudo_cmd(client, message: Message):
    parts = (message.text or "").split()
    if not message.reply_to_message and len(parts) < 2:
        await message.reply_text("❌ Usage: <code>.delsudo id</code>")
        return
    try:
        target = (
            message.reply_to_message.from_user.id
            if message.reply_to_message and message.reply_to_message.from_user
            else int(parts[1])
        )
    except Exception:
        await message.reply_text("❌ Invalid ID")
        return
    if target == OWNER_ID:
        await message.reply_text("❌ OWNER cannot remove")
        return
    await remove_sudo(target)
    SUDO_USERS.discard(target)
    await message.reply_text(f"✅ Removed <code>{target}</code>")


@app.on_message(ub_cmd("sudolist"), group=-5)
@owner_only
async def sudolist_cmd(client, message: Message):
    lines = "\n".join(f"• <code>{uid}</code>" for uid in sorted(SUDO_USERS)) or "—"
    await message.reply_text(f"<b>Sudo list</b>\n{lines}\nOWNER: <code>{OWNER_ID}</code>")


@app.on_message(
    filters.create(
        lambda _, __, m: (
            getattr(m, "outgoing", False)
            and bool((m.text or "").strip())
            and (m.text or "")[0] in ".!"
        )
    ),
    group=99,
)
async def _unknown_hint(client, message: Message):
    text = (message.text or "").strip()
    parts = text[1:].split()
    if not parts:
        return
    cmd = parts[0].lower().split("@")[0]
    if cmd in KNOWN_CMDS:
        return
    try:
        await message.reply_text(
            f"❓ Unknown: <code>.{cmd}</code>\n"
            f"📖 <code>.help</code> · 🏓 <code>.ping</code>"
        )
    except Exception:
        pass


try:

    def _ub_command(commands, prefixes=None, case_sensitive=False):
        if isinstance(commands, str):
            commands = [commands]
        return ub_cmd(*[str(c).lower().lstrip("./!") for c in commands])

    filters.command = _ub_command
    print("[sudoers] ub_cmd OUTGOING-only + filters.command patch ON")
except Exception as e:
    print(f"[sudoers] patch skip: {e}")
