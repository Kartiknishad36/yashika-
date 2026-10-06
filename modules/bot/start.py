"""Bot /start /help /ping"""
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from core.clients import bot
from config import BOT_NAME, OWNER_ID, OWNER_USERNAME, SUPPORT_CHAT, UPDATE_CHANNEL
from core.autodelete import auto_delete_msg

if bot is None:
    print("[bot.start] skip")
else:

    def _kb():
        rows = [[
            InlineKeyboardButton("🔐 Login", callback_data="login_start"),
            InlineKeyboardButton("📋 Help", callback_data="help_main"),
        ]]
        if SUPPORT_CHAT:
            rows.append([InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT)])
        if UPDATE_CHANNEL:
            rows.append([InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL)])
        return InlineKeyboardMarkup(rows)

    HELP = (
        f"<b>✦ {BOT_NAME} BOT ✦</b>\n\n"
        f"<b>Login</b>\n"
        f"/login — naya account\n"
        f"/cancel — cancel\n"
        f"/sessions — list\n\n"
        f"<b>Basic</b>\n"
        f"/start /help /ping\n\n"
        f"Userbot: STRING_SESSION set ho to account se <code>.help</code>"
    )

    @bot.on_message(filters.command(["start"]) & filters.private)
    async def cmd_start(client, message: Message):
        name = message.from_user.first_name if message.from_user else "User"
        text = (
            f"<b>✦ {BOT_NAME} ✦</b>\n\n"
            f"Hey <b>{name}</b>\n\n"
            f"• /login se account add karo\n"
            f"• Session Log Group me save\n"
            f"• Owner: <code>{OWNER_ID}</code>\n"
        )
        if OWNER_USERNAME:
            text += f"• @{OWNER_USERNAME}\n"
        await message.reply_text(text, reply_markup=_kb())
        await auto_delete_msg(message, 3)

    @bot.on_message(filters.command(["help"]) & filters.private)
    async def cmd_help(client, message: Message):
        await message.reply_text(HELP, reply_markup=_kb())
        await auto_delete_msg(message, 3)

    @bot.on_message(filters.command(["ping"]) & filters.private)
    async def cmd_ping(client, message: Message):
        await message.reply_text("🏓 <b>Pong!</b>")
        await auto_delete_msg(message, 2)

    @bot.on_callback_query(filters.regex("^help_main$"))
    async def cb_help(client, cq):
        await cq.message.edit_text(HELP, reply_markup=_kb())
        await cq.answer()

    print("[bot.start] ready")
