"""
Shared premium HELP menu + inline buttons.
Used by userbot (.help) and bot (/help /start).
"""
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_NAME, OWNER_USERNAME

NAME = BOT_NAME or "Yashika"
OWNER_TAG = f"@{OWNER_USERNAME}" if OWNER_USERNAME else "Owner"
_START = time.time()


def uptime() -> str:
    s = int(time.time() - _START)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}h {m}m {s}s"


PAGES = {
    "home": (
        f"╔══════════════════════════╗\n"
        f"║ ✨💎 <b>{NAME.upper()} PREMIUM</b> 💎✨ ║\n"
        f"║ 👑 {OWNER_TAG}\n"
        f"╚══════════════════════════╝\n\n"
        f"Neeche <b>buttons</b> se category kholo.\n"
        f"Userbot: <code>.help</code> · Bot: <code>/help</code>\n\n"
        f"⏱ Uptime: <code>{{up}}</code>\n"
        f"💎 Commands buttons · Owner only"
    ),
    "sys": (
        "⚙️ <b>SYSTEM</b>\n\n"
        "<code>.ping</code> / <code>/ping</code> — latency\n"
        "<code>.alive</code> — status\n"
        "<code>.id</code> — chat/user id\n"
        "<code>.uptime</code> — uptime\n"
        "<code>.help</code> / <code>/help</code> — this menu"
    ),
    "vc": (
        "🎵 <b>VC / MUSIC</b>\n\n"
        "<code>.play</code> <code>.skip</code> <code>.stop</code>\n"
        "<code>.pause</code> <code>.resume</code> <code>.queue</code>\n"
        "<code>.vcwelcome on</code> / <code>off</code>"
    ),
    "owner": (
        "👑 <b>OWNER</b>\n\n"
        "<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>\n"
        "<code>.sessions</code> <code>.sessioninfo</code>\n"
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
        "<code>.tagall</code> <code>.tag</code>\n"
        "<code>.tagadmins</code> <code>.tagme</code>\n"
        "<code>.tagallstop</code> <code>.tagstop</code>"
    ),
    "bro": (
        "🔥 <b>BRO</b>\n\n"
        "<code>.bro 10</code> <code>.broall</code>\n"
        "<code>.brodm</code> <code>.brogroup</code>\n"
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
        "<code>.clone</code> <code>.back</code>\n"
        "<code>.clonemode on/off</code>"
    ),
    "welcome": (
        "👋 <b>WELCOME · AFK</b>\n\n"
        "<code>.welcome on/off</code>\n"
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
        "<code>.moon</code> <code>.heart</code> <code>.love</code>\n"
        "<code>.ok</code> <code>.vip</code> <code>.boss</code> <code>.pro</code>\n"
        "<code>.king</code> <code>.yashika</code> <code>.win</code>\n"
        "<code>.gg</code> <code>.hi</code> <code>.bye</code>\n"
        "<code>.funhelp</code> <code>.arts</code>"
    ),
    "info": (
        "ℹ️ <b>INFO</b>\n\n"
        "<code>.info</code> <code>.whois</code> <code>.user</code>\n"
        "<code>.msginfo</code> <code>.chatinfo</code>\n"
        "<code>.groupinfo</code> <code>.common</code>\n"
        "<code>.nuinfo</code>"
    ),
    "media": (
        "🛡 <b>PROTECT · MEDIA</b>\n\n"
        "<code>.protect</code> <code>.psend</code> <code>.pfile</code>\n"
        "<code>.kang</code> <code>.dp</code> <code>.dpsave</code>"
    ),
    "auto": (
        "💬 <b>AUTO REPLY</b>\n\n"
        "<code>.autoreply on/off</code>\n"
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


def main_kb() -> InlineKeyboardMarkup:
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


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data="yh:home")],
        [InlineKeyboardButton("📖 Full Text", callback_data="yh:full")],
    ])


def home_text() -> str:
    return PAGES["home"].format(up=uptime())


def full_text() -> str:
    body = "\n\n".join(
        PAGES[k]
        for k in (
            "sys", "vc", "owner", "mod", "tag", "bro", "global",
            "clone", "welcome", "tools", "fun", "info", "media",
            "auto", "pm", "notes",
        )
    )
    return (
        f"╔══════════════════════════╗\n"
        f"║ ✨💎 <b>{NAME.upper()} PREMIUM</b> 💎✨ ║\n"
        f"║ 👑 {OWNER_TAG}\n"
        f"╚══════════════════════════╝\n\n"
        + body
        + f"\n\n💎 <b>{NAME}</b> · Userbot <code>.</code> · Bot <code>/</code>"
    )


async def handle_help_callback(cq):
    key = (cq.data or "").split(":", 1)[-1]
    try:
        if key == "home":
            await cq.message.edit_text(home_text(), reply_markup=main_kb())
        elif key == "full":
            try:
                await cq.message.edit_text(full_text()[:3900], reply_markup=back_kb())
            except Exception:
                await cq.message.reply_text(full_text()[:3900], reply_markup=back_kb())
        elif key in PAGES:
            await cq.message.edit_text(PAGES[key], reply_markup=back_kb())
        else:
            await cq.answer("Unknown", show_alert=False)
            return
        await cq.answer()
    except Exception as e:
        try:
            await cq.answer(str(e)[:100], show_alert=True)
        except Exception:
            pass
