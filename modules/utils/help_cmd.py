"""
👑 YASHIKA COMMAND CENTER — Premium Help Menu
Photo + coloured emoji buttons + multi-page categories
Works on Railway / Render / Heroku / VPS / local
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
    START_PIC,
)

PREFIXES = [".", "!"]

REPO_URL = "https://github.com/Kartiknishad36/yashika-"
RAILWAY_URL = "https://railway.app/new"
RENDER_URL = "https://dashboard.render.com/select-repo?type=web"
HEROKU_URL = "https://dashboard.heroku.com/new?template=" + REPO_URL
KOYEB_URL = "https://app.koyeb.com/deploy"

# Premium banner (public Telegram-style image — change if you want)
HELP_BANNER = (
    "https://telegra.ph/file/2d279c96d4f6e4d4e0c3a.jpg"
)


def _owner_url() -> str:
    u = (OWNER_USERNAME or "KARTIK_NISHAD_3").lstrip("@")
    return f"https://t.me/{u}"


def _support() -> str:
    return SUPPORT_CHAT or "https://t.me/+Ml99kT7JCMo0OTdl"


def _channel() -> str:
    return UPDATE_CHANNEL or "https://t.me/ye_duniya_ek_sapna_he"


# ===================== MAIN BUTTONS (coloured via emoji) =====================
def main_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🟢 🎵 MUSIC", callback_data="yh:vc"),
                InlineKeyboardButton("🔴 👮 MOD", callback_data="yh:mod"),
            ],
            [
                InlineKeyboardButton("🟣 🕵️ SCAN", callback_data="yh:scan"),
                InlineKeyboardButton("🟡 📢 CAST", callback_data="yh:cast"),
            ],
            [
                InlineKeyboardButton("🩷 💕 BRO", callback_data="yh:bro"),
                InlineKeyboardButton("🩵 👑 OWNER", callback_data="yh:owner"),
            ],
            [
                InlineKeyboardButton("🧡 🛡 PM", callback_data="yh:pm"),
                InlineKeyboardButton("💚 💰 ECO", callback_data="yh:eco"),
            ],
            [
                InlineKeyboardButton("🔵 🛠 TOOLS", callback_data="yh:tools"),
                InlineKeyboardButton("⚪ ⚙️ SYSTEM", callback_data="yh:system"),
            ],
            [
                InlineKeyboardButton("🚀 DEPLOY", callback_data="yh:deploy"),
            ],
            [
                InlineKeyboardButton("💬 Support", url=_support()),
                InlineKeyboardButton("📢 Channel", url=_channel()),
            ],
            [
                InlineKeyboardButton("👤 Owner", url=_owner_url()),
                InlineKeyboardButton("📦 Source", url=REPO_URL),
            ],
            [
                InlineKeyboardButton("❌ CLOSE", callback_data="yh:close"),
            ],
        ]
    )


def back_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="yh:home")],
            [
                InlineKeyboardButton("💬 Support", url=_support()),
                InlineKeyboardButton("👤 Owner", url=_owner_url()),
            ],
            [InlineKeyboardButton("❌ CLOSE", callback_data="yh:close")],
        ]
    )


def deploy_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🚂 Railway", url=RAILWAY_URL),
                InlineKeyboardButton("🖥 Render", url=RENDER_URL),
            ],
            [
                InlineKeyboardButton("🟣 Heroku", url=HEROKU_URL),
                InlineKeyboardButton("☁ Koyeb", url=KOYEB_URL),
            ],
            [InlineKeyboardButton("📦 Source Repo", url=REPO_URL)],
            [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="yh:home")],
            [InlineKeyboardButton("❌ CLOSE", callback_data="yh:close")],
        ]
    )


# ===================== HELP PAGES (full commands) =====================
HOME_CAPTION = (
    f"👑 <b>{BOT_NAME or 'YASHIKA'} COMMAND CENTER</b>\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"✨ <i>Premium Userbot · Select category</i>\n\n"
    f"🟢 Music  🔴 Mod  🟣 Scan  🟡 Broadcast\n"
    f"🩷 Bro  🩵 Owner  🧡 PM  💚 Economy\n"
    f"🔵 Tools  ⚪ System  🚀 Deploy\n\n"
    f"📌 Prefix: <code>.</code> <code>!</code>\n"
    f"🔐 Only OWNER / sudo"
)

HELP_DATA = {
    "vc": (
        "🟢 <b>MUSIC / VC</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.play</code> — play song (YT / reply)\n"
        "<code>.vply</code> — video play\n"
        "<code>.skip</code> — next track\n"
        "<code>.stop</code> / <code>.end</code> — leave VC\n"
        "<code>.pause</code> — pause\n"
        "<code>.resume</code> — resume\n"
        "<code>.queue</code> — show queue\n\n"
        "<i>cookies.txt + ffmpeg recommended</i>"
    ),
    "mod": (
        "🔴 <b>MODERATION</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.gban</code> / <code>.ungban</code>\n"
        "<code>.gmute</code> · <code>.gdel</code>\n"
        "<code>.warn</code> / <code>.warns</code>\n"
        "<code>.tagall</code> — mention members\n"
        "<code>.welcome</code> on/off + text\n"
        "<code>.antilink</code> · <code>.antiflood</code>\n"
        "<code>.antidelete</code> · <code>.locks</code>\n"
        "<code>.nightmode</code> · <code>.slowmode</code>\n"
        "<code>.zombies</code> · <code>.rules</code>\n"
        "<code>.autokick</code>"
    ),
    "scan": (
        "🟣 <b>USER SCAN (real API)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.uinfo</code> / <code>.scan</code> — full report\n"
        "<code>.dphist</code> — profile photos\n"
        "<code>.member</code> — status in this group\n"
        "<code>.fwdinfo</code> — forward origin\n"
        "<code>.commonlist</code> — mutual groups\n"
        "<code>.whois</code> · <code>.spy</code> — quick profile\n"
        "<code>.mutual</code> — common chats\n"
        "<code>.picspy</code> — get DP\n\n"
        "<i>Global groups/DMs/IP Telegram nahi deta</i>"
    ),
    "cast": (
        "🟡 <b>BROADCAST</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.broadcast</code> — all tracked chats\n"
        "<code>.gcast</code> — groups only\n"
        "<code>.dmcast</code> — private DMs only\n\n"
        "Reply + command → message copy\n"
        "<i>Pehle activity se chat list auto-track</i>"
    ),
    "bro": (
        "🩷 <b>BRO + SHAYARI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.bro</code> — auto-reply DM+group\n"
        "<code>.brodm</code> — sirf DM\n"
        "<code>.brogroup</code> — sirf group\n"
        "<code>.unbro</code> — disable\n"
        "<code>.brolist</code> — targets\n\n"
        "Shayari / fun (if loaded):\n"
        "<code>.love</code> · <code>.sad</code> · <code>.attitude</code>"
    ),
    "owner": (
        "🩵 <b>OWNER / SUDO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.addsudo</code> · <code>.delsudo</code>\n"
        "<code>.sudolist</code>\n"
        "<code>.clone</code> — clone profile\n"
        "<code>.back</code> — restore profile\n"
        "<code>.track</code> on/off\n"
        "<code>.trackadd</code> · <code>.trackdel</code>\n"
        "<code>.tracklist</code>\n"
        "<code>.ghost</code> — ghost mode\n"
        "<code>.secretlog</code>"
    ),
    "pm": (
        "🧡 <b>PM GUARD</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.approve</code> / <code>.unapprove</code>\n"
        "<code>.antispam</code>\n"
        "<code>.pmguard</code> settings\n"
        "<code>.secretlog</code>"
    ),
    "eco": (
        "💚 <b>ECONOMY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.bal</code> / <code>.balance</code>\n"
        "<code>.daily</code> — daily reward\n"
        "<code>.rob</code> — rob user\n"
        "<code>.pay</code> — transfer coins"
    ),
    "tools": (
        "🔵 <b>TOOLS / UTILS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.afk</code> · <code>.info</code> · <code>.id</code>\n"
        "<code>.notes</code> · <code>.filter</code>\n"
        "<code>.qr</code> · <code>.paste</code>\n"
        "<code>.telegraph</code> · <code>.stats</code>\n"
        "<code>.kang</code> — sticker kang\n"
        "<code>.download</code> — media dl"
    ),
    "system": (
        "⚪ <b>SYSTEM</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ping</code> — latency\n"
        "<code>.alive</code> — status\n"
        "<code>.help</code> / <code>.menu</code> — this menu\n"
        "<code>.cmds</code> — alias\n\n"
        f"Bot name: <b>{BOT_NAME or 'Yashika'}</b>\n"
        "Mode: <b>Pure Userbot</b>"
    ),
    "deploy": (
        "🚀 <b>DEPLOY ANYWHERE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Same code works on:\n"
        "• Railway · Render · Heroku\n"
        "• Koyeb · VPS · Local\n\n"
        "ENV required:\n"
        "<code>API_ID</code> <code>API_HASH</code>\n"
        "<code>STRING_SESSION</code> <code>OWNER_ID</code>\n\n"
        "Start: <code>python3 main.py</code>\n"
        "Neeche platform buttons dabao 👇"
    ),
}


async def _allowed(uid: int, client) -> bool:
    try:
        from config import OWNER_ID
        from modules.owner.sudoers import SUDO_USERS

        if uid == OWNER_ID or uid in SUDO_USERS:
            return True
        me = await client.get_me()
        return uid == me.id
    except Exception:
        return False


async def _send_help(message: Message):
    """Photo menu with fallback to text."""
    caption = HOME_CAPTION
    markup = main_buttons()
    # try START_PIC path / HELP_BANNER URL
    photo = HELP_BANNER
    if START_PIC and not START_PIC.startswith("assets/"):
        photo = START_PIC
    try:
        await message.reply_photo(
            photo,
            caption=caption,
            reply_markup=markup,
        )
        return
    except Exception:
        pass
    await message.reply_text(
        caption,
        reply_markup=markup,
        disable_web_page_preview=True,
    )


@app.on_message(filters.command(["help", "cmds", "commands", "menu"], prefixes=PREFIXES))
@sudo_only
async def help_cmd(client, message: Message):
    await _send_help(message)


@app.on_callback_query(filters.regex(r"^yh:"))
async def help_callback(client, query: CallbackQuery):
    if not query.from_user or not await _allowed(query.from_user.id, client):
        await query.answer("❌ Sirf OWNER / sudo", show_alert=True)
        return

    data = query.data.split(":", 1)[1]

    if data == "close":
        try:
            await query.message.delete()
        except Exception:
            try:
                await query.message.edit_caption("❌ Closed")
            except Exception:
                pass
        await query.answer()
        return

    if data == "home":
        try:
            if query.message.photo:
                await query.message.edit_caption(
                    HOME_CAPTION,
                    reply_markup=main_buttons(),
                )
            else:
                await query.message.edit_text(
                    HOME_CAPTION,
                    reply_markup=main_buttons(),
                    disable_web_page_preview=True,
                )
        except Exception:
            pass
        await query.answer()
        return

    if data == "deploy":
        text = HELP_DATA["deploy"]
        kb = deploy_buttons()
        try:
            if query.message.photo:
                await query.message.edit_caption(text, reply_markup=kb)
            else:
                await query.message.edit_text(
                    text, reply_markup=kb, disable_web_page_preview=True
                )
        except Exception:
            pass
        await query.answer()
        return

    text = HELP_DATA.get(data)
    if not text:
        await query.answer("Not found", show_alert=True)
        return

    try:
        if query.message.photo:
            await query.message.edit_caption(text, reply_markup=back_buttons())
        else:
            await query.message.edit_text(
                text,
                reply_markup=back_buttons(),
                disable_web_page_preview=True,
            )
    except Exception:
        pass
    await query.answer()
