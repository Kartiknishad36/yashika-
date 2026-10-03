"""
👑 YASHIKA — PREMIUM COLOUR HELP MENU (TEXT + BUTTONS)
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
    OWNER_ID,
)

PREFIXES = [".", "!"]
REPO_URL = "https://github.com/Kartiknishad36/yashika-"


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
                InlineKeyboardButton("🟢 MUSIC", callback_data="yh:vc"),
                InlineKeyboardButton("🔴 MOD", callback_data="yh:mod"),
            ],
            [
                InlineKeyboardButton("🟣 SCAN", callback_data="yh:scan"),
                InlineKeyboardButton("🟡 CAST", callback_data="yh:cast"),
            ],
            [
                InlineKeyboardButton("🩷 BRO", callback_data="yh:bro"),
                InlineKeyboardButton("🩵 OWNER", callback_data="yh:owner"),
            ],
            [
                InlineKeyboardButton("🧡 PM", callback_data="yh:pm"),
                InlineKeyboardButton("💚 ECO", callback_data="yh:eco"),
            ],
            [
                InlineKeyboardButton("🔵 TOOLS", callback_data="yh:tools"),
                InlineKeyboardButton("🌹 FUN", callback_data="yh:fun"),
            ],
            [
                InlineKeyboardButton("⚪️ SYSTEM", callback_data="yh:system"),
            ],
            [
                InlineKeyboardButton("💬 SUPPORT", url=_support()),
                InlineKeyboardButton("👤 OWNER", url=_owner_url()),
            ],
            [
                InlineKeyboardButton("❌ CLOSE", callback_data="yh:close"),
            ],
        ]
    )


def back_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔙 BACK", callback_data="yh:home")],
            [InlineKeyboardButton("❌ CLOSE", callback_data="yh:close")],
        ]
    )


HOME = (
    f"👑 <b>{BOT_NAME or 'YASHIKA'} COMMAND CENTER</b>\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"✨ Premium Userbot Menu\n\n"
    f"🟢 MUSIC · 🔴 MOD · 🟣 SCAN\n"
    f"🟡 CAST · 🩷 BRO · 🩵 OWNER\n"
    f"🧡 PM · 💚 ECO · 🔵 TOOLS\n"
    f"🌹 FUN · ⚪️ SYSTEM\n\n"
    f"📌 Prefix: <code>.</code> or <code>!</code>\n"
    f"🔐 Own account / OWNER / SUDO\n\n"
    f"Quick: <code>.ping</code> <code>.rose</code> <code>.cat</code>"
)

HELP_DATA = {
    "vc": (
        "🟢 <b>MUSIC / VC</b>\n━━━━━━━━━━━━\n"
        "<code>.play</code> <code>.vply</code> <code>.skip</code>\n"
        "<code>.stop</code> <code>.pause</code> <code>.resume</code>\n"
        "<code>.queue</code> <code>.end</code>"
    ),
    "mod": (
        "🔴 <b>MOD</b>\n━━━━━━━━━━━━\n"
        "<code>.gban</code> <code>.ungban</code> <code>.gmute</code>\n"
        "<code>.warn</code> <code>.tagall</code> <code>.welcome</code>\n"
        "<code>.antilink</code> <code>.antiflood</code> <code>.locks</code>"
    ),
    "scan": (
        "🟣 <b>SCAN + DP</b>\n━━━━━━━━━━━━\n"
        "<code>.uinfo</code> <code>.scan</code> <code>.dphist</code>\n"
        "<code>.dp</code> <code>.dpsave</code> <code>.dplog</code>\n"
        "<code>.fwdinfo</code> <code>.commonlist</code>"
    ),
    "cast": (
        "🟡 <b>CAST</b>\n━━━━━━━━━━━━\n"
        "<code>.broadcast</code> <code>.gcast</code> <code>.dmcast</code>"
    ),
    "bro": (
        "🩷 <b>BRO</b>\n━━━━━━━━━━━━\n"
        "<code>.bro</code> <code>.brodm</code> <code>.brogroup</code>\n"
        "<code>.unbro</code> <code>.brolist</code>"
    ),
    "owner": (
        "🩵 <b>OWNER</b>\n━━━━━━━━━━━━\n"
        "<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>\n"
        "<code>.clone</code> <code>.track</code> <code>.ghost</code>"
    ),
    "pm": (
        "🧡 <b>PM</b>\n━━━━━━━━━━━━\n"
        "<code>.approve</code> <code>.unapprove</code> <code>.pmguard</code>"
    ),
    "eco": (
        "💚 <b>ECO</b>\n━━━━━━━━━━━━\n"
        "<code>.bal</code> <code>.daily</code> <code>.rob</code> <code>.pay</code>"
    ),
    "tools": (
        "🔵 <b>TOOLS</b>\n━━━━━━━━━━━━\n"
        "<code>.afk</code> <code>.id</code> <code>.info</code>\n"
        "<code>.qr</code> <code>.paste</code> <code>.kang</code>"
    ),
    "fun": (
        "🌹 <b>FUN</b>\n━━━━━━━━━━━━\n"
        "<code>.rose</code> <code>.cat</code> <code>.heart</code>\n"
        "<code>.hacker</code> <code>.butterfly</code> <code>.myson</code>\n"
        "<code>.error</code>"
    ),
    "system": (
        "⚪️ <b>SYSTEM</b>\n━━━━━━━━━━━━\n"
        "<code>.ping</code> <code>.alive</code> <code>.help</code> <code>.menu</code>\n"
        "<code>.uptime</code> <code>.restart</code>"
    ),
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
    try:
        await message.reply_text(
            HOME, reply_markup=main_buttons(), disable_web_page_preview=True
        )
    except Exception as e:
        print(f"[help] fail: {e}")
        try:
            await message.reply_text(HOME)
        except Exception as e2:
            print(f"[help] fail2: {e2}")


@app.on_message(
    filters.command(["help", "cmds", "commands", "menu"], prefixes=PREFIXES)
)
@sudo_only
async def help_cmd(client, message: Message):
    await _send_help(message)


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
        await query.answer("❌ OWNER / sudo only", show_alert=True)
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
            await query.message.edit_text(
                HOME, reply_markup=main_buttons(), disable_web_page_preview=True
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
        await query.message.edit_text(
            text, reply_markup=back_buttons(), disable_web_page_preview=True
        )
    except Exception:
        pass
    await query.answer()
