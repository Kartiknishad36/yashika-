"""
.joke .quote .roast .fact .pickup .compliment
"""
import random

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

JOKES = [
    "Teacher: Late why? Student: Sir, traffic. Teacher: School ke andar? Student: Idea traffic.",
    "Debug: only you and God know. After a week: only God.",
    "Girlfriend status: typing… last seen 2 hours ago.",
]
QUOTES = [
    "Stay hungry, stay foolish.",
    "Consistency beats talent when talent doesn't work hard.",
    "Small steps every day.",
]
ROASTS = [
    "Teri personality buffering pe atak gayi hai.",
    "Brain 404 Not Found.",
    "Even calculator rejects your logic.",
]
FACTS = [
    "Honey kabhi expire nahi hota.",
    "Octopus ke 3 dil hote hain.",
    "Telegram stickers animated 2020 ke baad boom hue.",
]
PICKUPS = [
    "Are you WiFi? Because I feel connected.",
    "Tera smile full battery hai kya?",
]
COMPLIMENTS = [
    "Aaj ka energy solid hai.",
    "Style on point.",
    "Confidence dikh raha hai.",
]


def _target(message: Message) -> str:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.mention
    return "bhai"


@app.on_message(filters.command("joke", prefixes=PREFIXES))
@sudo_only
async def joke_cmd(client, message: Message):
    await message.reply_text(f"😂 {random.choice(JOKES)}")


@app.on_message(filters.command("quote", prefixes=PREFIXES))
@sudo_only
async def quote_cmd(client, message: Message):
    await message.reply_text(f"💬 <i>{random.choice(QUOTES)}</i>")


@app.on_message(filters.command("roast", prefixes=PREFIXES))
@sudo_only
async def roast_cmd(client, message: Message):
    await message.reply_text(f"🔥 {_target(message)}, {random.choice(ROASTS)}")


@app.on_message(filters.command("fact", prefixes=PREFIXES))
@sudo_only
async def fact_cmd(client, message: Message):
    await message.reply_text(f"📌 {random.choice(FACTS)}")


@app.on_message(filters.command(["pickup", "flirt"], prefixes=PREFIXES))
@sudo_only
async def pickup_cmd(client, message: Message):
    await message.reply_text(f"😉 {random.choice(PICKUPS)}")


@app.on_message(filters.command("compliment", prefixes=PREFIXES))
@sudo_only
async def compliment_cmd(client, message: Message):
    await message.reply_text(f"✨ {_target(message)}, {random.choice(COMPLIMENTS)}")
