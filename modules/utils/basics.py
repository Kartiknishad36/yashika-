"""
basics — ping / alive / id / premium .help / .helpanim
"""
import asyncio
import time

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME
from modules.owner.sudoers import ub_cmd, sudo_only

NAME = BOT_NAME or "Yashika"


@app.on_message(ub_cmd("ping"))
@sudo_only
async def ping_cmd(client, message: Message):
    start = time.time()
    try:
        msg = await message.reply_text("🏓 Pinging…")
        ms = (time.time() - start) * 1000
        await msg.edit_text(f"🏓 <b>Pong!</b> <code>{ms:.2f}ms</code>")
        print("[ping] OK")
    except Exception as e:
        print(f"[ping] {e}")


@app.on_message(ub_cmd("alive"))
@sudo_only
async def alive_cmd(client, message: Message):
    try:
        await message.reply_text(
            f"✨ <b>{NAME}</b> is <b>ALIVE</b> 🔥\n"
            f"📖 <code>.help</code> — command center\n"
            f"⚡ <code>.ping</code> — speed"
        )
    except Exception as e:
        print(f"[alive] {e}")


@app.on_message(ub_cmd("id"))
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
            f"🆔 <b>IDs</b>\n"
            f"Chat: <code>{chat_id}</code>\n"
            f"User: <code>{user_id}</code>"
        )
    except Exception as e:
        print(f"[id] {e}")


HELP_INDEX = (
    "╔══════════════════════╗\n"
    "║ 👑 <b>YASHIKA COMMAND CENTER</b> ║\n"
    "╚══════════════════════╝\n"
    f"✨ <i>Premium Hybrid Userbot</i>\n"
    f"🏷 <b>{NAME}</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "🎵 <b>01 MUSIC/VC</b> — <code>.help vc</code>\n"
    "👑 <b>02 OWNER</b> — <code>.help owner</code>\n"
    "🔑 <b>03 LOGIN</b> — <code>.help login</code>\n"
    "🛡 <b>04 PM SEC</b> — <code>.help pmsec</code>\n"
    "🌐 <b>05 GLOBAL</b> — <code>.help global</code>\n"
    "👮 <b>06 MOD</b> — <code>.help mod</code>\n"
    "🔗 <b>07 ANTI</b> — <code>.help anti</code>\n"
    "⚠️ <b>08 WARN</b> — <code>.help warn</code>\n"
    "📢 <b>09 CAST</b> — <code>.help cast</code>\n"
    "🔥 <b>10 RAID</b> — <code>.help raid</code>\n"
    "💕 <b>11 BRO/SHA</b> — <code>.help bro</code>\n"
    "👋 <b>12 WELCOME</b> — <code>.help welcome</code>\n"
    "💤 <b>13 AFK</b> — <code>.help afk</code>\n"
    "🔒 <b>14 PROTECT</b> — <code>.help protect</code>\n"
    "📌 <b>15 NOTES</b> — <code>.help notes</code>\n"
    "📥 <b>16 DL</b> — <code>.help dl</code>\n"
    "🎨 <b>17 MEDIA</b> — <code>.help media</code>\n"
    "👁 <b>18 GHOST/TRACK</b> — <code>.help ghost</code>\n"
    "🧹 <b>19 TOOLS</b> — <code>.help tools</code>\n"
    "🎬 <b>20 ANIMS</b> — <code>.help anims</code>\n"
    "🌸 <b>21 FLOWERS</b> — <code>.help flowers</code>\n"
    "💑 <b>22 GF-BF</b> — <code>.help gbf</code>\n"
    "🕵️ <b>23 SPY</b> — <code>.help spy</code>\n"
    "⚙️ <b>24 SYSTEM</b> — <code>.help system</code>\n"
    "🎮 <b>25 GAMES/ECO</b> — <code>.help fun</code>\n"
    "🤖 <b>26 AI</b> — <code>.help ai</code>\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📌 <code>.help page</code> · <code>.helpanim</code>\n"
    "👑 YASHIKA — Your Rules"
)

HELP_PAGES = {
    "vc": (
        "🎵 <b>MUSIC / VC</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.play .vply .vplay .cplay .cvply</code>\n"
        "<code>.pause .resume .skip .stop .queue</code>\n"
        "<code>.vmute .vunmute .vcinfo on/off</code>\n"
        "<code>.vcwelcome on/off/test</code>"
    ),
    "owner": (
        "👑 <b>OWNER / SUDO</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.addsudo .delsudo .sudolist</code>\n"
        "<code>.approve .unapprove .approved</code>\n"
        "<code>.clone .back .clonemode</code>\n"
        "<code>.setname .setbio .setpfp .delpfp</code>"
    ),
    "login": (
        "🔑 <b>LOGIN</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.login .cancellogin .addsession .mylogin</code>\n"
        "Phone → OTP → 2FA · Session → Saved Messages only"
    ),
    "pmsec": (
        "🛡 <b>PM SECURITY</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.antispam on/off .pmlog on/off</code>\n"
        "<code>.secretlog on/off .verify</code>"
    ),
    "global": (
        "🌐 <b>GLOBAL MOD</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.gban .ungban .gbanlist</code>\n"
        "<code>.gmute .gunmute</code>"
    ),
    "mod": (
        "👮 <b>CHAT MOD</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ban .unban .kick .mute .unmute</code>\n"
        "<code>.promote .demote .pin .unpin</code>\n"
        "<code>.tagall .tagallstop .zombies</code>\n"
        "<code>.lock .unlock .nightmode .slowmode</code>"
    ),
    "anti": (
        "🔗 <b>ANTI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.antilink on/off .antidelete on/off</code>\n"
        "<code>.antiflood on 5 60</code>"
    ),
    "warn": (
        "⚠️ <b>WARN</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.warn .unwarn .warns .resetwarns</code>"
    ),
    "cast": (
        "📢 <b>BROADCAST</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.broadcast</code> — all\n"
        "<code>.gcast</code> — groups\n"
        "<code>.dmcast</code> — DMs"
    ),
    "raid": (
        "🔥 <b>RAID / SPAM</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.raid 10 text</code> · <code>.raid off</code>\n"
        "<code>.spam 10 text</code> · <code>.spam off</code>"
    ),
    "bro": (
        "💕 <b>BRO / SHAYARI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.bro .brodm .brogroup .unbro .brolist</code>\n"
        "<code>.sha .love .sad .attitude</code>"
    ),
    "welcome": (
        "👋 <b>WELCOME</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.welcome on/off .setwelcome</code>\n"
        "<code>.vcwelcome on/off/test</code>"
    ),
    "afk": (
        "💤 <b>AFK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.afk [reason] .unafk .back</code>"
    ),
    "protect": (
        "🔒 <b>PROTECT</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.protect on/off</code>"
    ),
    "notes": (
        "📌 <b>NOTES</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.save .get .notes .clearnote</code>"
    ),
    "dl": (
        "📥 <b>DOWNLOAD</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ytmp3 .ytmp4 .song .video .dl</code>\n"
        "<code>.insta .tiktok .fb .social</code>"
    ),
    "media": (
        "🎨 <b>MEDIA</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.kang .tts .tg .qr .paste</code>\n"
        "<code>.dp .dpsave .dplog .dpclear</code>"
    ),
    "ghost": (
        "👁 <b>GHOST / TRACK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ghostmod .vanish .track .tracklist</code>\n"
        "<code>.secretlog</code>"
    ),
    "tools": (
        "🛠 <b>TOOLS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.calc .time .weather .tr .short</code>\n"
        "<code>.remind .autoreply .autojoin</code>\n"
        "<code>.del .purge</code>"
    ),
    "anims": (
        "🎬 <b>ANIMATIONS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.hack .moon .loveanim .type .loading</code>\n"
        "<code>.boom .heartbeat .party</code>"
    ),
    "flowers": (
        "🌸 <b>FLOWERS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.rose .cat .heart .hacker</code>"
    ),
    "gbf": (
        "💑 <b>GF-BF</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.propose .iloveu .sorry .missu</code>"
    ),
    "spy": (
        "🕵️ <b>SPY</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.whois .spy .uinfo .scan</code>"
    ),
    "system": (
        "⚙️ <b>SYSTEM</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ping .alive .id .help .helpanim</code>\n"
        "<code>.uptime .about .restart .logs</code>"
    ),
    "fun": (
        "🎮 <b>FUN / ECO</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.joke .quote .roast .bal .daily</code>"
    ),
    "ai": (
        "🤖 <b>AI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "Optional / disabled for speed."
    ),
}

HELP_PAGES["antilink"] = HELP_PAGES["anti"]
HELP_PAGES["broadcast"] = HELP_PAGES["cast"]
HELP_PAGES["utility"] = HELP_PAGES["system"]
HELP_PAGES["sha"] = HELP_PAGES["bro"]
HELP_PAGES["track"] = HELP_PAGES["ghost"]
HELP_PAGES["eco"] = HELP_PAGES["fun"]


@app.on_message(ub_cmd("help", "menu", "cmds", "commands"))
@sudo_only
async def help_cmd(client, message: Message):
    parts = (message.text or "").split()
    try:
        if len(parts) > 1:
            key = parts[1].lower()
            page = HELP_PAGES.get(key)
            if not page:
                await message.reply_text(
                    f"❌ No page: <code>{key}</code>\n<code>.help</code> for menu."
                )
                return
            await message.reply_text(page)
            return
        await message.reply_text(HELP_INDEX)
        print("[help] OK")
    except Exception as e:
        print(f"[help] {e}")
        try:
            await client.send_message(message.chat.id, HELP_INDEX)
        except Exception as e2:
            print(f"[help2] {e2}")


@app.on_message(ub_cmd("helpanim"))
@sudo_only
async def helpanim_cmd(client, message: Message):
    frames = [
        "✨",
        "✨👑",
        "👑 <b>YASHIKA</b>",
        "👑 <b>YASHIKA</b>\n💎 Premium",
        "👑 <b>YASHIKA</b>\n💎 Premium\n📜 Loading…",
    ]
    try:
        msg = await message.reply_text(frames[0])
        for f in frames[1:]:
            await asyncio.sleep(0.4)
            try:
                await msg.edit_text(f)
            except Exception:
                break
        await asyncio.sleep(0.3)
        try:
            await msg.edit_text(HELP_INDEX)
        except Exception:
            await message.reply_text(HELP_INDEX)
    except Exception as e:
        print(f"[helpanim] {e}")
