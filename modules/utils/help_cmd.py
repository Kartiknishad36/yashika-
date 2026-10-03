"""
Premium Help Menu — multi-page + URL buttons
Works on Railway / Render / Heroku / Koyeb / VPS / local (pure Pyrogram).
"""
from pyrogram import filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from core.clients import app
from modules.owner.sudoers import sudo_only
from config import (
    BOT_NAME,
    SUPPORT_CHAT,
    UPDATE_CHANNEL,
    OWNER_USERNAME,
)

PREFIXES = [".", "!"]

REPO_URL = "https://github.com/Kartiknishad36/yashika-"
RAILWAY_URL = "https://railway.app/new"
RENDER_URL = "https://dashboard.render.com/select-repo?type=web"
HEROKU_URL = "https://dashboard.heroku.com/new?template=" + REPO_URL
KOYEB_URL = "https://app.koyeb.com/deploy"
OKTETO_URL = "https://cloud.okteto.com"


def _owner_link() -> str:
    if OWNER_USERNAME:
        return f"https://t.me/{OWNER_USERNAME.lstrip('@')}"
    return "https://t.me/KARTIK_NISHAD_3"


def _support() -> str:
    return SUPPORT_CHAT or "https://t.me/+Ml99kT7JCMo0OTdl"


def _channel() -> str:
    return UPDATE_CHANNEL or "https://t.me/ye_duniya_ek_sapna_he"


# ---------- category texts ----------
PAGES = {
    "home": (
        f"✨ <b>{BOT_NAME or 'Yashika'} Userbot</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Pure Userbot · Premium Menu</i>\n\n"
        f"🎵 Music · 👑 Owner · 📢 Broadcast\n"
        f"💕 Bro · 🕵️ Scan · 👮 Mod · 🛡 PM\n"
        f"💰 Economy · 🔧 Utils\n\n"
        f"👇 Category choose karo\n"
        f"Prefix: <code>.</code> <code>!</code>"
    ),
    "music": (
        "🎵 <b>MUSIC / VC</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.play</code> — song play (YT / reply)\n"
        "<code>.vply</code> — video play\n"
        "<code>.skip</code> — next track\n"
        "<code>.stop</code> / <code>.end</code> — stop VC\n"
        "<code>.pause</code> — pause\n"
        "<code>.resume</code> — resume\n"
        "<code>.queue</code> — queue list\n\n"
        "<i>cookies.txt + ffmpeg required</i>"
    ),
    "owner": (
        "👑 <b>OWNER / SUDO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.addsudo</code> — add sudo\n"
        "<code>.delsudo</code> — remove sudo\n"
        "<code>.sudolist</code> — list\n"
        "<code>.clone</code> — clone profile\n"
        "<code>.back</code> — restore profile\n"
        "<code>.track</code> on/off — online track\n"
        "<code>.trackadd</code> / <code>.trackdel</code>\n"
        "<code>.ghost</code> — ghost mode"
    ),
    "broadcast": (
        "📢 <b>BROADCAST</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.broadcast</code> — all tracked chats\n"
        "<code>.gcast</code> — groups only\n"
        "<code>.dmcast</code> — DMs only\n\n"
        "Reply + command = copy message\n"
        "<i>Pehle groups/DM me activity se list bane</i>"
    ),
    "bro": (
        "💕 <b>BRO AUTO-REPLY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.bro</code> — DM + group (reply user)\n"
        "<code>.brodm</code> — sirf DM\n"
        "<code>.brogroup</code> — sirf group\n"
        "<code>.unbro</code> — disable\n"
        "<code>.brolist</code> — targets list"
    ),
    "scan": (
        "🕵️ <b>USER SCAN (real API)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.uinfo</code> / <code>.scan</code> — full report\n"
        "<code>.dphist</code> — DP history photos\n"
        "<code>.member</code> — is group status\n"
        "<code>.fwdinfo</code> — forward origin\n"
        "<code>.commonlist</code> — mutual groups\n"
        "<code>.whois</code> — quick profile\n"
        "<code>.mutual</code> — common chats\n"
        "<code>.picspy</code> — get DP"
    ),
    "mod": (
        "👮 <b>MODERATION</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.gban</code> / <code>.ungban</code>\n"
        "<code>.gmute</code> · <code>.gdel</code>\n"
        "<code>.warn</code> / <code>.warns</code>\n"
        "<code>.tagall</code> — mention all\n"
        "<code>.welcome</code> on/off\n"
        "<code>.antilink</code> · <code>.antiflood</code>\n"
        "<code>.nightmode</code> · <code>.slowmode</code>\n"
        "<code>.zombies</code> · <code>.locks</code>"
    ),
    "pm": (
        "🛡 <b>PM GUARD</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.approve</code> / <code>.unapprove</code>\n"
        "<code>.antispam</code>\n"
        "<code>.secretlog</code>\n"
        "<code>.pmguard</code> settings"
    ),
    "eco": (
        "💰 <b>ECONOMY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.bal</code> / <code>.balance</code>\n"
        "<code>.daily</code> — daily reward\n"
        "<code>.rob</code> — rob user\n"
        "<code>.pay</code> — transfer"
    ),
    "utils": (
        "🔧 <b>UTILS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.afk</code> · <code>.info</code> · <code>.id</code>\n"
        "<code>.notes</code> · <code>.filter</code>\n"
        "<code>.qr</code> · <code>.paste</code>\n"
        "<code>.telegraph</code> · <code>.stats</code>\n"
        "<code>.ping</code> · <code>.alive</code>\n"
        "<code>.help</code> — ye menu"
    ),
    "deploy": (
        "🚀 <b>DEPLOY (any platform)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Same code chalega:\n"
        "• Railway · Render · Heroku\n"
        "• Koyeb · Okteto · VPS · Local\n\n"
        "Required env:\n"
        "<code>API_ID</code> <code>API_HASH</code>\n"
        "<code>STRING_SESSION</code> <code>OWNER_ID</code>\n\n"
        "Start: <code>python3 main.py</code>\n"
        "Neeche buttons se platform kholo."
    ),
}


def _nav_keyboard(page: str = "home") -> InlineKeyboardMarkup:
    # category grid
    cats = [
        ["🎵 Music", "help:music", "👑 Owner", "help:owner"],
        ["📢 Broadcast", "help:broadcast", "💕 Bro", "help:bro"],
        ["🕵️ Scan", "help:scan", "👮 Mod", "help:mod"],
        ["🛡 PM", "help:pm", "💰 Eco", "help:eco"],
        ["🔧 Utils", "help:utils", "🚀 Deploy", "help:deploy"],
    ]
    rows = []
    for row in cats:
        rows.append(
            [
                InlineKeyboardButton(row[0], callback_data=row[1]),
                InlineKeyboardButton(row[2], callback_data=row[3]),
            ]
        )

    if page != "home":
        rows.append(
            [InlineKeyboardButton("🏠 Home", callback_data="help:home")]
        )

    # link buttons — Telegram
    rows.append(
        [
            InlineKeyboardButton("💬 Support", url=_support()),
            InlineKeyboardButton("📢 Channel", url=_channel()),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton("👤 Owner", url=_owner_link()),
            InlineKeyboardButton("📦 Source", url=REPO_URL),
        ]
    )
    # deploy platforms
    rows.append(
        [
            InlineKeyboardButton("🚂 Railway", url=RAILWAY_URL),
            InlineKeyboardButton("🖥 Render", url=RENDER_URL),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton("🟣 Heroku", url=HEROKU_URL),
            InlineKeyboardButton("☁ Koyeb", url=KOYEB_URL),
        ]
    )
    return InlineKeyboardMarkup(rows)


@app.on_message(filters.command(["help", "cmds", "commands", "menu"], prefixes=PREFIXES))
@sudo_only
async def help_cmd(client, message: Message):
    text = PAGES["home"]
    await message.reply_text(
        text,
        reply_markup=_nav_keyboard("home"),
        disable_web_page_preview=True,
    )


@app.on_callback_query(filters.regex(r"^help:(\w+)$"))
async def help_cb(client, query: CallbackQuery):
    # only owner/sudo (or self)
    try:
        from config import OWNER_ID
        from modules.owner.sudoers import SUDO_USERS

        uid = query.from_user.id if query.from_user else 0
        me = await client.get_me()
        if uid not in SUDO_USERS and uid != OWNER_ID and uid != me.id:
            await query.answer("Sirf OWNER / sudo.", show_alert=True)
            return
    except Exception:
        pass

    page = query.data.split(":", 1)[1]
    text = PAGES.get(page, PAGES["home"])
    try:
        await query.edit_message_text(
            text,
            reply_markup=_nav_keyboard(page),
            disable_web_page_preview=True,
        )
    except Exception:
        try:
            await query.answer()
        except Exception:
            pass
        return
    try:
        await query.answer()
    except Exception:
        pass
