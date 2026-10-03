"""
👑 YASHIKA — FULL PREMIUM COLOUR HELP MENU
.help / .menu / .cmds
"""
from pyrogram import filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from core.clients import app
from modules.owner.sudoers import sudo_only, SUDO_USERS
from config import (
    BOT_NAME,
    SUPPORT_CHAT,
    UPDATE_CHANNEL,
    OWNER_USERNAME,
    START_PIC,
    OWNER_ID,
)

PREFIXES = [".", "!"]

REPO_URL = "https://github.com/Kartiknishad36/yashika-"
RAILWAY_URL = "https://railway.app/new"
RENDER_URL = "https://dashboard.render.com/select-repo?type=web"
HEROKU_URL = "https://dashboard.heroku.com/new?template=" + REPO_URL
KOYEB_URL = "https://app.koyeb.com/deploy"

HELP_BANNER = (
    "https://images.unsplash.com/photo-1614850523459-c2f4e146661a?w=900&q=80"
)


def _owner_url() -> str:
    u = (OWNER_USERNAME or "KARTIK_NISHAD_3").lstrip("@")
    return f"https://t.me/{u}"


def _support() -> str:
    return SUPPORT_CHAT or "https://t.me/+Ml99kT7JCMo0OTdl"


def _channel() -> str:
    return UPDATE_CHANNEL or "https://t.me/ye_duniya_ek_sapna_he"


def main_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🟢🟢 🎵 MUSIC 🟢🟢", callback_data="yh:vc"),
                InlineKeyboardButton("🔴🔴 👮 MOD 🔴🔴", callback_data="yh:mod"),
            ],
            [
                InlineKeyboardButton("🟣🟣 🕵️ SCAN 🟣🟣", callback_data="yh:scan"),
                InlineKeyboardButton("🟡🟡 📢 CAST 🟡🟡", callback_data="yh:cast"),
            ],
            [
                InlineKeyboardButton("🩷🩷 💕 BRO 🩷🩷", callback_data="yh:bro"),
                InlineKeyboardButton("🩵🩵 👑 OWNER 🩵🩵", callback_data="yh:owner"),
            ],
            [
                InlineKeyboardButton("🧡🧡 🛡 PM 🧡🧡", callback_data="yh:pm"),
                InlineKeyboardButton("💚💚 💰 ECO 💚💚", callback_data="yh:eco"),
            ],
            [
                InlineKeyboardButton("🔵🔵 🛠 TOOLS 🔵🔵", callback_data="yh:tools"),
                InlineKeyboardButton("⚪️⚪️ ⚙️ SYSTEM ⚪️⚪️", callback_data="yh:system"),
            ],
            [
                InlineKeyboardButton(
                    "🚀🚀🚀  DEPLOY ANYWHERE  🚀🚀🚀", callback_data="yh:deploy"
                )
            ],
            [
                InlineKeyboardButton("💬💚 SUPPORT", url=_support()),
                InlineKeyboardButton("📢🩵 CHANNEL", url=_channel()),
            ],
            [
                InlineKeyboardButton("👤👑 OWNER", url=_owner_url()),
                InlineKeyboardButton("📦🟡 SOURCE", url=REPO_URL),
            ],
            [
                InlineKeyboardButton(
                    "❌❌  CLOSE MENU  ❌❌", callback_data="yh:close"
                )
            ],
        ]
    )


def back_buttons(color: str = "🟣") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{color}{color}  🔙 BACK TO MENU  {color}{color}",
                    callback_data="yh:home",
                )
            ],
            [
                InlineKeyboardButton("💬💚 SUPPORT", url=_support()),
                InlineKeyboardButton("👤👑 OWNER", url=_owner_url()),
            ],
            [
                InlineKeyboardButton(
                    "❌❌  CLOSE  ❌❌", callback_data="yh:close"
                )
            ],
        ]
    )


def deploy_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🚂🟢 RAILWAY", url=RAILWAY_URL),
                InlineKeyboardButton("🖥🔵 RENDER", url=RENDER_URL),
            ],
            [
                InlineKeyboardButton("🟣 HEROKU", url=HEROKU_URL),
                InlineKeyboardButton("☁️🟡 KOYEB", url=KOYEB_URL),
            ],
            [
                InlineKeyboardButton(
                    "📦🩷  SOURCE REPO  📦🩷", url=REPO_URL
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙🟢  BACK TO MENU  🟢🔙", callback_data="yh:home"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌❌  CLOSE  ❌❌", callback_data="yh:close"
                )
            ],
        ]
    )


HOME_CAPTION = (
    f"╔══════════════════════╗\n"
    f"║  👑 <b>{BOT_NAME or 'YASHIKA'}</b> 👑  ║\n"
    f"║   <b>COMMAND CENTER</b>   ║\n"
    f"╚══════════════════════╝\n\n"
    f"✨ <i>Premium Userbot · Full Colour Menu</i>\n"
    f"━━━━━━━━━━━━━━━━━━━━\n\n"
    f"🟢 <b>MUSIC</b>     🔴 <b>MOD</b>\n"
    f"🟣 <b>SCAN</b>      🟡 <b>CAST</b>\n"
    f"🩷 <b>BRO</b>       🩵 <b>OWNER</b>\n"
    f"🧡 <b>PM</b>        💚 <b>ECO</b>\n"
    f"🔵 <b>TOOLS</b>     ⚪️ <b>SYSTEM</b>\n"
    f"🚀 <b>DEPLOY</b>\n\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"📌 Prefix: <code>.</code>  <code>!</code>\n"
    f"🔐 Access: <b>OWNER / SUDO / own account</b>\n"
    f"💎 Style: <b>Premium Colour Board</b>"
)


HELP_DATA = {
    "vc": (
        "🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢\n"
        "🎵 <b>MUSIC / VC</b>\n"
        "🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢\n\n"
        "🟢 <code>.play</code> — song (YT / reply)\n"
        "🟢 <code>.vply</code> — video play\n"
        "🟢 <code>.skip</code> — next track\n"
        "🟢 <code>.stop</code> / <code>.end</code> — leave VC\n"
        "🟢 <code>.pause</code> — pause\n"
        "🟢 <code>.resume</code> — resume\n"
        "🟢 <code>.queue</code> — show queue\n\n"
        "💚 <i>cookies.txt + ffmpeg recommended</i>"
    ),
    "mod": (
        "🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴\n"
        "👮 <b>MODERATION</b>\n"
        "🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴\n\n"
        "🔴 <code>.gban</code> / <code>.ungban</code>\n"
        "🔴 <code>.gmute</code> · <code>.gdel</code>\n"
        "🔴 <code>.warn</code> / <code>.warns</code>\n"
        "🔴 <code>.tagall</code> · <code>.welcome</code>\n"
        "🔴 <code>.antilink</code> · <code>.antiflood</code>\n"
        "🔴 <code>.antidelete</code> · <code>.locks</code>\n"
        "🔴 <code>.nightmode</code> · <code>.slowmode</code>\n"
        "🔴 <code>.zombies</code> · <code>.rules</code>\n"
        "🔴 <code>.autokick</code>"
    ),
    "scan": (
        "🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣\n"
        "🕵️ <b>USER SCAN + MONGO DP</b>\n"
        "🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣\n\n"
        "🟣 <code>.uinfo</code> / <code>.scan</code>\n"
        "🟣 <code>.dphist</code> · <code>.member</code>\n"
        "🟣 <code>.fwdinfo</code> · <code>.commonlist</code>\n"
        "🥭 <code>.dp</code> / <code>.mongodp</code>\n"
        "🟣 <code>.dpsave</code> · <code>.dplog</code>"
    ),
    "cast": (
        "🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡\n"
        "📢 <b>BROADCAST</b>\n"
        "🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡\n\n"
        "🟡 <code>.broadcast</code> — all chats\n"
        "🟡 <code>.gcast</code> — groups\n"
        "🟡 <code>.dmcast</code> — DMs"
    ),
    "bro": (
        "🩷🩷🩷🩷🩷🩷🩷🩷🩷🩷\n"
        "💕 <b>BRO AUTO-REPLY</b>\n"
        "🩷🩷🩷🩷🩷🩷🩷🩷🩷🩷\n\n"
        "🩷 <code>.bro</code> · <code>.brodm</code>\n"
        "🩷 <code>.brogroup</code> · <code>.unbro</code>\n"
        "🩷 <code>.brolist</code>"
    ),
    "owner": (
        "🩵🩵🩵🩵🩵🩵🩵🩵🩵🩵\n"
        "👑 <b>OWNER / SUDO</b>\n"
        "🩵🩵🩵🩵🩵🩵🩵🩵🩵🩵\n\n"
        "🩵 <code>.addsudo</code> · <code>.delsudo</code>\n"
        "🩵 <code>.sudolist</code> · <code>.clone</code>\n"
        "🩵 <code>.track</code> · <code>.ghost</code>"
    ),
    "pm": (
        "🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡\n"
        "🛡 <b>PM GUARD</b>\n"
        "🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡\n\n"
        "🧡 <code>.approve</code> / <code>.unapprove</code>\n"
        "🧡 <code>.pmguard</code> · <code>.secretlog</code>"
    ),
    "eco": (
        "💚💚💚💚💚💚💚💚💚💚\n"
        "💰 <b>ECONOMY</b>\n"
        "💚💚💚💚💚💚💚💚💚💚\n\n"
        "💚 <code>.bal</code> · <code>.daily</code>\n"
        "💚 <code>.rob</code> · <code>.pay</code>"
    ),
    "tools": (
        "🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵\n"
        "🛠 <b>TOOLS</b>\n"
        "🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵\n\n"
        "🔵 <code>.afk</code> · <code>.id</code> · <code>.info</code>\n"
        "🔵 <code>.qr</code> · <code>.paste</code> · <code>.kang</code>"
    ),
    "system": (
        "⚪️⚪️⚪️⚪️⚪️⚪️⚪️⚪️⚪️⚪️\n"
        "⚙️ <b>SYSTEM</b>\n"
        "⚪️⚪️⚪️⚪️⚪️⚪️⚪️⚪️⚪️⚪️\n\n"
        "⚪️ <code>.ping</code> · <code>.alive</code>\n"
        "⚪️ <code>.help</code> / <code>.menu</code>\n"
        f"💎 <b>{BOT_NAME or 'Yashika'}</b> · Pure Userbot"
    ),
    "deploy": (
        "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀\n"
        "🚀 <b>DEPLOY</b>\n"
        "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀\n\n"
        "Railway · Render · Heroku · Koyeb\n\n"
        "🔑 <code>API_ID</code> <code>API_HASH</code>\n"
        "🔑 <code>STRING_SESSION</code> <code>OWNER_ID</code>"
    ),
}

PAGE_COLOR = {
    "vc": "🟢",
    "mod": "🔴",
    "scan": "🟣",
    "cast": "🟡",
    "bro": "🩷",
    "owner": "🩵",
    "pm": "🧡",
    "eco": "💚",
    "tools": "🔵",
    "system": "⚪️",
    "deploy": "🚀",
}


async def _allowed(uid: int, client) -> bool:
    try:
        if OWNER_ID and uid == OWNER_ID:
            return True
        if uid in SUDO_USERS:
            return True
        me = await client.get_me()
        return bool(me and uid == me.id)
    except Exception:
        return False


async def _send_help(message: Message):
    caption = HOME_CAPTION
    markup = main_buttons()
    # Prefer text first (most reliable); photo optional
    try:
        await message.reply_text(
            caption, reply_markup=markup, disable_web_page_preview=True
        )
        return
    except Exception as e:
        print(f"[help] reply_text failed: {e}")
    photo = HELP_BANNER
    if START_PIC and str(START_PIC).startswith("http"):
        photo = START_PIC
    try:
        await message.reply_photo(photo, caption=caption, reply_markup=markup)
    except Exception as e:
        print(f"[help] reply_photo failed: {e}")


# Primary: command filter + sudo (outgoing always allowed in sudo_only)
@app.on_message(
    filters.command(["help", "cmds", "commands", "menu"], prefixes=PREFIXES)
)
@sudo_only
async def help_cmd(client, message: Message):
    await _send_help(message)


# Backup: plain text match on own account (if command filter misses)
@app.on_message(
    filters.me
    & filters.text
    & filters.regex(r"^[.!](help|menu|cmds|commands)(@\w+)?(\s|$)"),
    group=1,
)
async def help_cmd_backup(client, message: Message):
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
            pass
        await query.answer()
        return

    if data == "home":
        try:
            if query.message.photo:
                await query.message.edit_caption(
                    HOME_CAPTION, reply_markup=main_buttons()
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

    color = PAGE_COLOR.get(data, "🟣")
    kb = back_buttons(color)

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
