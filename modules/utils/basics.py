"""
basics — ping / alive / id / help — MUST always work for owner userbot
"""
import asyncio
import time

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME
from modules.owner import sudoers
from modules.owner.sudoers import ub_cmd, is_allowed

NAME = BOT_NAME or "Yashika"


async def _send(message: Message, text: str):
    try:
        await message.reply_text(text)
        return
    except Exception as e:
        print(f"[basics reply] {e}")
    try:
        await app.send_message(message.chat.id, text)
    except Exception as e:
        print(f"[basics send] {e}")


# ========== CORE: filters.me so userbot ALWAYS matches own messages ==========

@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]ping(\s|$)"), group=-10)
async def ping_me(client, message: Message):
    t0 = time.time()
    try:
        m = await message.reply_text("Pinging...")
        ms = (time.time() - t0) * 1000
        await m.edit_text(f"<b>Pong!</b> <code>{ms:.0f}ms</code>")
        print("[ping] OK")
    except Exception as e:
        print(f"[ping] {e}")


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]alive(\s|$)"), group=-10)
async def alive_me(client, message: Message):
    await _send(
        message,
        f"<b>{NAME}</b> is <b>ALIVE</b>\n<code>.help</code> · <code>.ping</code>",
    )


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]id(\s|$)"), group=-10)
async def id_me(client, message: Message):
    chat_id = message.chat.id if message.chat else 0
    user_id = (
        message.reply_to_message.from_user.id
        if message.reply_to_message and message.reply_to_message.from_user
        else (message.from_user.id if message.from_user else sudoers.ME_ID)
    )
    await _send(message, f"<b>IDs</b>\nChat: <code>{chat_id}</code>\nUser: <code>{user_id}</code>")


HELP_INDEX = (
    f"<b>YASHIKA COMMAND CENTER</b>\n"
    f"{NAME}\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"01 <code>.help vc</code> MUSIC\n"
    f"02 <code>.help owner</code> OWNER\n"
    f"03 <code>.help login</code> LOGIN\n"
    f"04 <code>.help mod</code> MOD / TAGALL\n"
    f"05 <code>.help global</code> GBAN\n"
    f"06 <code>.help cast</code> BROADCAST\n"
    f"07 <code>.help bro</code> BRO\n"
    f"08 <code>.help welcome</code> WELCOME\n"
    f"09 <code>.help afk</code> AFK\n"
    f"10 <code>.help tools</code> TOOLS\n"
    f"11 <code>.help fun</code> FUN\n"
    f"12 <code>.help system</code> SYSTEM\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"<code>.ping</code> <code>.rose</code> <code>.tagall</code>"
)

HELP_PAGES = {
    "vc": "<b>VC</b>\n<code>.play .skip .stop .pause .resume .queue .vcwelcome</code>",
    "owner": "<b>OWNER</b>\n<code>.addsudo .delsudo .sudolist</code>",
    "login": "<b>LOGIN</b>\n<code>.login .addsession .cancellogin</code>",
    "mod": "<b>MOD</b>\n<code>.ban .kick .mute .tagall .tagallstop .tagme</code>",
    "global": "<b>GLOBAL</b>\n<code>.gban .ungban .gbanlist</code>",
    "cast": "<b>CAST</b>\n<code>.broadcast .gcast .dmcast</code>",
    "bro": "<b>BRO</b>\n<code>.bro .unbro .brolist</code>",
    "welcome": "<b>WELCOME</b>\n<code>.welcome on/off .vcwelcome on/off</code>",
    "afk": "<b>AFK</b>\n<code>.afk .unafk .back</code>",
    "tools": "<b>TOOLS</b>\n<code>.calc .time .weather .tr</code>",
    "fun": "<b>FUN</b>\n<code>.rose .cat .heart .hack</code>",
    "system": "<b>SYSTEM</b>\n<code>.ping .alive .id .help .uptime</code>",
    "anti": "<b>ANTI</b>\n<code>.antilink .antidelete .antiflood</code>",
    "warn": "<b>WARN</b>\n<code>.warn .unwarn .warns</code>",
    "raid": "<b>RAID</b>\n<code>.raid .spam</code>",
    "media": "<b>MEDIA</b>\n<code>.kang .dp .dpsave</code>",
    "flowers": "<b>FLOWERS</b>\n<code>.rose .cat .heart</code>",
    "spy": "<b>SPY</b>\n<code>.uinfo .scan</code>",
    "ghost": "<b>GHOST</b>\n<code>.ghostmod .vanish .track</code>",
    "notes": "<b>NOTES</b>\n<code>.save .get .notes</code>",
    "protect": "<b>PROTECT</b>\n<code>.protect on/off</code>",
    "dl": "<b>DL</b>\n<code>.ytmp3 .song .video</code>",
    "anims": "<b>ANIMS</b>\n<code>.hack .heart</code>",
    "pmsec": "<b>PM</b>\n<code>.secretlog .verify</code>",
    "ai": "AI optional",
}


async def _do_help(message: Message):
    parts = (message.text or "").split()
    if len(parts) > 1:
        page = HELP_PAGES.get(parts[1].lower())
        if not page:
            await _send(message, f"No page. <code>.help</code>")
            return
        await _send(message, page)
        return
    await _send(message, HELP_INDEX)
    print("[help] OK")


@app.on_message(
    filters.me & filters.text & filters.regex(r"^[.!](help|menu|cmds|commands)(\s|$)"),
    group=-10,
)
async def help_me(client, message: Message):
    await _do_help(message)


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]helpanim(\s|$)"), group=-10)
async def helpanim_me(client, message: Message):
    try:
        msg = await message.reply_text("✨")
        await asyncio.sleep(0.3)
        await msg.edit_text(HELP_INDEX)
    except Exception:
        await _send(message, HELP_INDEX)


# Also via ub_cmd (sudo / outgoing)
@app.on_message(ub_cmd("ping", "alive", "id", "help", "menu", "cmds", "commands", "helpanim"), group=-9)
async def core_ub(client, message: Message):
    # filters.me handlers at -10 already handle own msgs; this is for edge cases
    if getattr(message, "outgoing", False):
        return  # already handled by filters.me group -10
    if not is_allowed(message):
        return
    cmd = (message.command or [""])[0] if getattr(message, "command", None) else ""
    text = (message.text or "").strip()
    if not cmd and text:
        cmd = text[1:].split()[0].lower().split("@")[0]
    if cmd == "ping":
        await ping_me(client, message)
    elif cmd == "alive":
        await alive_me(client, message)
    elif cmd == "id":
        await id_me(client, message)
    elif cmd in ("help", "menu", "cmds", "commands"):
        await _do_help(message)
    elif cmd == "helpanim":
        await helpanim_me(client, message)
