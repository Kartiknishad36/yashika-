"""
Premium /start for BOT YASHIKA 
Userbot handlers stay on `app`; this runs only on `bot`.
"""
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from core.clients import bot
from config import (
    BOT_NAME,
    BOT_USERNAME,
    OWNER_ID,
    OWNER_USERNAME,
    SUPPORT_CHAT,
    UPDATE_CHANNEL,
)

if bot is None:
    raise RuntimeError("modules.bot.start requires BOT_TOKEN in .env")

# In-memory stats (File 4 economy DB se replace hoga)
_STATS: dict[int, dict] = {}


def get_stats(uid: int) -> dict:
    if uid not in _STATS:
        _STATS[uid] = {"balance": 300, "rank": 14522, "gems": 0.0, "kills": 0}
    st = _STATS[uid]
    st["rank"] = max(1, 200000 - int(st["balance"]) // 1000000000)
    return st


def start_keyboard() -> InlineKeyboardMarkup:
    uname = (BOT_USERNAME or "Music_yaa_bot").lstrip("@")
    add_url = f"https://t.me/{uname}?startgroup=true"

    owner_btn = None
    if OWNER_USERNAME:
        owner_btn = InlineKeyboardButton(
            "👤 OWNER", url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}"
        )
    elif OWNER_ID:
        owner_btn = InlineKeyboardButton("👤 OWNER", url=f"tg://user?id={OWNER_ID}")

    rows = [
        [InlineKeyboardButton(f"☘️ {BOT_NAME.upper()} FEATURES", callback_data="ui_features")],
    ]
    if owner_btn:
        rows.append([owner_btn])
    rows.extend(
        [
            [
                InlineKeyboardButton("👥 GROUPS", url=SUPPORT_CHAT or "https://t.me"),
                InlineKeyboardButton("🕊 PROMOTER", callback_data="ui_promoter"),
            ],
            [
                InlineKeyboardButton("📢 UPDATES", url=UPDATE_CHANNEL or "https://t.me"),
                InlineKeyboardButton("🎮 GAMES", callback_data="ui_games"),
            ],
            [InlineKeyboardButton("➕ ADD ME TO YOUR GROUP", url=add_url)],
        ]
    )
    return InlineKeyboardMarkup(rows)


def start_caption(name: str, st: dict) -> str:
    return (
        f"💙 <b>HIEEEE {name.upper()}</b>\n"
        f"I'M <b>{BOT_NAME.upper()}</b> — A GAMING AND CHATTING GIRL HAVING "
        f"LOTS OF FEATURES TO ENGAGE YOUR GROUP.\n\n"
        f"<blockquote>"
        f"📊 <b>YOUR STATS:</b>\n"
        f"💰 BALANCE: {st['balance']}\n"
        f"🏆 RANK: {st['rank']}\n"
        f"💎 GEMS: {st['gems']:.2f}\n"
        f"⚔ KILLS: {st['kills']}"
        f"</blockquote>\n\n"
        f"<b>🎛 HOW TO PLAY?</b>\n"
        f"💵 /bal — CHECK YOUR STATS\n"
        f"🖼 /pfp — CHECK YOUR PFP\n"
        f"🎁 /daily — GET FREE COINS\n"
        f"🛡 /protect — SAVE YOURSELF\n"
        f"⚔ /kill & /rob — LOOT OTHERS\n\n"
        f"👇 <b>CHOOSE AN OPTION BELOW :</b>"
    )


@bot.on_message(filters.command("start") & filters.private)
async def bot_start(client, message: Message):
    user = message.from_user
    if not user:
        return
    st = get_stats(user.id)
    await message.reply_text(
        start_caption(user.first_name or "USER", st),
        reply_markup=start_keyboard(),
        disable_web_page_preview=True,
    )


@bot.on_callback_query(filters.regex(r"^ui_"))
async def ui_callbacks(client, query: CallbackQuery):
    data = query.data
    await query.answer()

    if data == "ui_features":
        await query.message.reply_text(
            f"<b>✨ {BOT_NAME} FEATURES</b>\n\n"
            f"🎵 Music / VC (userbot: .play .vplay)\n"
            f"🎮 Games — /dice, /couple, /TD, /bomb\n"
            f"💰 Economy — /bal /daily /rob /kill\n"
            f"💕 Fun — /kiss /hug /slap /couple\n"
            f"🛡 Group tools — /welcome, mod\n\n"
            f"Group mein add karke try karo."
        )
    elif data == "ui_games":
        await query.message.reply_text(
            "<b>🎮 GAMES</b>\n\n"
            "/dice /dart /basket — Telegram games\n"
            "/couple — today's cute couple\n"
            "/td — truth & dare\n"
            "/bomb — bomb game (soon)\n"
            "/chain — word chain (soon)"
        )
    elif data == "ui_promoter":
        await query.answer("Contact owner for promoter access.", show_alert=True)
