"""
basics — ping / alive / id / help
ONLY these core cmds — baaki modules khud handle karein.
"""
import time

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME, OWNER_ID
from modules.owner.sudoers import SUDO_USERS, ub_cmd


def _help_text() -> str:
    name = BOT_NAME or "Yashika"
    return (
        f"<b>{name} · Command Center</b>\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"<b>Music / VC</b>\n"
        f"<code>.play</code> <code>.vply</code> <code>.skip</code> "
        f"<code>.stop</code> <code>.pause</code> <code>.resume</code> <code>.queue</code>\n\n"
        f"<b>Mod</b>\n"
        f"<code>.gban</code> <code>.ungban</code> <code>.gmute</code> "
        f"<code>.warn</code> <code>.tagall</code> <code>.welcome</code>\n\n"
        f"<b>Scan / DP</b>\n"
        f"<code>.uinfo</code> <code>.scan</code> <code>.dp</code> "
        f"<code>.dpsave</code> <code>.dplog</code>\n\n"
        f"<b>Cast</b>\n"
        f"<code>.broadcast</code> <code>.gcast</code> <code>.dmcast</code>\n\n"
        f"<b>Bro</b>\n"
        f"<code>.bro</code> <code>.unbro</code> <code>.brolist</code>\n\n"
        f"<b>Login</b>\n"
        f"<code>.login</code> <code>.addsession</code> <code>.cancellogin</code>\n\n"
        f"<b>Owner</b>\n"
        f"<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>\n\n"
        f"<b>PM</b>\n"
        f"<code>.approve</code> <code>.unapprove</code> <code>.verify</code>\n\n"
        f"<b>AutoReply</b>\n"
        f"<code>.autoreply on</code> / <code>off</code> / <code>set text</code>\n\n"
        f"<b>VC Welcome</b>\n"
        f"<code>.vcwelcome on</code> / <code>off</code> / <code>test</code>\n\n"
        f"<b>Fun</b>\n"
        f"<code>.rose</code> <code>.cat</code> <code>.heart</code> <code>.hack</code>\n\n"
        f"<b>System</b>\n"
        f"<code>.ping</code> <code>.alive</code> <code>.id</code> <code>.help</code>\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Prefix: <code>.</code> or <code>!</code>"
    )


@app.on_message(ub_cmd("ping") & filters.me)
async def ping_cmd(client, message: Message):
    t0 = time.time()
    try:
        msg = await message.reply_text("Pinging…")
        ms = (time.time() - t0) * 1000
        await msg.edit_text(f"<b>Pong!</b> <code>{ms:.0f}ms</code>")
    except Exception as e:
        print(f"[ping] {e}")


@app.on_message(ub_cmd("alive") & filters.me)
async def alive_cmd(client, message: Message):
    try:
        await message.reply_text(
            f"<b>{BOT_NAME or 'Yashika'}</b> is online.\n"
            f"<code>.help</code> · <code>.ping</code>"
        )
    except Exception as e:
        print(f"[alive] {e}")


@app.on_message(ub_cmd("id") & filters.me)
async def id_cmd(client, message: Message):
    chat_id = message.chat.id if message.chat else 0
    user_id = (
        message.reply_to_message.from_user.id
        if message.reply_to_message and message.reply_to_message.from_user
        else (message.from_user.id if message.from_user else "N/A")
    )
    try:
        await message.reply_text(
            f"<b>Chat:</b> <code>{chat_id}</code>\n"
            f"<b>User:</b> <code>{user_id}</code>"
        )
    except Exception as e:
        print(f"[id] {e}")


@app.on_message(ub_cmd("help", "menu", "cmds", "commands") & filters.me)
async def help_cmd(client, message: Message):
    try:
        await message.reply_text(_help_text())
        print("[help] OK")
    except Exception as e:
        print(f"[help] {e}")
        try:
            await client.send_message(message.chat.id, _help_text())
        except Exception as e2:
            print(f"[help2] {e2}")
