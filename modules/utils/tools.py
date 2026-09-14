"""
.calc .time .weather .translate .short
"""
import re
from datetime import datetime
from urllib.parse import quote

import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


@app.on_message(filters.command(["calc", "calculate"], prefixes=PREFIXES))
@sudo_only
async def calc_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.calc 2+2*5</code>")
        return
    expr = message.text.split(None, 1)[1].strip()
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expr):
        await message.reply_text("❌ Sirf numbers / + - * / ( )")
        return
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        await message.reply_text(f"🧮 <code>{expr}</code> = <b>{result}</b>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command(["time", "date"], prefixes=PREFIXES))
@sudo_only
async def time_cmd(client, message: Message):
    now = datetime.now()
    await message.reply_text(
        f"🕒 <b>{now.strftime('%I:%M:%S %p')}</b>\n"
        f"📅 {now.strftime('%A, %d %B %Y')}"
    )


@app.on_message(filters.command("weather", prefixes=PREFIXES))
@sudo_only
async def weather_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.weather Delhi</code>")
        return
    city = message.text.split(None, 1)[1].strip()
    url = f"https://wttr.in/{quote(city)}?format=3"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                text = (await r.text()).strip()
        await message.reply_text(f"🌤 <b>Weather</b>\n<code>{text}</code>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command(["translate", "tr"], prefixes=PREFIXES))
@sudo_only
async def translate_cmd(client, message: Message):
    """
    .tr hi hello
    .tr en <reply>
    """
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        lang = message.command[1] if len(message.command) > 1 else "hi"
        text = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) >= 3:
        lang = message.command[1]
        text = message.text.split(None, 2)[2]
    else:
        await message.reply_text(
            "Usage:\n<code>.tr hi Hello</code>\nReply + <code>.tr en</code>"
        )
        return

    api = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl=auto&tl={quote(lang)}&dt=t&q={quote(text[:2000])}"
    )
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(api, timeout=aiohttp.ClientTimeout(total=20)) as r:
                data = await r.json()
        out = "".join(part[0] for part in data[0] if part and part[0])
        await message.reply_text(f"🌐 <b>{lang}</b>\n{out}")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command(["short", "shorten"], prefixes=PREFIXES))
@sudo_only
async def short_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: <code>.short https://example.com</code>")
        return
    url = message.command[1]
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"https://tinyurl.com/api-create.php?url={quote(url)}",
                timeout=aiohttp.ClientTimeout(total=15),
            ) as r:
                short = (await r.text()).strip()
        await message.reply_text(f"🔗 {short}")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
