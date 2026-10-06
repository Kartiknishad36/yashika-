"""
basics — ping / alive / id / help — MUST always work for owner userbot
Premium command center with full pages.
"""
import asyncio
import time
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME, OWNER_USERNAME
from modules.owner import sudoers
from modules.owner.sudoers import ub_cmd, is_allowed

NAME = BOT_NAME or "Yashika"
OWNER_TAG = f"@{OWNER_USERNAME}" if OWNER_USERNAME else "Owner"
_START_TS = time.time()


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


def _uptime() -> str:
    s = int(time.time() - _START_TS)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}h {m}m {s}s"


HELP_INDEX = (
    f"╔══ 💎 <b>{NAME.upper()} PREMIUM</b> ══╗\n"
    f"Owner: {OWNER_TAG}\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"01 <code>.help vc</code> — Music / VC\n"
    f"02 <code>.help owner</code> — Owner / Sudo\n"
    f"03 <code>.help login</code> — Multi login\n"
    f"04 <code>.help mod</code> — Ban / Mute / Tag\n"
    f"05 <code>.help global</code> — Gban / Warn\n"
    f"06 <code>.help cast</code> — Broadcast\n"
    f"07 <code>.help clone</code> — Clone profile\n"
    f"08 <code>.help welcome</code> — Welcome / VC\n"
    f"09 <code>.help afk</code> — AFK\n"
    f"10 <code>.help tools</code> — Tools\n"
    f"11 <code>.help fun</code> — Arts / Anim\n"
    f"12 <code>.help system</code> — Core\n"
    f"13 <code>.help info</code> — User info\n"
    f"14 <code>.help protect</code> — Protect\n"
    f"15 <code>.help media</code> — Media\n"
    f"16 <code>.help track</code> — Tracker\n"
    f"17 <code>.help anti</code> — Anti modules\n"
    f"18 <code>.help notes</code> — Notes\n"
    f"19 <code>.help economy</code> — Economy\n"
    f"20 <code>.help pm</code> — PM guard\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"Quick: <code>.ping</code> <code>.alive</code> <code>.id</code>\n"
    f"╚══════════════════╝"
)

HELP_PAGES = {
    "vc": (
        "╔══ 🎵 <b>VC / MUSIC</b> ══╗\n"
        "<code>.play</code> — play song\n"
        "<code>.skip</code> <code>.stop</code>\n"
        "<code>.pause</code> <code>.resume</code>\n"
        "<code>.queue</code>\n"
        "<code>.vcwelcome on/off</code>\n"
        "╚══════════════╝"
    ),
    "owner": (
        "╔══ 👑 <b>OWNER</b> ══╗\n"
        "<code>.addsudo</code> reply/id\n"
        "<code>.delsudo</code>\n"
        "<code>.sudolist</code>\n"
        "╚══════════════╝"
    ),
    "login": (
        "╔══ 🔐 <b>LOGIN</b> ══╗\n"
        "<code>.login</code> — phone OTP flow\n"
        "<code>.addsession</code> string\n"
        "<code>.cancellogin</code>\n"
        "<code>.sessions</code> list\n"
        "<code>.sessioninfo</code>\n"
        "<code>.sessionstop</code> / <code>.sessionstart</code>\n"
        "╚══════════════╝"
    ),
    "mod": (
        "╔══ 🛡 <b>MOD / TAG</b> ══╗\n"
        "<code>.ban</code> <code>.unban</code> <code>.kick</code>\n"
        "<code>.mute</code> <code>.unmute</code>\n"
        "<code>.promote</code> <code>.demote</code>\n"
        "<code>.pin</code> <code>.unpin</code>\n"
        "<code>.tagall</code> [text] — batch\n"
        "<code>.tag</code> [text] — one by one\n"
        "<code>.tagallstop</code> <code>.tagstop</code>\n"
        "<code>.tagadmins</code> <code>.tagme</code>\n"
        "╚══════════════╝"
    ),
    "global": (
        "╔══ 🌐 <b>GLOBAL</b> ══╗\n"
        "<code>.gban</code> <code>.ungban</code>\n"
        "<code>.gbanlist</code>\n"
        "<code>.warn</code> <code>.unwarn</code>\n"
        "<code>.warns</code> <code>.resetwarns</code>\n"
        "╚══════════════╝"
    ),
    "cast": (
        "╔══ 📢 <b>BROADCAST</b> ══╗\n"
        "<code>.broadcast</code>\n"
        "<code>.gcast</code>\n"
        "<code>.dmcast</code>\n"
        "╚══════════════╝"
    ),
    "clone": (
        "╔══ 👤 <b>CLONE</b> ══╗\n"
        "<code>.clonemode</code>\n"
        "<code>.clone</code> reply\n"
        "<code>.back</code> restore\n"
        "╚══════════════╝"
    ),
    "welcome": (
        "╔══ 👋 <b>WELCOME</b> ══╗\n"
        "<code>.welcome on/off</code>\n"
        "<code>.setwelcome</code> text\n"
        "<code>.vcwelcome on/off</code>\n"
        "╚══════════════╝"
    ),
    "afk": (
        "╔══ 💤 <b>AFK</b> ══╗\n"
        "<code>.afk</code> reason\n"
        "<code>.unafk</code> / <code>.back</code>\n"
        "╚══════════════╝"
    ),
    "tools": (
        "╔══ 🛠 <b>TOOLS</b> ══╗\n"
        "<code>.calc</code> <code>.time</code>\n"
        "<code>.weather</code> <code>.tr</code>\n"
        "<code>.nuinfo</code> number\n"
        "<code>.qr</code> <code>.paste</code>\n"
        "╚══════════════╝"
    ),
    "fun": (
        "╔══ 🎨 <b>FUN / ARTS</b> ══╗\n"
        "<code>.cat</code> <code>.rose</code>\n"
        "<code>.hacker</code> <code>.error</code>\n"
        "<code>.fuck</code> <code>.butterfly</code>\n"
        "<code>.love</code> <code>.moon</code>\n"
        "<code>.heart</code> <code>.myson</code>\n"
        "<code>.yourmom</code> <code>.funhelp</code>\n"
        "╚══════════════╝"
    ),
    "system": (
        "╔══ ⚙️ <b>SYSTEM</b> ══╗\n"
        "<code>.ping</code> <code>.alive</code>\n"
        "<code>.id</code> <code>.help</code>\n"
        "<code>.uptime</code> <code>.menu</code>\n"
        "╚══════════════╝"
    ),
    "info": (
        "╔══ ℹ️ <b>INFO</b> ══╗\n"
        "<code>.info</code> reply/id\n"
        "<code>.user</code> full report\n"
        "<code>.msginfo</code> <code>.chatinfo</code>\n"
        "<code>.common</code>\n"
        "╚══════════════╝"
    ),
    "protect": (
        "╔══ 🛡 <b>PROTECT</b> ══╗\n"
        "<code>.protect on/off/status</code>\n"
        "Reply + <code>.protect</code>\n"
        "<code>.psend</code> text\n"
        "Reply + <code>.pfile</code>\n"
        "╚══════════════╝"
    ),
    "media": (
        "╔══ 🖼 <b>MEDIA</b> ══╗\n"
        "<code>.kang</code> sticker\n"
        "<code>.dp</code> / Mango DP\n"
        "<code>.dpsave</code>\n"
        "╚══════════════╝"
    ),
    "track": (
        "╔══ 📍 <b>TRACK</b> ══╗\n"
        "<code>.track</code>\n"
        "<code>.trackadd</code>\n"
        "<code>.trackdel</code>\n"
        "╚══════════════╝"
    ),
    "anti": (
        "╔══ 🚫 <b>ANTI</b> ══╗\n"
        "<code>.antilink</code>\n"
        "<code>.antidelete</code>\n"
        "<code>.antiflood</code>\n"
        "╚══════════════╝"
    ),
    "notes": (
        "╔══ 📝 <b>NOTES</b> ══╗\n"
        "<code>.save</code> <code>.get</code>\n"
        "<code>.notes</code>\n"
        "╚══════════════╝"
    ),
    "economy": (
        "╔══ 💰 <b>ECONOMY</b> ══╗\n"
        "<code>.bal</code> <code>.daily</code>\n"
        "<code>.rob</code>\n"
        "╚══════════════╝"
    ),
    "pm": (
        "╔══ 💬 <b>PM GUARD</b> ══╗\n"
        "<code>.approve</code> <code>.unapprove</code>\n"
        "<code>.approved</code>\n"
        "╚══════════════╝"
    ),
    # aliases
    "tag": None,  # filled below
    "arts": None,
    "anim": None,
    "flowers": None,
    "anims": None,
    "spy": None,
    "warn": None,
    "bro": (
        "╔══ 🤝 <b>BRO</b> ══╗\n"
        "<code>.bro</code> reply\n"
        "<code>.unbro</code>\n"
        "<code>.brolist</code>\n"
        "╚══════════════╝"
    ),
}

# aliases point to same pages
HELP_PAGES["tag"] = HELP_PAGES["mod"]
HELP_PAGES["arts"] = HELP_PAGES["fun"]
HELP_PAGES["anim"] = HELP_PAGES["fun"]
HELP_PAGES["flowers"] = HELP_PAGES["fun"]
HELP_PAGES["anims"] = HELP_PAGES["fun"]
HELP_PAGES["spy"] = HELP_PAGES["info"]
HELP_PAGES["warn"] = HELP_PAGES["global"]
HELP_PAGES["ghost"] = HELP_PAGES["track"]
HELP_PAGES["dl"] = HELP_PAGES["media"]
HELP_PAGES["raid"] = (
    "╔══ ⚡ <b>RAID</b> ══╗\n"
    "Owner modules only\n"
    "╚══════════════╝"
)


async def _do_help(message: Message):
    parts = (message.text or "").split()
    if len(parts) > 1:
        key = parts[1].lower()
        page = HELP_PAGES.get(key)
        if not page:
            await _send(
                message,
                f"❌ Unknown page <code>{key}</code>\n"
                f"Use <code>.help</code> for index",
            )
            return
        await _send(message, page)
        return
    await _send(message, HELP_INDEX)
    print("[help] OK")


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]ping(\s|$)"), group=-10)
async def ping_me(client, message: Message):
    t0 = time.time()
    try:
        m = await message.reply_text("💎 Pinging...")
        ms = (time.time() - t0) * 1000
        prem = "Yes" if getattr(await client.get_me(), "is_premium", False) else "No"
        await m.edit_text(
            f"╔══ 💎 <b>PONG</b> ══╗\n"
            f"Latency: <code>{ms:.0f}ms</code>\n"
            f"Uptime: <code>{_uptime()}</code>\n"
            f"Premium: <b>{prem}</b>\n"
            f"╚══════════╝"
        )
        print("[ping] OK")
    except Exception as e:
        print(f"[ping] {e}")


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]alive(\s|$)"), group=-10)
async def alive_me(client, message: Message):
    try:
        me = await client.get_me()
        prem = "✅" if getattr(me, "is_premium", False) else "❌"
    except Exception:
        me = None
        prem = "?"
    await _send(
        message,
        f"╔══ 💎 <b>{NAME}</b> ══╗\n"
        f"Status: <b>ALIVE</b>\n"
        f"Premium: {prem}\n"
        f"Uptime: <code>{_uptime()}</code>\n"
        f"Owner: {OWNER_TAG}\n"
        f"<code>.help</code> · <code>.ping</code>\n"
        f"╚══════════════╝",
    )


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]id(\s|$)"), group=-10)
async def id_me(client, message: Message):
    chat_id = message.chat.id if message.chat else 0
    user_id = (
        message.reply_to_message.from_user.id
        if message.reply_to_message and message.reply_to_message.from_user
        else (message.from_user.id if message.from_user else sudoers.ME_ID)
    )
    await _send(
        message,
        f"╔══ 🆔 <b>IDS</b> ══╗\n"
        f"Chat: <code>{chat_id}</code>\n"
        f"User: <code>{user_id}</code>\n"
        f"╚══════════╝",
    )


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]uptime(\s|$)"), group=-10)
async def uptime_me(client, message: Message):
    await _send(message, f"⏱ Uptime: <code>{_uptime()}</code>")


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
        await asyncio.sleep(0.25)
        await msg.edit_text("💎")
        await asyncio.sleep(0.25)
        await msg.edit_text(HELP_INDEX)
    except Exception:
        await _send(message, HELP_INDEX)


@app.on_message(
    ub_cmd("ping", "alive", "id", "help", "menu", "cmds", "commands", "helpanim", "uptime"),
    group=-9,
)
async def core_ub(client, message: Message):
    if getattr(message, "outgoing", False):
        return
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
    elif cmd == "uptime":
        await uptime_me(client, message)
    elif cmd in ("help", "menu", "cmds", "commands"):
        await _do_help(message)
    elif cmd == "helpanim":
        await helpanim_me(client, message)
