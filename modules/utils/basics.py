"""
Core userbot: .ping .alive .id .help .uptime
Buttons from help_menu — same as bot.
"""
import asyncio
import time

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from core.clients import app
from config import BOT_NAME, OWNER_USERNAME
from modules.owner import sudoers
from modules.owner.sudoers import ub_cmd
from modules.utils.help_menu import (
    home_text, main_kb, uptime, handle_help_callback, NAME, OWNER_TAG,
)

_START = time.time()


async def _reply(message: Message, text: str, reply_markup=None):
    if app is None:
        return
    try:
        await message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        print(f"[basics] reply fail: {e}")
        try:
            await app.send_message(message.chat.id, text, reply_markup=reply_markup)
        except Exception as e2:
            print(f"[basics] send fail: {e2}")


if app is not None:

    @app.on_message(ub_cmd("ping"), group=-50)
    async def cmd_ping(client, message: Message):
        t0 = time.time()
        try:
            m = await message.reply_text("💎 …")
        except Exception as e:
            print(f"[ping] {e}")
            return
        ms = (time.time() - t0) * 1000
        try:
            prem = "✅" if getattr(await client.get_me(), "is_premium", False) else "❌"
        except Exception:
            prem = "?"
        try:
            await m.edit_text(
                f"🏓 <b>PONG</b>\n"
                f"⚡ <code>{ms:.0f}ms</code>\n"
                f"⏱ <code>{uptime()}</code>\n"
                f"💎 Premium: {prem}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📖 Help", callback_data="yh:home")],
                ]),
            )
        except Exception as e:
            print(f"[ping] edit: {e}")

    @app.on_message(ub_cmd("alive"), group=-50)
    async def cmd_alive(client, message: Message):
        try:
            me = await client.get_me()
            prem = "✅" if getattr(me, "is_premium", False) else "❌"
            un = f"@{me.username}" if me.username else "—"
        except Exception:
            prem, un = "?", "—"
        await _reply(
            message,
            f"💚 <b>{NAME}</b> ALIVE\n"
            f"👤 {un}\n💎 {prem}\n"
            f"⏱ <code>{uptime()}</code>\n👑 {OWNER_TAG}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🏓 System", callback_data="yh:sys"),
                    InlineKeyboardButton("📖 Help", callback_data="yh:home"),
                ],
            ]),
        )

    @app.on_message(ub_cmd("id"), group=-50)
    async def cmd_id(client, message: Message):
        cid = message.chat.id if message.chat else 0
        uid = (
            message.reply_to_message.from_user.id
            if message.reply_to_message and message.reply_to_message.from_user
            else (message.from_user.id if message.from_user else sudoers.ME_ID)
        )
        await _reply(
            message,
            f"🆔 Chat: <code>{cid}</code>\n👤 User: <code>{uid}</code>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ℹ️ Info", callback_data="yh:info")],
            ]),
        )

    @app.on_message(ub_cmd("uptime"), group=-50)
    async def cmd_uptime(client, message: Message):
        await _reply(
            message,
            f"⏱ Uptime: <code>{uptime()}</code>",
            reply_markup=main_kb(),
        )

    @app.on_message(ub_cmd("help", "menu", "cmds", "commands"), group=-50)
    async def cmd_help(client, message: Message):
        await _reply(message, home_text(), reply_markup=main_kb())

    @app.on_message(ub_cmd("helpanim"), group=-50)
    async def cmd_helpanim(client, message: Message):
        frames = ["✨", "💎", "✨💎✨", f"💎 <b>{NAME}</b> 💎"]
        try:
            m = await message.reply_text(frames[0])
            for f in frames[1:]:
                await asyncio.sleep(0.25)
                await m.edit_text(f)
            await asyncio.sleep(0.3)
            await m.delete()
        except Exception:
            pass
        await _reply(message, home_text(), reply_markup=main_kb())

    @app.on_callback_query(filters.regex(r"^yh:"))
    async def help_buttons_ub(client, cq: CallbackQuery):
        await handle_help_callback(cq)

    print("[basics] userbot HELP + buttons ON")
else:
    print("[basics] skip — no STRING_SESSION / app")
