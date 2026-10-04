"""
basics — ping / alive / id / help
"""
import time

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME, OWNER_ID
from modules.owner.sudoers import sudo_only, SUDO_USERS

PREFIXES = [".", "!"]


def cmd(*names):
    return filters.command(list(names), prefixes=PREFIXES)


@app.on_message(cmd("ping"))
@sudo_only
async def ping_cmd(client, message: Message):
    start = time.time()
    try:
        msg = await message.reply_text("Pinging…")
        ms = (time.time() - start) * 1000
        await msg.edit_text(f"<b>Pong!</b> <code>{ms:.0f}ms</code>")
    except Exception as e:
        print(f"[ping] {e}")


@app.on_message(cmd("alive"))
@sudo_only
async def alive_cmd(client, message: Message):
    try:
        await message.reply_text(
            f"<b>{BOT_NAME or 'Yashika'}</b> is online.\n"
            f"<code>.help</code> — commands\n"
            f"<code>.ping</code> — latency"
        )
    except Exception as e:
        print(f"[alive] {e}")


@app.on_message(cmd("id"))
@sudo_only
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
        f"<code>.warn</code> <code>.tagall</code> <code>.welcome</code>\n"
        f"<code>.antilink</code> <code>.antiflood</code> <code>.locks</code>\n\n"
        f"<b>Scan / DP</b>\n"
        f"<code>.uinfo</code> <code>.scan</code> <code>.dp</code> "
        f"<code>.dpsave</code> <code>.dplog</code>\n\n"
        f"<b>Cast</b>\n"
        f"<code>.broadcast</code> <code>.gcast</code> <code>.dmcast</code>\n\n"
        f"<b>Bro</b>\n"
        f"<code>.bro</code> <code>.brodm</code> <code>.brogroup</code> "
        f"<code>.unbro</code> <code>.brolist</code>\n\n"
        f"<b>Login</b> (owner/sudo)\n"
        f"<code>.login</code> <code>.addsession</code> "
        f"<code>.cancellogin</code> <code>.mylogin</code>\n\n"
        f"<b>Owner</b>\n"
        f"<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>\n\n"
        f"<b>PM</b>\n"
        f"<code>.approve</code> <code>.unapprove</code> <code>.verify</code>\n\n"
        f"<b>AutoReply</b> (per chat)\n"
        f"<code>.autoreply on</code> / <code>.autoreply off</code>\n"
        f"<code>.autoreply set text</code>\n\n"
        f"<b>VC Welcome</b>\n"
        f"<code>.vcwelcome on</code> / <code>off</code> / <code>test</code>\n\n"
        f"<b>Fun</b>\n"
        f"<code>.rose</code> <code>.cat</code> <code>.heart</code> <code>.hacker</code>\n\n"
        f"<b>System</b>\n"
        f"<code>.ping</code> <code>.alive</code> <code>.id</code> "
        f"<code>.help</code> <code>.uptime</code> <code>.restart</code>\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Prefix: <code>.</code> or <code>!</code>"
    )


HELP_PAGES = {
    "vc": "<b>Music/VC</b>\n<code>.play .vply .skip .stop .pause .resume .queue</code>",
    "mod": "<b>Mod</b>\n<code>.gban .ungban .gmute .warn .tagall .welcome .antilink</code>",
    "scan": "<b>Scan</b>\n<code>.uinfo .scan .dp .dpsave .dplog</code>",
    "cast": "<b>Cast</b>\n<code>.broadcast .gcast .dmcast</code>",
    "bro": "<b>Bro</b>\n<code>.bro .brodm .brogroup .unbro .brolist</code>",
    "login": "<b>Login</b>\n<code>.login</code> phone→OTP→2FA\n<code>.addsession</code> <code>.cancellogin</code>",
    "owner": "<b>Owner</b>\n<code>.addsudo .delsudo .sudolist .clone .track</code>",
    "pm": "<b>PM</b>\n<code>.approve .unapprove .verify</code>",
    "fun": "<b>Fun</b>\n<code>.rose .cat .heart .hacker</code>",
    "system": "<b>System</b>\n<code>.ping .alive .id .help .uptime .restart</code>",
    "auto": "<b>AutoReply</b>\n<code>.autoreply on|off</code>\n<code>.autoreply set text</code>",
    "vcwelcome": "<b>VC Welcome</b>\n<code>.vcwelcome on|off|test</code>",
}


async def _send_help(message: Message):
    text = _help_text()
    if message.command and len(message.command) > 1:
        key = message.command[1].lower()
        page = HELP_PAGES.get(key)
        if page:
            text = page
        else:
            text = f"No page: <code>{key}</code>\nUse <code>.help</code>"
    try:
        await message.reply_text(text)
        print("[help] replied OK")
    except Exception as e:
        print(f"[help] reply failed: {e}")
        try:
            await app.send_message(message.chat.id, text)
        except Exception as e2:
            print(f"[help] send failed: {e2}")


@app.on_message(cmd("help", "menu", "cmds", "commands"))
async def help_cmd(client, message: Message):
    """No sudo_only — allow own account always; still check if needed."""
    # allow: outgoing / me / owner / sudo
    ok = getattr(message, "outgoing", False)
    if not ok and message.from_user:
        uid = message.from_user.id
        if OWNER_ID and uid == OWNER_ID:
            ok = True
        elif uid in SUDO_USERS:
            ok = True
        else:
            try:
                me = await client.get_me()
                if me and uid == me.id:
                    ok = True
            except Exception:
                pass
    if not ok:
        return
    await _send_help(message)


# Backup: own account text match (agar command filter miss kare)
@app.on_message(
    filters.me
    & filters.text
    & filters.regex(r"^[.!](help|menu|cmds|commands)(\s|$)")
    ,
    group=1,
)
async def help_backup(client, message: Message):
    await _send_help(message)
