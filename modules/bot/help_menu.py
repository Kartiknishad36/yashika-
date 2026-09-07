"""Callback help pages for start UI."""
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from core.clients import bot
from config import BOT_NAME

if bot is None:
    raise RuntimeError("modules.bot.help_menu needs BOT_TOKEN")


def _back_kb():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("« Back", callback_data="ui_features")]]
    )


@bot.on_callback_query(filters.regex(r"^help_"))
async def help_pages(client, query: CallbackQuery):
    await query.answer()
    data = query.data

    pages = {
        "help_music": (
            f"<b>🎵 Music ({BOT_NAME})</b>\n\n"
            f"Userbot account se:\n"
            f".play .vplay .pause .resume .skip .stop\n"
            f".vcinfo on/off — VC join-leave alerts"
        ),
        "help_eco": (
            "<b>💰 Economy</b>\n\n"
            "/bal /daily /pfp\n"
            "/protect /rob /kill"
        ),
        "help_games": (
            "<b>🎮 Games</b>\n\n"
            "/couple /td /truth /dare\n"
            "/dice /dart /basket /slot\n"
            "/bomb /bombstart\n"
            "/chain /riddle /answer\n"
            "/chase /chasestart /catch\n"
            "/ludo join|start|roll"
        ),
        "help_fun": (
            "<b>💕 Fun</b>\n\n"
            "/kiss /hug /slap /kick /pat /sex /gif\n"
            "(reply to user)"
        ),
    }

    text = pages.get(data, "Unknown")
    await query.message.edit_text(text, reply_markup=_back_kb())
