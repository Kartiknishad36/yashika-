"""
basics — ping / alive / id / premium .help / .helpanim
"""
import asyncio
import time

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME
from modules.owner.sudoers import ub_cmd, sudo_only, ME_ID, OWNER_ID, SUDO_USERS

NAME = BOT_NAME or "Yashika"


async def _safe_send(message: Message, text: str):
    """Reply; fallback send_message if reply fails."""
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
            # last try: strip HTML
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
@sudo_only
async def ping_cmd(client, message: Message):
    start = time.time()
    try:
        msg = await message.reply_text("Pinging...")
        ms = (time.time() - start) * 1000
        await msg.edit_text(f"<b>Pong!</b> <code>{ms:.0f}ms</code>")
        print("[ping] OK")
    except Exception as e:
        print(f"[ping] {e}")


@app.on_message(ub_cmd("alive"), group=-5)
@sudo_only
async def alive_cmd(client, message: Message):
    await _safe_send(
        message,
        f"<b>{NAME}</b> is <b>ALIVE</b>\n"
        f"<code>.help</code> — command center\n"
        f"<code>.ping</code> — speed",
    )


@app.on_message(ub_cmd("id"), group=-5)
@sudo_only
async def id_cmd(client, message: Message):
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
    "vc": (
        "<b>MUSIC / VC</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.play .vply .vplay .skip .stop</code>\n"
        "<code>.pause .resume .queue</code>\n"
        "<code>.vmute .vunmute .vcinfo</code>\n"
        "<code>.vcwelcome on/off/test</code>"
    ),
    "owner": (
        "<b>OWNER / SUDO</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.addsudo .delsudo .sudolist</code>\n"
        "<code>.approve .unapprove .verify</code>\n"
        "<code>.clone .setname .setbio .setpfp</code>"
    ),
    "login": (
        "<b>LOGIN</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.login .cancellogin .addsession .mylogin</code>\n"
        "Phone → OTP → 2FA · Saved Messages only"
    ),
    "pmsec": (
        "<b>PM SECURITY</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.secretlog on/off .verify</code>"
    ),
    "global": (
        "<b>GLOBAL</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.gban .ungban .gbanlist</code>\n"
        "<code>.gmute .gunmute</code>"
    ),
    "mod": (
        "<b>CHAT MOD</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ban .unban .kick .mute .unmute</code>\n"
        "<code>.promote .demote .pin .unpin</code>\n"
        "<code>.tagall .tagallstop .tagme .tagadmins</code>\n"
        "<code>.banall .kickall .muteall .unmuteall</code>"
    ),
    "anti": (
        "<b>ANTI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.antilink on/off .antidelete on/off</code>\n"
        "<code>.antiflood on 5 60</code>"
    ),
    "warn": (
        "<b>WARN</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.warn .unwarn .warns .resetwarns</code>"
    ),
    "cast": (
        "<b>BROADCAST</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.broadcast</code> all\n"
        "<code>.gcast</code> groups\n"
        "<code>.dmcast</code> DMs"
    ),
    "raid": (
        "<b>RAID / SPAM</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.raid 10 text</code> · <code>.raid off</code>\n"
        "<code>.spam 10 text</code> · <code>.spam off</code>"
    ),
    "bro": (
        "<b>BRO</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.bro .brodm .brogroup .unbro .brolist</code>"
    ),
    "welcome": (
        "<b>WELCOME</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.welcome on/off .setwelcome</code>\n"
        "<code>.vcwelcome on/off/test</code>"
    ),
    "afk": (
        "<b>AFK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.afk reason .unafk .back .afkstatus</code>"
    ),
    "protect": (
        "<b>PROTECT</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.protect on/off</code>"
    ),
    "notes": (
        "<b>NOTES</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.save .get .notes .clearnote</code>"
    ),
    "dl": (
        "<b>DOWNLOAD</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ytmp3 .ytmp4 .song .video .dl</code>\n"
        "<code>.insta .tiktok .fb .social</code>"
    ),
    "media": (
        "<b>MEDIA</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.kang .tts .tg .qr .paste</code>\n"
        "<code>.dp .dpsave .dplog .dpclear</code>"
    ),
    "ghost": (
        "<b>GHOST / TRACK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ghostmod .vanish .track .tracklist</code>\n"
        "<code>.secretlog</code>"
    ),
    "tools": (
        "<b>TOOLS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.calc .time .weather .tr</code>\n"
        "<code>.remind .autoreply .autojoin</code>"
    ),
    "anims": (
        "<b>ANIMS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.hack .hacker .heart</code>"
    ),
    "flowers": (
        "<b>FLOWERS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.rose .cat .heart .hacker</code>"
    ),
    "spy": (
        "<b>SPY</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.uinfo .scan .whois</code>"
    ),
    "system": (
        "<b>SYSTEM</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ping .alive .id .help .helpanim</code>\n"
        "<code>.uptime .about .restart .logs</code>"
    ),
    "fun": (
        "<b>FUN</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.rose .cat .heart .hack</code>\n"
        "<code>.bal .daily</code>"
    ),
    "ai": (
        "<b>AI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "Optional / disabled for speed."
    ),
}

HELP_PAGES["antilink"] = HELP_PAGES["anti"]
HELP_PAGES["broadcast"] = HELP_PAGES["cast"]
HELP_PAGES["utility"] = HELP_PAGES["system"]
HELP_PAGES["sha"] = HELP_PAGES["bro"]
HELP_PAGES["track"] = HELP_PAGES["ghost"]
HELP_PAGES["eco"] = HELP_PAGES["fun"]
HELP_PAGES["gbf"] = HELP_PAGES["fun"]
HELP_PAGES["pm"] = HELP_PAGES["pmsec"]


def _allowed(message: Message) -> bool:
    if getattr(message, "outgoing", False):
        return True
    uid = message.from_user.id if message.from_user else None
    if uid is None:
        return bool(getattr(message, "outgoing", False))
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
            await _safe_send(
                message,
                f"No page: <code>{key}</code>\n<code>.help</code> for menu.",
            )
            return
        ok = await _safe_send(message, page)
        print(f"[help] page={key} ok={ok}")
        return
    ok = await _safe_send(message, HELP_INDEX)
    print(f"[help] index ok={ok}")


@app.on_message(ub_cmd("help", "menu", "cmds", "commands"), group=-5)
async def help_cmd(client, message: Message):
    if not _allowed(message):
        # still try if from me after start
        try:
            me = await client.get_me()
            if message.from_user and message.from_user.id == me.id:
                pass
            else:
                return
        except Exception:
            return
    await _do_help(message)


# Backup: filters.me regex (agar ub_cmd miss)
@app.on_message(
    filters.me
    & filters.text
    & filters.regex(r"^[.!](help|menu|cmds|commands)(\s|$)"),
    group=-4,
)
async def help_backup(client, message: Message):
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
