"""
Core: .ping .alive .id .help .uptime
Premium HELP with INLINE BUTTONS for every category.
"""
import asyncio
import time

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

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


async def _reply(message: Message, text: str, reply_markup=None):
    try:
        await message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        print(f"[basics] reply fail: {e}")
        try:
            await app.send_message(message.chat.id, text, reply_markup=reply_markup)
        except Exception as e2:
            print(f"[basics] send fail: {e2}")


# ─── Category texts ───
PAGES = {
    "home": (
        f"╔══════════════════════════╗\n"
        f"║ ✨💎 <b>{NAME.upper()} PREMIUM</b> 💎✨ ║\n"
        f"║ 👑 {OWNER_TAG}\n"
        f"╚══════════════════════════╝\n\n"
        f"Neeche <b>buttons</b> se category kholo.\n"
        f"Har command <code>.</code> prefix se.\n\n"
        f"⏱ Uptime: <code>{{up}}</code>\n"
        f"💎 Premium Userbot"
    ),
    "sys": (
        "⚙️ <b>SYSTEM</b>\n\n"
        "<code>.ping</code> — latency\n"
        "<code>.alive</code> — status\n"
        "<code>.id</code> — chat/user id\n"
        "<code>.uptime</code> — uptime\n"
        "<code>.help</code> — this menu\n"
        "<code>.helpanim</code> — animated help"
    ),
    "vc": (
        "🎵 <b>VC / MUSIC</b>\n\n"
        "<code>.play</code> — play song\n"
        "<code>.skip</code> — skip\n"
        "<code>.stop</code> — stop\n"
        "<code>.pause</code> / <code>.resume</code>\n"
        "<code>.queue</code> — queue\n"
        "<code>.vcwelcome on</code> / <code>off</code>"
    ),
    "owner": (
        "👑 <b>OWNER</b>\n\n"
        "<code>.addsudo</code> <code>.delsudo</code>\n"
        "<code>.sudolist</code>\n"
        "<code>.sessions</code> <code>.sessioninfo</code>\n"
        "<code>.sessionstop</code> <code>.sessionstart</code>\n"
        "Bot DM: <code>/login</code>"
    ),
    "mod": (
        "🛡 <b>MOD</b>\n\n"
        "<code>.ban</code> <code>.unban</code> <code>.kick</code>\n"
        "<code>.mute</code> <code>.unmute</code>\n"
        "<code>.promote</code> <code>.demote</code>\n"
        "<code>.pin</code> <code>.unpin</code>"
    ),
    "tag": (
        "📣 <b>TAG</b>\n\n"
        "<code>.tagall</code> — all members\n"
        "<code>.tag</code> — one by one\n"
        "<code>.tagadmins</code> <code>.tagme</code>\n"
        "<code>.tagallstop</code> <code>.tagstop</code>"
    ),
    "bro": (
        "🔥 <b>BRO</b>\n\n"
        "<code>.bro 10</code> — reply spam\n"
        "<code>.broall</code> — group\n"
        "<code>.brodm</code> — DM\n"
        "<code>.brogroup</code> — long\n"
        "<code>.unbro</code> <code>.brolist</code>"
    ),
    "global": (
        "🌐 <b>GLOBAL</b>\n\n"
        "<code>.gban</code> <code>.ungban</code> <code>.gbanlist</code>\n"
        "<code>.warn</code> <code>.unwarn</code> <code>.warns</code>\n"
        "<code>.broadcast</code> <code>.gcast</code> <code>.dmcast</code>"
    ),
    "clone": (
        "👤 <b>CLONE</b>\n\n"
        "<code>.clone</code> — copy profile\n"
        "<code>.back</code> — restore\n"
        "<code>.clonemode on/off</code>"
    ),
    "welcome": (
        "👋 <b>WELCOME · AFK</b>\n\n"
        "<code>.welcome on</code> <code>.welcome off</code>\n"
        "<code>.setwelcome</code>\n"
        "<code>.afk</code> <code>.unafk</code>"
    ),
    "tools": (
        "🛠 <b>TOOLS</b>\n\n"
        "<code>.calc</code> <code>.time</code> <code>.weather</code>\n"
        "<code>.tr</code> <code>.qr</code> <code>.paste</code>\n"
        "<code>.nuinfo</code> — 200+ phone details"
    ),
    "fun": (
        "🎨 <b>FUN · ARTS</b>\n\n"
        "<code>.cat</code> <code>.rose</code> <code>.hacker</code>\n"
        "<code>.error</code> <code>.fuck</code> <code>.butterfly</code>\n"
        "<code>.love</code> <code>.moon</code> <code>.heart</code>\n"
        "<code>.yourmom</code> <code>.myson</code>\n"
        "<code>.ok</code> <code>.vip</code> <code>.boss</code> <code>.pro</code>\n"
        "<code>.king</code> <code>.yashika</code> <code>.win</code>\n"
        "<code>.gg</code> <code>.hi</code> <code>.bye</code>\n"
        "<code>.funhelp</code> <code>.arts</code>"
    ),
    "info": (
        "ℹ️ <b>INFO</b>\n\n"
        "<code>.info</code> <code>.whois</code> — full user\n"
        "<code>.user</code> — deep scan → log\n"
        "<code>.msginfo</code> <code>.chatinfo</code>\n"
        "<code>.groupinfo</code> <code>.common</code>\n"
        "<code>.nuinfo</code> — number 200+"
    ),
    "media": (
        "🛡 <b>PROTECT · MEDIA</b>\n\n"
        "<code>.protect</code> <code>.psend</code> <code>.pfile</code>\n"
        "<code>.kang</code> <code>.dp</code> <code>.dpsave</code>"
    ),
    "auto": (
        "💬 <b>AUTO REPLY</b>\n\n"
        "<code>.autoreply on</code> <code>.autoreply off</code>\n"
        "<code>.stylescan</code> <code>.stylestatus</code>"
    ),
    "pm": (
        "🔒 <b>PM · TRACK · ANTI</b>\n\n"
        "<code>.approve</code> <code>.unapprove</code>\n"
        "<code>.antispam on</code> <code>.pmlog on</code>\n"
        "<code>.track</code> <code>.trackadd</code> <code>.trackdel</code>\n"
        "<code>.antilink</code> <code>.antidelete</code> <code>.antiflood</code>"
    ),
    "notes": (
        "📝 <b>NOTES · ECONOMY</b>\n\n"
        "<code>.save</code> <code>.get</code> <code>.notes</code>\n"
        "<code>.bal</code> <code>.daily</code> <code>.rob</code>"
    ),
}


def _main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ System", callback_data="yh:sys"),
            InlineKeyboardButton("🎵 VC", callback_data="yh:vc"),
            InlineKeyboardButton("👑 Owner", callback_data="yh:owner"),
        ],
        [
            InlineKeyboardButton("🛡 Mod", callback_data="yh:mod"),
            InlineKeyboardButton("📣 Tag", callback_data="yh:tag"),
            InlineKeyboardButton("🔥 Bro", callback_data="yh:bro"),
        ],
        [
            InlineKeyboardButton("🌐 Global", callback_data="yh:global"),
            InlineKeyboardButton("👤 Clone", callback_data="yh:clone"),
            InlineKeyboardButton("👋 Welcome", callback_data="yh:welcome"),
        ],
        [
            InlineKeyboardButton("🛠 Tools", callback_data="yh:tools"),
            InlineKeyboardButton("🎨 Fun", callback_data="yh:fun"),
            InlineKeyboardButton("ℹ️ Info", callback_data="yh:info"),
        ],
        [
            InlineKeyboardButton("🎬 Media", callback_data="yh:media"),
            InlineKeyboardButton("💬 Auto", callback_data="yh:auto"),
            InlineKeyboardButton("🔒 PM", callback_data="yh:pm"),
        ],
        [
            InlineKeyboardButton("📝 Notes", callback_data="yh:notes"),
            InlineKeyboardButton("📖 Full Text", callback_data="yh:full"),
        ],
    ])


def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data="yh:home")],
        [InlineKeyboardButton("📖 Full Text", callback_data="yh:full")],
    ])


HELP_FULL = (
    f"╔══════════════════════════╗\n"
    f"║ ✨💎 <b>{NAME.upper()} PREMIUM</b> 💎✨ ║\n"
    f"║ 👑 {OWNER_TAG}\n"
    f"╚══════════════════════════╝\n\n"
    + "\n\n".join(
        PAGES[k] for k in (
            "sys", "vc", "owner", "mod", "tag", "bro", "global",
            "clone", "welcome", "tools", "fun", "info", "media",
            "auto", "pm", "notes",
        )
    )
    + f"\n\n💎 <b>{NAME}</b> · Prefix <b>.</b> only"
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
        f"💎 Premium: {prem}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Help", callback_data="yh:home")],
        ]),
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
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🏓 Ping", callback_data="yh:sys"),
                InlineKeyboardButton("📖 Help", callback_data="yh:home"),
            ],
        ]),
    )


@app.on_message(ub_cmd("id"), group=-20)
async def cmd_id(client, message: Message):
    cid = message.chat.id if message.chat else 0
    uid = (
        message.reply_to_message.from_user.id
        if message.reply_to_message and message.reply_to_message.from_user
        else (message.from_user.id if message.from_user else sudoers.ME_ID)
    )
    await _reply(
        message,
        f"🆔 Chat: <code>{cid}</code>\n👤 User: <code>{uid}</code>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ℹ️ .info", callback_data="yh:info")],
        ]),
    )


@app.on_message(ub_cmd("uptime"), group=-20)
async def cmd_uptime(client, message: Message):
    await _reply(
        message,
        f"⏱ Uptime: <code>{_uptime()}</code>",
        reply_markup=_main_kb(),
    )


@app.on_message(ub_cmd("help", "menu", "cmds", "commands"), group=-20)
async def cmd_help(client, message: Message):
    text = PAGES["home"].format(up=_uptime())
    await _reply(message, text, reply_markup=_main_kb())


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
    text = PAGES["home"].format(up=_uptime())
    await _reply(message, text, reply_markup=_main_kb())


@app.on_callback_query(filters.regex(r"^yh:"))
async def help_buttons(client, cq: CallbackQuery):
    key = (cq.data or "").split(":", 1)[-1]
    try:
        if key == "home":
            text = PAGES["home"].format(up=_uptime())
            await cq.message.edit_text(text, reply_markup=_main_kb())
        elif key == "full":
            # full may be long — try edit else send
            try:
                await cq.message.edit_text(HELP_FULL[:3900], reply_markup=_back_kb())
            except Exception:
                await cq.message.reply_text(HELP_FULL[:3900], reply_markup=_back_kb())
        elif key in PAGES:
            await cq.message.edit_text(PAGES[key], reply_markup=_back_kb())
        else:
            await cq.answer("Unknown", show_alert=False)
            return
        await cq.answer()
    except Exception as e:
        try:
            await cq.answer(str(e)[:100], show_alert=True)
        except Exception:
            pass


print("[basics] premium HELP + buttons loaded")
