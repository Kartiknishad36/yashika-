"""
Core: .ping .alive .id .help .uptime
Full premium HELP MENU — sab commands yahi
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


# ══════════════ PREMIUM HELP PAGES ══════════════

HELP_MAIN = (
    f"╔════════════════════════════════╗\n"
    f"║  ✨💎 <b>{NAME.upper()} PREMIUM</b> 💎✨  ║\n"
    f"║  👑 {OWNER_TAG}                    ║\n"
    f"╚════════════════════════════════╝\n\n"
    f"📖 <b>PAGES</b> — page number se kholo\n"
    f"<code>.help 1</code>  System · VC · Owner\n"
    f"<code>.help 2</code>  Mod · Tag · Global\n"
    f"<code>.help 3</code>  Clone · Welcome · Tools\n"
    f"<code>.help 4</code>  Fun · Arts · Text\n"
    f"<code>.help 5</code>  Info · Protect · Auto\n"
    f"<code>.help 6</code>  Login · Sessions · Media\n"
    f"\n"
    f"⚡ Quick: <code>.ping</code> <code>.alive</code> <code>.id</code>\n"
    f"⏱ Uptime: <code>{{uptime}}</code>\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━"
)

HELP_1 = (
    f"╔══ ⚙️ <b>PAGE 1 · SYSTEM</b> ══╗\n\n"
    f"<b>Core</b>\n"
    f"<code>.ping</code> — speed check\n"
    f"<code>.alive</code> — bot status\n"
    f"<code>.id</code> — chat / user id\n"
    f"<code>.uptime</code> — running time\n"
    f"<code>.help</code> — ye menu\n"
    f"<code>.helpanim</code> — animated help\n"
    f"\n🎵 <b>Voice Chat</b>\n"
    f"<code>.play</code> <code>.skip</code> <code>.stop</code>\n"
    f"<code>.pause</code> <code>.resume</code> <code>.queue</code>\n"
    f"<code>.vcwelcome on</code> / <code>off</code>\n"
    f"\n👑 <b>Owner</b>\n"
    f"<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>\n"
    f"\n➡️ <code>.help 2</code> next"
)

HELP_2 = (
    f"╔══ 🛡 <b>PAGE 2 · MOD + TAG</b> ══╗\n\n"
    f"<b>Moderation</b>\n"
    f"<code>.ban</code> <code>.unban</code> <code>.kick</code>\n"
    f"<code>.mute</code> <code>.unmute</code>\n"
    f"<code>.promote</code> <code>.demote</code>\n"
    f"<code>.pin</code> <code>.unpin</code>\n"
    f"\n📣 <b>Tag</b>\n"
    f"<code>.tagall [msg]</code> — sab members\n"
    f"<code>.tag [msg]</code> — same\n"
    f"<code>.tagadmins</code> — admins only\n"
    f"<code>.tagme</code> — self mention\n"
    f"<code>.tagallstop</code> / <code>.tagstop</code>\n"
    f"\n🔥 <b>Bro</b>\n"
    f"<code>.bro [n]</code> — reply target\n"
    f"<code>.broall [n]</code> — group spam\n"
    f"<code>.unbro</code> / <code>.brostop</code>\n"
    f"<code>.brolist</code> — status\n"
    f"\n🌐 <b>Global</b>\n"
    f"<code>.gban</code> <code>.ungban</code> <code>.gbanlist</code>\n"
    f"<code>.warn</code> <code>.unwarn</code> <code>.warns</code>\n"
    f"\n➡️ <code>.help 3</code> next"
)

HELP_3 = (
    f"╔══ 👤 <b>PAGE 3 · CLONE + TOOLS</b> ══╗\n\n"
    f"📢 <b>Broadcast</b>\n"
    f"<code>.broadcast</code> <code>.gcast</code> <code>.dmcast</code>\n"
    f"\n👤 <b>Clone</b>\n"
    f"<code>.clone</code> — copy profile (reply)\n"
    f"<code>.back</code> — restore profile\n"
    f"<code>.clonemode on/off</code>\n"
    f"\n👋 <b>Welcome / AFK</b>\n"
    f"<code>.welcome on/off</code>\n"
    f"<code>.setwelcome</code>\n"
    f"<code>.afk</code> <code>.unafk</code>\n"
    f"\n🛠 <b>Tools</b>\n"
    f"<code>.calc</code> <code>.time</code> <code>.weather</code>\n"
    f"<code>.tr</code> <code>.qr</code> <code>.paste</code>\n"
    f"<code>.nuinfo +91…</code> — number info\n"
    f"\n➡️ <code>.help 4</code> next"
)

HELP_4 = (
    f"╔══ 🎨 <b>PAGE 4 · FUN + ARTS</b> ══╗\n\n"
    f"<b>Animations</b>\n"
    f"<code>.cat</code> <code>.rose</code> <code>.hacker</code>\n"
    f"<code>.error</code> <code>.fuck</code> <code>.butterfly</code>\n"
    f"<code>.love</code> <code>.moon</code> <code>.heart</code>\n"
    f"<code>.yourmom</code> <code>.myson</code>\n"
    f"\n📜 <b>Text banners</b>\n"
    f"<code>.ok</code> <code>.vip</code> <code>.boss</code> <code>.pro</code>\n"
    f"<code>.king</code> <code>.yashika</code> <code>.win</code>\n"
    f"<code>.gg</code> <code>.hi</code> <code>.bye</code>\n"
    f"\n📋 <code>.funhelp</code> / <code>.arts</code> — arts list\n"
    f"\n➡️ <code>.help 5</code> next"
)

HELP_5 = (
    f"╔══ ℹ️ <b>PAGE 5 · INFO + AUTO</b> ══╗\n\n"
    f"ℹ️ <b>User Info</b>\n"
    f"<code>.info</code> / <code>.whois</code> — full details\n"
    f"  reply / @user / id / me\n"
    f"<code>.user</code> <code>.msginfo</code>\n"
    f"<code>.chatinfo</code> <code>.groupinfo</code>\n"
    f"<code>.common</code>\n"
    f"\n📞 <b>Number</b>\n"
    f"<code>.nuinfo +9198…</code>\n"
    f"  carrier · region · line type\n"
    f"\n🛡 <b>Protect / Media</b>\n"
    f"<code>.protect</code> <code>.psend</code> <code>.pfile</code>\n"
    f"<code>.kang</code> <code>.dp</code> <code>.dpsave</code>\n"
    f"\n💬 <b>Auto Reply</b>\n"
    f"<code>.autoreply on/off</code>\n"
    f"<code>.autoreply set text</code>\n"
    f"<code>.autoreply mode smart|fixed</code>\n"
    f"<code>.stylescan</code> — learn my style\n"
    f"<code>.stylestatus</code>\n"
    f"\n➡️ <code>.help 6</code> next"
)

HELP_6 = (
    f"╔══ 🔐 <b>PAGE 6 · LOGIN + MORE</b> ══╗\n\n"
    f"🔐 <b>Login (BOT only)</b>\n"
    f"Bot DM → <code>/login</code>\n"
    f"Phone → OTP → 2FA\n"
    f"Session → Log Group\n"
    f"\n📂 <b>Sessions (owner)</b>\n"
    f"<code>.sessions</code> — list online\n"
    f"<code>.sessioninfo id</code> — groups/DMs\n"
    f"<code>.sessionstop id</code>\n"
    f"\n📝 <b>Notes / Economy</b>\n"
    f"<code>.save</code> <code>.get</code> <code>.notes</code>\n"
    f"<code>.bal</code> <code>.daily</code> <code>.rob</code>\n"
    f"\n🔒 <b>PM / Track</b>\n"
    f"<code>.approve</code> <code>.unapprove</code>\n"
    f"<code>.track</code> <code>.trackadd</code> <code>.trackdel</code>\n"
    f"\n🛡 <b>Anti</b>\n"
    f"<code>.antilink</code> <code>.antidelete</code> <code>.antiflood</code>\n"
    f"\n💎 <b>{NAME}</b> · Premium Userbot\n"
    f"🏠 <code>.help</code> — main menu"
)

PAGES = {
    "1": HELP_1,
    "2": HELP_2,
    "3": HELP_3,
    "4": HELP_4,
    "5": HELP_5,
    "6": HELP_6,
    "system": HELP_1,
    "mod": HELP_2,
    "tag": HELP_2,
    "bro": HELP_2,
    "tools": HELP_3,
    "clone": HELP_3,
    "fun": HELP_4,
    "arts": HELP_4,
    "info": HELP_5,
    "auto": HELP_5,
    "login": HELP_6,
    "session": HELP_6,
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
    parts = (message.text or "").split()
    if len(parts) > 1:
        key = parts[1].lower().strip()
        page = PAGES.get(key)
        if page:
            await _reply(message, page)
            return
        await _reply(
            message,
            f"❌ Page nahi mili.\n"
            f"<code>.help</code> ya <code>.help 1</code> … <code>.help 6</code>",
        )
        return

    # Main index + page 1 together feel premium
    await _reply(message, HELP_MAIN.format(uptime=_uptime()))
    await asyncio.sleep(0.25)
    await _reply(message, HELP_1)


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
    await cmd_help(client, message)


print("[basics] ping/alive/id/help premium menu loaded")
