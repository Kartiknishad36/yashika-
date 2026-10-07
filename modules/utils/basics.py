"""
Core: .ping .alive .id .help .uptime
Ek hi premium HELP — sirf . commands
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


HELP = (
    f"╔══════════════════════════╗\n"
    f"║ ✨💎 <b>{NAME.upper()} PREMIUM</b> 💎✨ ║\n"
    f"║ 👑 {OWNER_TAG}\n"
    f"╚══════════════════════════╝\n\n"

    f"⚙️ <b>SYSTEM</b>\n"
    f"<code>.ping</code> <code>.alive</code> <code>.id</code>\n"
    f"<code>.uptime</code> <code>.help</code> <code>.helpanim</code>\n\n"

    f"🎵 <b>VC</b>\n"
    f"<code>.play</code> <code>.skip</code> <code>.stop</code>\n"
    f"<code>.pause</code> <code>.resume</code> <code>.queue</code>\n"
    f"<code>.vcwelcome on</code> <code>.vcwelcome off</code>\n\n"

    f"👑 <b>OWNER</b>\n"
    f"<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>\n\n"

    f"🛡 <b>MOD</b>\n"
    f"<code>.ban</code> <code>.unban</code> <code>.kick</code>\n"
    f"<code>.mute</code> <code>.unmute</code>\n"
    f"<code>.promote</code> <code>.demote</code>\n"
    f"<code>.pin</code> <code>.unpin</code>\n\n"

    f"📣 <b>TAG</b>\n"
    f"<code>.tagall</code> <code>.tag</code> <code>.tagadmins</code>\n"
    f"<code>.tagme</code> <code>.tagallstop</code> <code>.tagstop</code>\n\n"

    f"🔥 <b>BRO</b>\n"
    f"<code>.bro</code> <code>.broall</code> <code>.unbro</code>\n"
    f"<code>.brostop</code> <code>.brolist</code>\n\n"

    f"🌐 <b>GLOBAL</b>\n"
    f"<code>.gban</code> <code>.ungban</code> <code>.gbanlist</code>\n"
    f"<code>.warn</code> <code>.unwarn</code> <code>.warns</code>\n\n"

    f"📢 <b>CAST</b>\n"
    f"<code>.broadcast</code> <code>.gcast</code> <code>.dmcast</code>\n\n"

    f"👤 <b>CLONE</b>\n"
    f"<code>.clone</code> <code>.back</code> <code>.clonemode</code>\n\n"

    f"👋 <b>WELCOME · AFK</b>\n"
    f"<code>.welcome on</code> <code>.welcome off</code>\n"
    f"<code>.setwelcome</code> <code>.afk</code> <code>.unafk</code>\n\n"

    f"🛠 <b>TOOLS</b>\n"
    f"<code>.calc</code> <code>.time</code> <code>.weather</code>\n"
    f"<code>.tr</code> <code>.qr</code> <code>.paste</code>\n"
    f"<code>.nuinfo</code>\n\n"

    f"🎨 <b>FUN · ARTS</b>\n"
    f"<code>.cat</code> <code>.rose</code> <code>.hacker</code>\n"
    f"<code>.error</code> <code>.fuck</code> <code>.butterfly</code>\n"
    f"<code>.love</code> <code>.moon</code> <code>.heart</code>\n"
    f"<code>.yourmom</code> <code>.myson</code>\n"
    f"<code>.ok</code> <code>.vip</code> <code>.boss</code> <code>.pro</code>\n"
    f"<code>.king</code> <code>.yashika</code> <code>.win</code>\n"
    f"<code>.gg</code> <code>.hi</code> <code>.bye</code>\n"
    f"<code>.funhelp</code> <code>.arts</code>\n\n"

    f"ℹ️ <b>INFO</b>\n"
    f"<code>.info</code> <code>.whois</code> <code>.user</code>\n"
    f"<code>.msginfo</code> <code>.chatinfo</code> <code>.groupinfo</code>\n"
    f"<code>.common</code>\n\n"

    f"🛡 <b>PROTECT · MEDIA</b>\n"
    f"<code>.protect</code> <code>.psend</code> <code>.pfile</code>\n"
    f"<code>.kang</code> <code>.dp</code> <code>.dpsave</code>\n\n"

    f"💬 <b>AUTO REPLY</b>\n"
    f"<code>.autoreply on</code> <code>.autoreply off</code>\n"
    f"<code>.autoreply set</code> <code>.autoreply mode</code>\n"
    f"<code>.stylescan</code> <code>.stylestatus</code>\n\n"

    f"📂 <b>SESSIONS</b>\n"
    f"<code>.sessions</code> <code>.sessioninfo</code>\n"
    f"<code>.sessionstop</code> <code>.sessionstart</code>\n\n"

    f"📝 <b>NOTES · ECONOMY</b>\n"
    f"<code>.save</code> <code>.get</code> <code>.notes</code>\n"
    f"<code>.bal</code> <code>.daily</code> <code>.rob</code>\n\n"

    f"🔒 <b>PM · TRACK · ANTI</b>\n"
    f"<code>.approve</code> <code>.unapprove</code>\n"
    f"<code>.track</code> <code>.trackadd</code> <code>.trackdel</code>\n"
    f"<code>.antilink</code> <code>.antidelete</code> <code>.antiflood</code>\n\n"

    f"💎 <b>{NAME}</b> · Premium Userbot\n"
    f"Prefix: <b>.</b> only"
)


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
        f"🏓 <b>PONG</b>\n"
        f"⚡ <code>{ms:.0f}ms</code>\n"
        f"⏱ <code>{_uptime()}</code>\n"
        f"💎 Premium: {prem}"
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
        f"💚 <b>{NAME}</b> ALIVE\n"
        f"👤 {un}\n💎 {prem}\n"
        f"⏱ <code>{_uptime()}</code>\n👑 {OWNER_TAG}",
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
    await _reply(message, HELP)


@app.on_message(ub_cmd("helpanim"), group=-20)
async def cmd_helpanim(client, message: Message):
    frames = ["✨", "💎", "✨💎✨", f"💎 <b>{NAME}</b> 💎"]
    try:
        m = await message.reply_text(frames[0])
        for f in frames[1:]:
            await asyncio.sleep(0.3)
            await m.edit_text(f)
        await asyncio.sleep(0.35)
        await m.delete()
    except Exception:
        pass
    await _reply(message, HELP)


print("[basics] single .help menu loaded")
