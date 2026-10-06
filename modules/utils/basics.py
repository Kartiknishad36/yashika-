"""
Core: .ping .alive .id .help .uptime — always work
"""
import asyncio
import time

from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME, OWNER_USERNAME
from modules.owner import sudoers
from modules.owner.sudoers import ub_cmd

NAME = BOT_NAME or "Yashika"
OWNER_TAG = f"@{OWNER_USERNAME}" if OWNER_USERNAME else "Owner"
_START = time.time()


def _uptime() -> str:
    s = int(time.time() - _START)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}h {m}m {s}s"


async def _reply(message: Message, text: str):
    try:
        await message.reply_text(text)
    except Exception as e:
        print(f"[basics] reply fail: {e}")
        try:
            await app.send_message(message.chat.id, text)
        except Exception as e2:
            print(f"[basics] send fail: {e2}")


HELP_1 = (
    f"✨💎 <b>{NAME.upper()} MENU</b> 💎✨\n"
    f"👑 {OWNER_TAG}\n"
    f"━━━━━━━━━━━━━━━━━━━━\n\n"
    f"⚙️ <b>SYSTEM</b>\n"
    f"<code>.ping</code> <code>.alive</code> <code>.id</code> <code>.uptime</code>\n"
    f"<code>.help</code> <code>.help fun</code>\n\n"
    f"🎵 <b>VC</b>\n"
    f"<code>.play</code> <code>.skip</code> <code>.stop</code> <code>.pause</code> <code>.resume</code> <code>.queue</code>\n"
    f"<code>.vcwelcome on/off</code>\n\n"
    f"👑 <b>OWNER</b>\n"
    f"<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>\n\n"
    f"🔐 <b>LOGIN</b>\n"
    f"<code>.login</code> <code>.addsession</code> <code>.sessions</code>\n"
    f"<code>.sessioninfo</code> <code>.sessionstop</code> <code>.sessionstart</code>\n\n"
    f"🛡 <b>MOD</b>\n"
    f"<code>.ban</code> <code>.unban</code> <code>.kick</code> <code>.mute</code> <code>.unmute</code>\n"
    f"<code>.promote</code> <code>.demote</code> <code>.pin</code> <code>.unpin</code>\n\n"
    f"📣 <b>TAG</b>\n"
    f"<code>.tagall</code> <code>.tag</code> <code>.tagstop</code> <code>.tagadmins</code> <code>.tagme</code>\n"
)

HELP_2 = (
    f"🌐 <b>GLOBAL</b>\n"
    f"<code>.gban</code> <code>.ungban</code> <code>.warn</code> <code>.unwarn</code>\n\n"
    f"📢 <b>CAST</b>\n"
    f"<code>.broadcast</code> <code>.gcast</code> <code>.dmcast</code>\n\n"
    f"👤 <b>CLONE</b>\n"
    f"<code>.clone</code> <code>.clonemode</code> <code>.back</code>\n\n"
    f"👋 <b>WELCOME / AFK</b>\n"
    f"<code>.welcome on/off</code> <code>.setwelcome</code>\n"
    f"<code>.afk</code> <code>.unafk</code>\n\n"
    f"🛠 <b>TOOLS</b>\n"
    f"<code>.calc</code> <code>.time</code> <code>.weather</code> <code>.tr</code> <code>.nuinfo</code>\n\n"
    f"🎨 <b>FUN</b>\n"
    f"<code>.cat</code> <code>.rose</code> <code>.hacker</code> <code>.moon</code> <code>.heart</code>\n"
    f"<code>.love</code> <code>.butterfly</code> <code>.funhelp</code>\n\n"
    f"ℹ️ <b>INFO</b>\n"
    f"<code>.info</code> <code>.user</code> <code>.msginfo</code> <code>.chatinfo</code> <code>.common</code>\n\n"
    f"🛡 <b>PROTECT / MEDIA</b>\n"
    f"<code>.protect</code> <code>.psend</code> <code>.kang</code> <code>.dp</code>\n\n"
    f"💎 {NAME} Userbot"
)

PAGES = {
    "fun": "🎨 <code>.cat</code> <code>.rose</code> <code>.hacker</code> <code>.moon</code> <code>.heart</code> <code>.love</code>",
    "mod": "🛡 <code>.ban</code> <code>.kick</code> <code>.mute</code> <code>.tagall</code> <code>.tag</code>",
    "vc": "🎵 <code>.play</code> <code>.skip</code> <code>.stop</code> <code>.vcwelcome</code>",
    "info": "ℹ️ <code>.info</code> <code>.user</code> <code>.msginfo</code> <code>.chatinfo</code>",
}


@app.on_message(ub_cmd("ping"), group=-20)
async def cmd_ping(client, message: Message):
    t0 = time.time()
    m = await message.reply_text("💎 …")
    ms = (time.time() - t0) * 1000
    try:
        prem = "✅" if getattr(await client.get_me(), "is_premium", False) else "❌"
    except Exception:
        prem = "?"
    await m.edit_text(
        f"🏓 <b>PONG</b>\n⚡ <code>{ms:.0f}ms</code>\n⏱ <code>{_uptime()}</code>\n💎 Premium: {prem}"
    )


@app.on_message(ub_cmd("alive"), group=-20)
async def cmd_alive(client, message: Message):
    try:
        me = await client.get_me()
        prem = "✅" if getattr(me, "is_premium", False) else "❌"
        un = f"@{me.username}" if me.username else "—"
    except Exception:
        prem, un = "?", "—"
    await _reply(
        message,
        f"💚 <b>{NAME}</b> ALIVE\n👤 {un}\n💎 {prem}\n⏱ <code>{_uptime()}</code>\n👑 {OWNER_TAG}",
    )


@app.on_message(ub_cmd("id"), group=-20)
async def cmd_id(client, message: Message):
    cid = message.chat.id if message.chat else 0
    uid = (
        message.reply_to_message.from_user.id
        if message.reply_to_message and message.reply_to_message.from_user
        else (message.from_user.id if message.from_user else sudoers.ME_ID)
    )
    await _reply(message, f"🆔 Chat: <code>{cid}</code>\n👤 User: <code>{uid}</code>")


@app.on_message(ub_cmd("uptime"), group=-20)
async def cmd_uptime(client, message: Message):
    await _reply(message, f"⏱ Uptime: <code>{_uptime()}</code>")


@app.on_message(ub_cmd("help", "menu", "cmds", "commands"), group=-20)
async def cmd_help(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) > 1:
        key = parts[1].lower()
        page = PAGES.get(key)
        if page:
            await _reply(message, page)
            return
        await _reply(message, f"❌ Unknown page. Try <code>.help</code>")
        return
    await _reply(message, HELP_1)
    await asyncio.sleep(0.3)
    await _reply(message, HELP_2)


@app.on_message(ub_cmd("helpanim"), group=-20)
async def cmd_helpanim(client, message: Message):
    try:
        m = await message.reply_text("✨")
        await asyncio.sleep(0.25)
        await m.edit_text("💎")
        await asyncio.sleep(0.25)
        await m.delete()
    except Exception:
        pass
    await cmd_help(client, message)


print("[basics] ping/alive/id/help loaded")
