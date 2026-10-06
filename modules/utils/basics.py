"""
basics — ping / alive / id / help
Premium emoji menu — sab commands ek sath.
"""
import asyncio
import time

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


async def _send_multi(message: Message, parts: list):
    for p in parts:
        await _send(message, p)
        await asyncio.sleep(0.35)


def _uptime() -> str:
    s = int(time.time() - _START_TS)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}h {m}m {s}s"


# ─── FULL MENU (all commands together) ───
HELP_FULL_1 = (
    f"✨💎 <b>{NAME.upper()} PREMIUM MENU</b> 💎✨\n"
    f"👑 Owner: {OWNER_TAG}\n"
    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"⚙️ <b>SYSTEM</b>\n"
    f"🏓 <code>.ping</code>  ·  💚 <code>.alive</code>\n"
    f"🆔 <code>.id</code>  ·  ⏱ <code>.uptime</code>\n"
    f"📖 <code>.help</code>  ·  ✨ <code>.helpanim</code>\n\n"
    f"🎵 <b>VC / MUSIC</b>\n"
    f"▶️ <code>.play</code>  ⏭ <code>.skip</code>  ⏹ <code>.stop</code>\n"
    f"⏸ <code>.pause</code>  ▶️ <code>.resume</code>  📋 <code>.queue</code>\n"
    f"🎤 <code>.vcwelcome on/off</code>\n\n"
    f"👑 <b>OWNER / SUDO</b>\n"
    f"➕ <code>.addsudo</code>  ➖ <code>.delsudo</code>\n"
    f"📜 <code>.sudolist</code>\n\n"
    f"🔐 <b>LOGIN</b>\n"
    f"📱 <code>.login</code>  🔑 <code>.addsession</code>\n"
    f"📋 <code>.sessions</code>  ℹ️ <code>.sessioninfo</code>\n"
    f"⏹ <code>.sessionstop</code>  ▶️ <code>.sessionstart</code>\n"
    f"❌ <code>.cancellogin</code>\n\n"
    f"🛡 <b>MOD</b>\n"
    f"🔨 <code>.ban</code>  ✅ <code>.unban</code>  👢 <code>.kick</code>\n"
    f"🔇 <code>.mute</code>  🔊 <code>.unmute</code>\n"
    f"⬆️ <code>.promote</code>  ⬇️ <code>.demote</code>\n"
    f"📌 <code>.pin</code>  📍 <code>.unpin</code>\n\n"
    f"📣 <b>TAG</b>\n"
    f"👥 <code>.tagall</code> [text]  — batch\n"
    f"👤 <code>.tag</code> [text]  — one by one\n"
    f"🛑 <code>.tagallstop</code>  <code>.tagstop</code>\n"
    f"🛡 <code>.tagadmins</code>  🙋 <code>.tagme</code>\n"
)

HELP_FULL_2 = (
    f"🌐 <b>GLOBAL</b>\n"
    f"⛔ <code>.gban</code>  ✅ <code>.ungban</code>  📜 <code>.gbanlist</code>\n"
    f"⚠️ <code>.warn</code>  ♻️ <code>.unwarn</code>  📋 <code>.warns</code>\n\n"
    f"📢 <b>BROADCAST</b>\n"
    f"📡 <code>.broadcast</code>  🌍 <code>.gcast</code>  💬 <code>.dmcast</code>\n\n"
    f"👤 <b>CLONE</b>\n"
    f"🎭 <code>.clonemode</code>  📋 <code>.clone</code>  🔙 <code>.back</code>\n\n"
    f"👋 <b>WELCOME</b>\n"
    f"✅ <code>.welcome on/off</code>\n"
    f"✏️ <code>.setwelcome</code>\n"
    f"🎤 <code>.vcwelcome on/off</code>\n\n"
    f"💤 <b>AFK</b>\n"
    f"🌙 <code>.afk</code>  ☀️ <code>.unafk</code>  🔙 <code>.back</code>\n\n"
    f"🛠 <b>TOOLS</b>\n"
    f"🔢 <code>.calc</code>  🕐 <code>.time</code>  🌤 <code>.weather</code>\n"
    f"🌐 <code>.tr</code>  📞 <code>.nuinfo</code>\n"
    f"📷 <code>.qr</code>  📄 <code>.paste</code>\n\n"
    f"🎨 <b>FUN / ARTS</b>\n"
    f"🐈 <code>.cat</code>  🌹 <code>.rose</code>  💻 <code>.hacker</code>\n"
    f"⚠️ <code>.error</code>  🖕 <code>.fuck</code>  🦋 <code>.butterfly</code>\n"
    f"❤️ <code>.love</code>  🌕 <code>.moon</code>  💖 <code>.heart</code>\n"
    f"🐰 <code>.myson</code>  🤱 <code>.yourmom</code>  🎨 <code>.funhelp</code>\n\n"
    f"ℹ️ <b>INFO</b>\n"
    f"👤 <code>.info</code>  📊 <code>.user</code>\n"
    f"💬 <code>.msginfo</code>  🏷 <code>.chatinfo</code>  🔗 <code>.common</code>\n\n"
    f"🛡 <b>PROTECT</b>\n"
    f"🔒 <code>.protect on/off</code>  ✉️ <code>.psend</code>  📎 <code>.pfile</code>\n\n"
    f"🖼 <b>MEDIA</b>\n"
    f"🎗 <code>.kang</code>  🖼 <code>.dp</code>  💾 <code>.dpsave</code>\n\n"
    f"📍 <b>TRACK</b>\n"
    f"👁 <code>.track</code>  ➕ <code>.trackadd</code>  ➖ <code>.trackdel</code>\n\n"
    f"🚫 <b>ANTI</b>\n"
    f"🔗 <code>.antilink</code>  🗑 <code>.antidelete</code>  🌊 <code>.antiflood</code>\n\n"
    f"📝 <b>NOTES</b>  ·  💰 <b>ECONOMY</b>  ·  💬 <b>PM</b>\n"
    f"💾 <code>.save</code> <code>.get</code> <code>.notes</code>\n"
    f"💵 <code>.bal</code> <code>.daily</code> <code>.rob</code>\n"
    f"✅ <code>.approve</code> <code>.unapprove</code> <code>.approved</code>\n\n"
    f"━━━━━━━━━━━━━━━━━━━━━━\n"
    f"✨ Page: <code>.help fun</code> <code>.help mod</code> …\n"
    f"💎 <b>{NAME}</b> · Premium Userbot"
)

HELP_PAGES = {
    "vc": HELP_FULL_1.split("🛡 <b>MOD</b>")[0] if False else (
        "🎵 <b>VC</b>\n▶️<code>.play</code> ⏭<code>.skip</code> ⏹<code>.stop</code>\n"
        "⏸<code>.pause</code> ▶️<code>.resume</code> 📋<code>.queue</code>\n"
        "🎤<code>.vcwelcome on/off</code>"
    ),
    "owner": "👑 <b>OWNER</b>\n➕<code>.addsudo</code> ➖<code>.delsudo</code> 📜<code>.sudolist</code>",
    "login": (
        "🔐 <b>LOGIN</b>\n📱<code>.login</code> 🔑<code>.addsession</code>\n"
        "📋<code>.sessions</code> ℹ️<code>.sessioninfo</code>\n"
        "⏹<code>.sessionstop</code> ▶️<code>.sessionstart</code> ❌<code>.cancellogin</code>"
    ),
    "mod": (
        "🛡 <b>MOD + TAG</b>\n"
        "🔨<code>.ban</code> ✅<code>.unban</code> 👢<code>.kick</code>\n"
        "🔇<code>.mute</code> 🔊<code>.unmute</code>\n"
        "⬆️<code>.promote</code> ⬇️<code>.demote</code>\n"
        "📌<code>.pin</code> 📍<code>.unpin</code>\n"
        "👥<code>.tagall</code> 👤<code>.tag</code> 🛑<code>.tagstop</code>\n"
        "🛡<code>.tagadmins</code> 🙋<code>.tagme</code>"
    ),
    "global": "🌐 <b>GLOBAL</b>\n⛔<code>.gban</code> ✅<code>.ungban</code> ⚠️<code>.warn</code> ♻️<code>.unwarn</code>",
    "cast": "📢 <b>CAST</b>\n📡<code>.broadcast</code> 🌍<code>.gcast</code> 💬<code>.dmcast</code>",
    "clone": "👤 <b>CLONE</b>\n🎭<code>.clonemode</code> 📋<code>.clone</code> 🔙<code>.back</code>",
    "welcome": "👋 <b>WELCOME</b>\n✅<code>.welcome on/off</code> ✏️<code>.setwelcome</code> 🎤<code>.vcwelcome</code>",
    "afk": "💤 <b>AFK</b>\n🌙<code>.afk</code> ☀️<code>.unafk</code> 🔙<code>.back</code>",
    "tools": "🛠 <b>TOOLS</b>\n🔢<code>.calc</code> 🕐<code>.time</code> 🌤<code>.weather</code> 🌐<code>.tr</code> 📞<code>.nuinfo</code>",
    "fun": (
        "🎨 <b>FUN</b>\n🐈<code>.cat</code> 🌹<code>.rose</code> 💻<code>.hacker</code>\n"
        "⚠️<code>.error</code> 🖕<code>.fuck</code> 🦋<code>.butterfly</code>\n"
        "❤️<code>.love</code> 🌕<code>.moon</code> 💖<code>.heart</code>\n"
        "🐰<code>.myson</code> 🤱<code>.yourmom</code> 🎨<code>.funhelp</code>"
    ),
    "system": "⚙️ <b>SYSTEM</b>\n🏓<code>.ping</code> 💚<code>.alive</code> 🆔<code>.id</code> ⏱<code>.uptime</code>",
    "info": "ℹ️ <b>INFO</b>\n👤<code>.info</code> 📊<code>.user</code> 💬<code>.msginfo</code> 🏷<code>.chatinfo</code>",
    "protect": "🛡 <b>PROTECT</b>\n🔒<code>.protect</code> ✉️<code>.psend</code> 📎<code>.pfile</code>",
    "media": "🖼 <b>MEDIA</b>\n🎗<code>.kang</code> 🖼<code>.dp</code> 💾<code>.dpsave</code>",
    "track": "📍 <b>TRACK</b>\n👁<code>.track</code> ➕<code>.trackadd</code> ➖<code>.trackdel</code>",
    "anti": "🚫 <b>ANTI</b>\n🔗<code>.antilink</code> 🗑<code>.antidelete</code> 🌊<code>.antiflood</code>",
    "notes": "📝 <b>NOTES</b>\n💾<code>.save</code> 📥<code>.get</code> 📋<code>.notes</code>",
    "economy": "💰 <b>ECONOMY</b>\n💵<code>.bal</code> 🎁<code>.daily</code> 🔫<code>.rob</code>",
    "pm": "💬 <b>PM</b>\n✅<code>.approve</code> ❌<code>.unapprove</code> 📜<code>.approved</code>",
    "bro": "🤝 <b>BRO</b>\n<code>.bro</code> <code>.unbro</code> <code>.brolist</code>",
}
HELP_PAGES["tag"] = HELP_PAGES["mod"]
HELP_PAGES["arts"] = HELP_PAGES["fun"]
HELP_PAGES["anim"] = HELP_PAGES["fun"]
HELP_PAGES["anims"] = HELP_PAGES["fun"]
HELP_PAGES["spy"] = HELP_PAGES["info"]
HELP_PAGES["warn"] = HELP_PAGES["global"]
HELP_PAGES["ghost"] = HELP_PAGES["track"]


async def _do_help(message: Message):
    parts = (message.text or "").split()
    if len(parts) > 1:
        key = parts[1].lower()
        page = HELP_PAGES.get(key)
        if not page:
            await _send(message, f"❌ Unknown · try <code>.help</code>")
            return
        await _send(message, f"✨ {page}")
        return
    # sab commands ek sath (2 messages — Telegram limit)
    await _send_multi(message, [HELP_FULL_1, HELP_FULL_2])
    print("[help] OK full")


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]ping(\s|$)"), group=-10)
async def ping_me(client, message: Message):
    t0 = time.time()
    try:
        m = await message.reply_text("💎✨ Pinging...")
        ms = (time.time() - t0) * 1000
        prem = "✅" if getattr(await client.get_me(), "is_premium", False) else "❌"
        await m.edit_text(
            f"🏓 <b>PONG!</b> ✨\n"
            f"⚡ <code>{ms:.0f}ms</code>\n"
            f"⏱ <code>{_uptime()}</code>\n"
            f"💎 Premium: {prem}"
        )
    except Exception as e:
        print(f"[ping] {e}")


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]alive(\s|$)"), group=-10)
async def alive_me(client, message: Message):
    try:
        me = await client.get_me()
        prem = "✅" if getattr(me, "is_premium", False) else "❌"
        uname = f"@{me.username}" if me.username else "—"
    except Exception:
        prem, uname = "?", "—"
    await _send(
        message,
        f"💚✨ <b>{NAME}</b> is <b>ALIVE</b> ✨\n"
        f"👤 {uname}\n"
        f"💎 Premium: {prem}\n"
        f"⏱ <code>{_uptime()}</code>\n"
        f"👑 {OWNER_TAG}\n"
        f"📖 <code>.help</code>",
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
        f"🆔 <b>IDs</b>\n💬 Chat: <code>{chat_id}</code>\n👤 User: <code>{user_id}</code>",
    )


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]uptime(\s|$)"), group=-10)
async def uptime_me(client, message: Message):
    await _send(message, f"⏱✨ Uptime: <code>{_uptime()}</code>")


@app.on_message(
    filters.me & filters.text & filters.regex(r"^[.!](help|menu|cmds|commands)(\s|$)"),
    group=-10,
)
async def help_me(client, message: Message):
    await _do_help(message)


@app.on_message(filters.me & filters.text & filters.regex(r"^[.!]helpanim(\s|$)"), group=-10)
async def helpanim_me(client, message: Message):
    frames = ["✨", "💎", "✨💎✨", "📖 Loading..."]
    try:
        msg = await message.reply_text(frames[0])
        for f in frames[1:]:
            await asyncio.sleep(0.3)
            await msg.edit_text(f)
        await asyncio.sleep(0.3)
        await msg.edit_text(HELP_FULL_1)
        await _send(message, HELP_FULL_2)
    except Exception:
        await _do_help(message)


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
