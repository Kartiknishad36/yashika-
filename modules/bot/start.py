"""Bot /start /help /ping — same command buttons as userbot"""
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from core.clients import bot
from config import BOT_NAME, OWNER_ID, OWNER_USERNAME, SUPPORT_CHAT, UPDATE_CHANNEL
from core.autodelete import auto_delete_msg
from modules.utils.help_menu import home_text, main_kb, handle_help_callback, uptime

if bot is None:
    print("[bot.start] skip")
else:

    def _start_kb():
        rows = [
            [
                InlineKeyboardButton("📖 Full Commands", callback_data="yh:home"),
                InlineKeyboardButton("🔐 Login", callback_data="login_start"),
            ],
        ]
        if SUPPORT_CHAT:
            rows.append([InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT)])
        if UPDATE_CHANNEL:
            rows.append([InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL)])
        return InlineKeyboardMarkup(rows)

    @bot.on_message(filters.command(["start"]) & filters.private)
    async def cmd_start(client, message: Message):
        name = message.from_user.first_name if message.from_user else "User"
        text = (
            f"╔══════════════════════════╗\n"
            f"║ ✨💎 <b>{(BOT_NAME or 'Yashika').upper()}</b> 💎✨ ║\n"
            f"╚══════════════════════════╝\n\n"
            f"Hey <b>{name}</b>\n\n"
            f"• <code>/help</code> — saari commands + buttons\n"
            f"• <code>/login</code> — naya account session\n"
            f"• <code>/ping</code> — bot alive\n"
            f"• Owner: <code>{OWNER_ID}</code>\n"
        )
        if OWNER_USERNAME:
            text += f"• @{OWNER_USERNAME}\n"
        text += (
            f"\n⏱ <code>{uptime()}</code>\n"
            f"User account pe: <code>.help</code> (STRING_SESSION)"
        )
        await message.reply_text(text, reply_markup=_start_kb())

    @bot.on_message(filters.command(["help", "menu", "cmds"]))
    async def cmd_help(client, message: Message):
        # Owner gets full menu anywhere; others only private soft menu
        uid = message.from_user.id if message.from_user else 0
        if OWNER_ID and uid == OWNER_ID:
            await message.reply_text(home_text(), reply_markup=main_kb())
        elif message.chat and message.chat.type.name == "PRIVATE":
            await message.reply_text(home_text(), reply_markup=main_kb())
        else:
            await message.reply_text(
                f"<b>{BOT_NAME}</b> — DM me <code>/help</code>",
                reply_markup=_start_kb(),
            )

    @bot.on_message(filters.command(["ping"]))
    async def cmd_ping(client, message: Message):
        await message.reply_text(
            f"🏓 <b>Pong!</b>\n⏱ <code>{uptime()}</code>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Help", callback_data="yh:home")],
            ]),
        )

    @bot.on_callback_query(filters.regex(r"^yh:"))
    async def cb_help_bot(client, cq):
        await handle_help_callback(cq)

    @bot.on_callback_query(filters.regex("^help_main$"))
    async def cb_help_legacy(client, cq):
        await cq.message.edit_text(home_text(), reply_markup=main_kb())
        await cq.answer()

    print("[bot.start] premium HELP buttons ready")
