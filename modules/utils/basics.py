"""
basics — ping / alive / id / premium .help / .helpanim
"""
import asyncio
import time

from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME
from modules.owner.sudoers import ub_cmd, ME_ID, OWNER_ID, SUDO_USERS

NAME = BOT_NAME or "Yashika"


async def _safe_send(message: Message, text: str):
    try:
        await message.reply_text(text)
        return True
    except Exception as e:
        print(f"[safe_send reply] {e}")
        try:
            await app.send_message(message.chat.id, text)
            return True
        except Exception as e2:
            print(f"[safe_send send] {e2}")
            plain = (
                text.replace("<b>", "").replace("</b>", "")
                .replace("<i>", "").replace("</i>", "")
                .replace("<code>", "").replace("</code>", "")
            )
            try:
                await app.send_message(message.chat.id, plain)
                return True
            except Exception as e3:
                print(f"[safe_send plain] {e3}")
                return False


@app.on_message(ub_cmd("ping"), group=-5)
async def ping_cmd(client, message: Message):
    if not _allowed(message):
        return
    start = time.time()
    try:
        msg = await message.reply_text("Pinging...")
        ms = (time.time() - start) * 1000
        await msg.edit_text(f"<b>Pong!</b> <code>{ms:.0f}ms</code>")
        print("[ping] OK")
    except Exception as e:
        print(f"[ping] {e}")


@app.on_message(ub_cmd("alive"), group=-5)
async def alive_cmd(client, message: Message):
    if not _allowed(message):
        return
    await _safe_send(
        message,
        f"<b>{NAME}</b> is <b>ALIVE</b>\n"
        f"<code>.help</code> — command center\n"
        f"<code>.ping</code> — speed",
    )


@app.on_message(ub_cmd("id"), group=-5)
async def id_cmd(client, message: Message):
    if not _allowed(message):
        return
    chat_id = message.chat.id if message.chat else 0
    user_id = (
        message.reply_to_message.from_user.id
        if message.reply_to_message and message.reply_to_message.from_user
        else (message.from_user.id if message.from_user else "N/A")
    )
    await _safe_send(
        message,
        f"<b>IDs</b>\nChat: <code>{chat_id}</code>\nUser: <code>{user_id}</code>",
    )


HELP_INDEX = (
    f"<b>YASHIKA COMMAND CENTER</b>\n"
    f"Premium Hybrid Userbot · <b>{NAME}</b>\n"
    f"━━━━━━━━━━━━━━━━━━━━\n\n"
    f"01 MUSIC/VC — <code>.help vc</code>\n"
    f"02 OWNER — <code>.help owner</code>\n"
    f"03 LOGIN — <code>.help login</code>\n"
    f"04 PM SEC — <code>.help pmsec</code>\n"
    f"05 GLOBAL — <code>.help global</code>\n"
    f"06 MOD — <code>.help mod</code>\n"
    f"07 ANTI — <code>.help anti</code>\n"
    f"08 WARN — <code>.help warn</code>\n"
    f"09 CAST — <code>.help cast</code>\n"
    f"10 RAID — <code>.help raid</code>\n"
    f"11 BRO — <code>.help bro</code>\n"
    f"12 WELCOME — <code>.help welcome</code>\n"
    f"13 AFK — <code>.help afk</code>\n"
    f"14 PROTECT — <code>.help protect</code>\n"
    f"15 NOTES — <code>.help notes</code>\n"
    f"16 DL — <code>.help dl</code>\n"
    f"17 MEDIA — <code>.help media</code>\n"
    f"18 GHOST — <code>.help ghost</code>\n"
    f"19 TOOLS — <code>.help tools</code>\n"
    f"20 ANIMS — <code>.help anims</code>\n"
    f"21 FLOWERS — <code>.help flowers</code>\n"
    f"22 SPY — <code>.help spy</code>\n"
    f"23 SYSTEM — <code>.help system</code>\n"
    f"24 FUN — <code>.help fun</code>\n\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"<code>.help page</code> · <code>.helpanim</code>\n"
    f"Prefix: <code>.</code> or <code>!</code>"
)

HELP_PAGES = {
    "vc": "<b>MUSIC / VC</b>\n<code>.play .skip .stop .pause .resume .queue</code>\n<code>.vcwelcome on/off/test</code>",
    "owner": "<b>OWNER</b>\n<code>.addsudo .delsudo .sudolist</code>",
    "login": "<b>LOGIN</b>\n<code>.login .cancellogin .addsession .mylogin</code>",
    "pmsec": "<b>PM SEC</b>\n<code>.secretlog on/off .verify</code>",
    "global": "<b>GLOBAL</b>\n<code>.gban .ungban .gbanlist .gmute</code>",
    "mod": "<b>MOD</b>\n<code>.ban .kick .mute .promote .pin</code>\n<code>.tagall .tagallstop .tagme .tagadmins</code>",
    "anti": "<b>ANTI</b>\n<code>.antilink on/off .antidelete on/off .antiflood</code>",
    "warn": "<b>WARN</b>\n<code>.warn .unwarn .warns .resetwarns</code>",
    "cast": "<b>CAST</b>\n<code>.broadcast .gcast .dmcast</code>",
    "raid": "<b>RAID</b>\n<code>.raid 10 text .spam 10 text</code>",
    "bro": "<b>BRO</b>\n<code>.bro .brodm .brogroup .unbro .brolist</code>",
    "welcome": "<b>WELCOME</b>\n<code>.welcome on/off .setwelcome .vcwelcome</code>",
    "afk": "<b>AFK</b>\n<code>.afk .unafk .back .afkstatus</code>",
    "protect": "<b>PROTECT</b>\n<code>.protect on/off</code>",
    "notes": "<b>NOTES</b>\n<code>.save .get .notes .clearnote</code>",
    "dl": "<b>DL</b>\n<code>.ytmp3 .ytmp4 .song .video .dl</code>",
    "media": "<b>MEDIA</b>\n<code>.kang .tts .dp .dpsave .dplog</code>",
    "ghost": "<b>GHOST</b>\n<code>.ghostmod .vanish .track .secretlog</code>",
    "tools": "<b>TOOLS</b>\n<code>.calc .time .weather .tr .remind</code>",
    "anims": "<b>ANIMS</b>\n<code>.hack .hacker .heart</code>",
    "flowers": "<b>FLOWERS</b>\n<code>.rose .cat .heart</code>",
    "spy": "<b>SPY</b>\n<code>.uinfo .scan .whois</code>",
    "system": "<b>SYSTEM</b>\n<code>.ping .alive .id .help .uptime .restart</code>",
    "fun": "<b>FUN</b>\n<code>.rose .cat .heart .hack .bal .daily</code>",
    "ai": "<b>AI</b>\nOptional / disabled.",
}
HELP_PAGES["antilink"] = HELP_PAGES["anti"]
HELP_PAGES["broadcast"] = HELP_PAGES["cast"]
HELP_PAGES["sha"] = HELP_PAGES["bro"]
HELP_PAGES["eco"] = HELP_PAGES["fun"]


def _allowed(message: Message) -> bool:
    if getattr(message, "outgoing", False):
        return True
    uid = message.from_user.id if message.from_user else None
    if uid is None:
        return False
    if ME_ID and uid == ME_ID:
        return True
    if OWNER_ID and uid == OWNER_ID:
        return True
    if uid in SUDO_USERS:
        return True
    return False


async def _do_help(message: Message):
    parts = (message.text or "").split()
    if len(parts) > 1:
        key = parts[1].lower()
        page = HELP_PAGES.get(key)
        if not page:
            await _safe_send(message, f"No page: <code>{key}</code>\n<code>.help</code>")
            return
        await _safe_send(message, page)
        print(f"[help] page={key}")
        return
    await _safe_send(message, HELP_INDEX)
    print("[help] index OK")


@app.on_message(ub_cmd("help", "menu", "cmds", "commands"), group=-5)
async def help_cmd(client, message: Message):
    if not _allowed(message):
        try:
            me = await client.get_me()
            if not (message.from_user and message.from_user.id == me.id):
                return
        except Exception:
            return
    await _do_help(message)


@app.on_message(ub_cmd("helpanim"), group=-5)
async def helpanim_cmd(client, message: Message):
    if not _allowed(message):
        return
    frames = ["✨", "✨👑", "👑 <b>YASHIKA</b>", "👑 <b>YASHIKA</b>\nLoading..."]
    try:
        msg = await message.reply_text(frames[0])
        for f in frames[1:]:
            await asyncio.sleep(0.35)
            try:
                await msg.edit_text(f)
            except Exception:
                break
        await asyncio.sleep(0.25)
        try:
            await msg.edit_text(HELP_INDEX)
        except Exception:
            await _safe_send(message, HELP_INDEX)
    except Exception as e:
        print(f"[helpanim] {e}")
        await _safe_send(message, HELP_INDEX)
