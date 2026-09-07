""" /td  |  /truth  |  /dare """
import random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from core.clients import bot

if bot is None:
    raise RuntimeError("modules.games.truth_dare needs BOT_TOKEN")

PREFIXES = ["/", ".", "!"]

TRUTHS = [
    "Sabse awkward crush kaun tha?",
    "Last lie kab boli?",
    "Group mein sabse funny kaun?",
    "Kabhi ghost kiya kisi ko?",
    "Sabse weird dream kya tha?",
    "Phone unlock karke dikhao (joke — mat dikhana)?",
    "Ek secret batao jo group nahi jaanta.",
    "Sabse zyada miss kisse karte ho?",
    # ADD MORE HERE
]

DARES = [
    "Voice note mein gaana gao.",
    "Status pe 'I love this group' likho 1 hour.",
    "Kiss emoji 10 baar bhejo.",
    "Admin ko good morning bolo (agar so rahe hon toh mat jagana).",
    "Apna pehla message is group mein dhundo.",
    "Random member ko compliment do.",
    "30 second ke liye CAPS LOCK ON likho.",
    # ADD MORE HERE
]


def _td_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔵 Truth", callback_data="td_truth"),
                InlineKeyboardButton("🔴 Dare", callback_data="td_dare"),
            ]
        ]
    )


@bot.on_message(filters.command(["td", "truthdare"], prefixes=PREFIXES))
async def td_menu(client, message: Message):
    await message.reply_text(
        "🎲 <b>Truth & Dare</b>\nChoose:",
        reply_markup=_td_keyboard(),
    )


@bot.on_message(filters.command("truth", prefixes=PREFIXES))
async def truth_cmd(client, message: Message):
    await message.reply_text(f"🔵 <b>Truth:</b>\n{random.choice(TRUTHS)}")


@bot.on_message(filters.command("dare", prefixes=PREFIXES))
async def dare_cmd(client, message: Message):
    await message.reply_text(f"🔴 <b>Dare:</b>\n{random.choice(DARES)}")


@bot.on_callback_query(filters.regex(r"^td_"))
async def td_cb(client, query: CallbackQuery):
    await query.answer()
    if query.data == "td_truth":
        await query.message.reply_text(f"🔵 <b>Truth:</b>\n{random.choice(TRUTHS)}")
    else:
        await query.message.reply_text(f"🔴 <b>Dare:</b>\n{random.choice(DARES)}")
