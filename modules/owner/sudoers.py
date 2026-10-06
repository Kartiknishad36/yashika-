"""
Auth + userbot command filter
Sirf aapka account (outgoing / ME_ID / OWNER_ID).
"""
import functools
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID
from database.mongo import add_sudo, remove_sudo, get_sudoers

SUDO_USERS: set = {OWNER_ID} if OWNER_ID else set()
ME_ID: int = 0

# Known commands for "unknown command" hint (extend as needed)
KNOWN_CMDS = {
    "ping", "alive", "id", "help", "menu", "cmds", "commands", "helpanim", "uptime",
    "ban", "unban", "kick", "mute", "unmute", "promote", "demote", "pin", "unpin",
    "tagall", "tag", "tagallstop", "tagstop", "tagadmins", "tagme",
    "gban", "ungban", "gbanlist", "warn", "unwarn", "warns", "resetwarns",
    "broadcast", "gcast", "dmcast",
    "clone", "clonemode", "back",
    "welcome", "setwelcome", "vcwelcome",
    "afk", "unafk",
    "calc", "time", "weather", "tr", "nuinfo", "qr", "paste",
    "cat", "rose", "hacker", "hack", "error", "fuck", "butterfly", "love",
    "moon", "chand", "heart", "heartart", "yourmom", "myson", "funhelp", "arts",
    "info", "whois", "user", "msginfo", "chatinfo", "groupinfo", "common",
    "protect", "psend", "pfile",
    "kang", "dp", "dpsave",
    "track", "trackadd", "trackdel",
    "antilink", "antidelete", "antiflood",
    "save", "get", "notes",
    "bal", "daily", "rob",
    "approve", "unapprove", "approved",
    "login", "addsession", "cancellogin", "mylogin",
    "sessions", "sessioninfo", "sessionstop", "sessionstart",
    "addsudo", "delsudo", "sudolist",
    "play", "skip", "stop", "pause", "resume", "queue",
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
    """True only for messages YOU sent (userbot)."""
    if getattr(message, "outgoing", False):
        return True
    uid = None
    try:
        if message.from_user:
            uid = message.from_user.id
    except Exception:
        pass
    if uid is None:
        # no from_user + not clearly incoming → treat as possible self
        return bool(getattr(message, "outgoing", False))
    if ME_ID and uid == ME_ID:
        return True
    if OWNER_ID and uid == OWNER_ID:
        return True
    return False


def ub_cmd(*names):
    """
    .cmd / !cmd / /cmd — SIRF aapke messages.
    filters.me AND avoid karo (kabhi fail hota hai) — outgoing/ME_ID check.
    """
    want = {n.lower().lstrip(".!/") for n in names}

    async def _filter(_, client, message: Message):
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
    """ub_cmd already self-only — just run handler (no silent drop)."""

    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not _is_self(message):
            # last chance live me
            try:
                me = await client.get_me()
                if me:
                    set_me_id(me.id)
                uid = message.from_user.id if message.from_user else None
                if not (getattr(message, "outgoing", False) or (uid and uid == me.id)):
                    return
            except Exception:
                return
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            # show error so user knows what failed
            try:
                await message.reply_text(
                    f"❌ <b>Command error</b>\n"
                    f"<code>{type(e).__name__}: {e}</code>"
                )
            except Exception:
                print(f"[cmd error] {e}")
            print(f"[sudo_only err] {e}")

    return wrapper


def owner_or_sudo(func):
    return sudo_only(func)


def owner_only(func):
    return sudo_only(func)


@app.on_message(ub_cmd("addsudo"))
@owner_only
async def addsudo_cmd(client, message: Message):
    parts = (message.text or "").split()
    if not message.reply_to_message and len(parts) < 2:
        await message.reply_text(
            "❌ Usage: reply + <code>.addsudo</code>\n"
            "ya <code>.addsudo 123456789</code>"
        )
        return
    try:
        target = (
            message.reply_to_message.from_user.id
            if message.reply_to_message and message.reply_to_message.from_user
            else int(parts[1])
        )
    except Exception:
        await message.reply_text("❌ Invalid ID — number chahiye")
        return
    await add_sudo(target)
    SUDO_USERS.add(target)
    await message.reply_text(f"✅ Added sudo <code>{target}</code>")


@app.on_message(ub_cmd("delsudo"))
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
        await message.reply_text("❌ OWNER remove nahi hota")
        return
    await remove_sudo(target)
    SUDO_USERS.discard(target)
    await message.reply_text(f"✅ Removed <code>{target}</code>")


@app.on_message(ub_cmd("sudolist"))
@owner_only
async def sudolist_cmd(client, message: Message):
    lines = "\n".join(f"• <code>{uid}</code>" for uid in sorted(SUDO_USERS))
    await message.reply_text(f"<b>Sudo</b>\n{lines}\nOWNER: <code>{OWNER_ID}</code>")


# Unknown command hint — sirf aapke .xxx pe
@app.on_message(
    filters.create(
        lambda _, __, m: (
            _is_self(m)
            and bool((m.text or "").strip())
            and (m.text or "")[0] in ".!"
        )
    ),
    group=50,
)
async def _unknown_cmd_hint(client, message: Message):
    text = (message.text or "").strip()
    if not text or text[0] not in ".!":
        return
    parts = text[1:].split()
    if not parts:
        return
    cmd = parts[0].lower().split("@")[0]
    if cmd in KNOWN_CMDS:
        return  # real handler should have run
    # missing args style hints for common mistakes
    hint = (
        f"❓ <b>Unknown command</b>: <code>.{cmd}</code>\n\n"
        f"📖 Try: <code>.help</code>\n"
        f"🏓 Test: <code>.ping</code>\n"
        f"🎨 Fun: <code>.rose</code> <code>.cat</code>"
    )
    try:
        await message.reply_text(hint)
    except Exception as e:
        print(f"[unknown] {e}")


# Legacy filters.command → ub_cmd (self only)
try:

    def _ub_command(commands, prefixes=None, case_sensitive=False):
        if isinstance(commands, str):
            commands = [commands]
        names = [str(c).lower().lstrip("./!") for c in commands]
        return ub_cmd(*names)

    filters.command = _ub_command
    print("[sudoers] ub_cmd self-only + unknown hint ON")
except Exception as e:
    print(f"[sudoers] patch skip: {e}")
