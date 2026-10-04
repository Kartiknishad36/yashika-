"""
basics — ping / alive / id / help

Userbot: apne account se typed commands = outgoing / filters.me
filters.command kabhi miss karta hai → yahan text parse se handle.
"""
import time
import re

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME, OWNER_ID
from modules.owner.sudoers import SUDO_USERS

PREFIXES = (".", "!")


def _parse_cmd(text: str):
    """Return (cmd_name, args_list) or (None, [])."""
    if not text:
        return None, []
    text = text.strip()
    if not text or text[0] not in PREFIXES:
        return None, []
    parts = text[1:].split()
    if not parts:
        return None, []
    return parts[0].lower().split("@")[0], parts[1:]


async def _is_allowed(message: Message, client) -> bool:
    if getattr(message, "outgoing", False):
        return True
    if filters.me(client, message):  # may not work as call — skip
        pass
    uid = message.from_user.id if message.from_user else None
    if uid is None:
        return bool(getattr(message, "outgoing", False))
    if OWNER_ID and uid == OWNER_ID:
        return True
    if uid in SUDO_USERS:
        return True
    try:
        me = await client.get_me()
        if me and uid == me.id:
            return True
    except Exception:
        pass
    return False


def _help_text() -> str:
    name = BOT_NAME or "Yashika"
    return (
        f"<b>{name} · Command Center</b>\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"<b>Music / VC</b>\n"
        f"<code>.play</code> <code>.vply</code> <code>.skip</code> "
        f"<code>.stop</code> <code>.pause</code> <code>.resume</code> <code>.queue</code>\n\n"
        f"<b>Mod</b>\n"
        f"<code>.gban</code> <code>.ungban</code> <code>.gmute</code> "
        f"<code>.warn</code> <code>.tagall</code> <code>.welcome</code>\n\n"
        f"<b>Scan / DP</b>\n"
        f"<code>.uinfo</code> <code>.scan</code> <code>.dp</code> "
        f"<code>.dpsave</code> <code>.dplog</code>\n\n"
        f"<b>Cast</b>\n"
        f"<code>.broadcast</code> <code>.gcast</code> <code>.dmcast</code>\n\n"
        f"<b>Bro</b>\n"
        f"<code>.bro</code> <code>.unbro</code> <code>.brolist</code>\n\n"
        f"<b>Login</b>\n"
        f"<code>.login</code> <code>.addsession</code> <code>.cancellogin</code>\n\n"
        f"<b>Owner</b>\n"
        f"<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>\n\n"
        f"<b>PM</b>\n"
        f"<code>.approve</code> <code>.unapprove</code> <code>.verify</code>\n\n"
        f"<b>AutoReply</b>\n"
        f"<code>.autoreply on</code> / <code>off</code> / <code>set text</code>\n\n"
        f"<b>VC Welcome</b>\n"
        f"<code>.vcwelcome on</code> / <code>off</code> / <code>test</code>\n\n"
        f"<b>Fun</b>\n"
        f"<code>.rose</code> <code>.cat</code> <code>.heart</code>\n\n"
        f"<b>System</b>\n"
        f"<code>.ping</code> <code>.alive</code> <code>.id</code> <code>.help</code>\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Prefix: <code>.</code> or <code>!</code>"
    )


# -------- Core handlers: filters.me (userbot own messages) --------

@app.on_message(filters.me & filters.text, group=-2)
async def core_commands(client, message: Message):
    """Own account se typed .cmd — highest priority."""
    text = message.text or ""
    name, args = _parse_cmd(text)
    if not name:
        return  # not a command — let others handle (need continue?)

    # Only handle known core cmds here; others pass via continue_propagation
    core = {
        "ping", "alive", "id", "help", "menu", "cmds", "commands",
    }
    if name not in core:
        try:
            message.continue_propagation()
        except Exception:
            pass
        return

    print(f"[cmd] core: .{name} chat={getattr(message.chat, 'id', None)}")

    try:
        if name == "ping":
            t0 = time.time()
            msg = await message.reply_text("Pinging…")
            ms = (time.time() - t0) * 1000
            await msg.edit_text(f"<b>Pong!</b> <code>{ms:.0f}ms</code>")
            return

        if name == "alive":
            await message.reply_text(
                f"<b>{BOT_NAME or 'Yashika'}</b> is online.\n"
                f"<code>.help</code> · <code>.ping</code>"
            )
            return

        if name == "id":
            chat_id = message.chat.id if message.chat else 0
            user_id = (
                message.reply_to_message.from_user.id
                if message.reply_to_message and message.reply_to_message.from_user
                else (message.from_user.id if message.from_user else "N/A")
            )
            await message.reply_text(
                f"<b>Chat:</b> <code>{chat_id}</code>\n"
                f"<b>User:</b> <code>{user_id}</code>"
            )
            return

        if name in ("help", "menu", "cmds", "commands"):
            await message.reply_text(_help_text())
            print("[help] OK")
            return
    except Exception as e:
        print(f"[cmd] .{name} ERROR: {type(e).__name__}: {e}")
        try:
            await client.send_message(
                message.chat.id,
                f"Error: <code>{type(e).__name__}: {e}</code>",
            )
        except Exception:
            pass


# Also allow sudo users (incoming) for help/ping
@app.on_message(
    filters.text
    & filters.regex(r"^[.!](ping|alive|id|help|menu|cmds|commands)(\s|$)")
    & ~filters.me,
    group=-1,
)
async def core_commands_sudo(client, message: Message):
    if not await _is_allowed(message, client):
        return
    text = message.text or ""
    name, args = _parse_cmd(text)
    if not name:
        return
    print(f"[cmd] sudo: .{name}")
    try:
        if name == "ping":
            t0 = time.time()
            msg = await message.reply_text("Pinging…")
            await msg.edit_text(f"<b>Pong!</b> <code>{(time.time()-t0)*1000:.0f}ms</code>")
        elif name == "alive":
            await message.reply_text(f"<b>{BOT_NAME or 'Yashika'}</b> online")
        elif name == "id":
            await message.reply_text(
                f"Chat <code>{message.chat.id}</code>"
            )
        elif name in ("help", "menu", "cmds", "commands"):
            await message.reply_text(_help_text())
    except Exception as e:
        print(f"[cmd-sudo] {e}")
