"""
basics — ping / alive / id / premium .help
"""
import asyncio
import time

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def cmd(name):
    return filters.command(name, prefixes=PREFIXES)


@app.on_message(cmd("ping"))
@sudo_only
async def ping_cmd(client, message: Message):
    start = time.time()
    msg = await message.reply_text("🏓 Pinging…")
    ms = (time.time() - start) * 1000
    await msg.edit_text(f"🏓 <b>Pong!</b> <code>{ms:.2f}ms</code>")


@app.on_message(cmd("alive"))
@sudo_only
async def alive_cmd(client, message: Message):
    await message.reply_text(
        f"✨ <b>{BOT_NAME}</b> is <b>ALIVE</b> 🔥\n"
        f"📖 <code>.help</code> — command center\n"
        f"⚡ <code>.ping</code> — speed"
    )


@app.on_message(cmd("id"))
@sudo_only
async def id_cmd(client, message: Message):
    chat_id = message.chat.id
    user_id = (
        message.reply_to_message.from_user.id
        if message.reply_to_message and message.reply_to_message.from_user
        else (message.from_user.id if message.from_user else "N/A")
    )
    await message.reply_text(
        f"🆔 <b>IDs</b>\nChat: <code>{chat_id}</code>\nUser: <code>{user_id}</code>"
    )


# ===================== PREMIUM HELP =====================

HELP_INDEX = f"""
╔══════════════════════╗
║ 👑 <b>YASHIKA COMMAND CENTER</b> ║
╚══════════════════════╝
✨ <i>Premium Hybrid Userbot</i>
🏷 <b>{BOT_NAME}</b>
━━━━━━━━━━━━━━━━━━━━

🎵 <b>01 MUSIC/VC</b> — <code>.help vc</code>
👑 <b>02 OWNER</b> — <code>.help owner</code>
🔑 <b>03 LOGIN</b> — <code>.help login</code>
🛡 <b>04 PM SEC</b> — <code>.help pmsec</code>
🌐 <b>05 GLOBAL</b> — <code>.help global</code>
👮 <b>06 MOD</b> — <code>.help mod</code>
🔗 <b>07 ANTI</b> — <code>.help anti</code>
⚠️ <b>08 WARN</b> — <code>.help warn</code>
📢 <b>09 CAST</b> — <code>.help cast</code>
🔥 <b>10 RAID</b> — <code>.help raid</code>
💕 <b>11 BRO/SHA</b> — <code>.help bro</code>
👋 <b>12 WELCOME</b> — <code>.help welcome</code>
💤 <b>13 AFK</b> — <code>.help afk</code>
🔒 <b>14 PROTECT</b> — <code>.help protect</code>
📌 <b>15 NOTES</b> — <code>.help notes</code>
📥 <b>16 DL</b> — <code>.help dl</code>
🎨 <b>17 MEDIA</b> — <code>.help media</code>
👁 <b>18 GHOST/TRACK</b> — <code>.help ghost</code>
🧹 <b>19 TOOLS</b> — <code>.help tools</code>
🎬 <b>20 ANIMS</b> — <code>.help anims</code>
🌸 <b>21 FLOWERS</b> — <code>.help flowers</code>
💑 <b>22 GF-BF</b> — <code>.help gbf</code>
🕵️ <b>23 SPY</b> — <code>.help spy</code>
⚙️ <b>24 SYSTEM</b> — <code>.help system</code>
🎮 <b>25 GAMES/ECO</b> — <code>.help fun</code>
🤖 <b>26 AI</b> — <code>.help ai</code>

━━━━━━━━━━━━━━━━━━━━
📌 <code>.help &lt;name&gt;</code> · <code>.helpanim</code>
👑 YASHIKA — Your Rules
"""

HELP_PAGES = {
    "vc": (
        "🎵 <b>MUSIC / VC</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.play .vply .vplay .cplay .cvply</code>\n"
        "<code>.pause .resume .skip .stop .queue</code>\n"
        "<code>.vmute .vunmute .vcinfo on/off</code>"
    ),
    "owner": (
        "👑 <b>OWNER / SUDO</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.addsudo .delsudo .sudolist</code>\n"
        "<code>.approve .unapprove .approved</code>\n"
        "<code>.clone .back .clonemode</code>\n"
        "<code>.setname .setbio .setpfp .delpfp</code>\n"
        "<code>.block .unblock</code>"
    ),
    "login": (
        "🔑 <b>LOGIN</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.login .cancellogin .logout .mylogin</code>"
    ),
    "pmsec": (
        "🛡 <b>PM SECURITY</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.antispam on/off .pmlog on/off</code>\n"
        "<code>.secretlog on/off .verify</code>\n"
        "Auto warn → block (3x) + group verify"
    ),
    "global": (
        "🌐 <b>GLOBAL MOD</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.gban .ungban .gbanlist</code>\n"
        "<code>.gmute .gunmute</code>"
    ),
    "mod": (
        "👮 <b>CHAT MOD</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ban .unban .kick .mute .unmute</code>\n"
        "<code>.banall .kickall .muteall .unmuteall</code>\n"
        "<code>.promote .demote .pin .unpin</code>\n"
        "<code>.tagall .tagallstop .tagme .tagadmins</code>\n"
        "<code>.invitelink .zombies clean .autokick</code>\n"
        "<code>.lock .unlock .nightmode .slowmode</code>\n"
        "<code>.setrules .rules .clearrules</code>\n"
        "<code>.setgrouppic .setgrouptitle .setgroupdesc</code>"
    ),
    "anti": (
        "🔗 <b>ANTI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.antilink on/off .antibot on/off</code>\n"
        "<code>.antidelete on/off .antilinkstatus</code>\n"
        "<code>.antiflood on 5 60</code>"
    ),
    "warn": (
        "⚠️ <b>WARN</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.warn .unwarn .warns .resetwarns</code>"
    ),
    "cast": (
        "📢 <b>BROADCAST</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.broadcast</code> — all tracked\n"
        "<code>.gcast</code> — groups only\n"
        "<code>.dmcast</code> — DMs only\n"
        "Bot: <code>/broadcast /gcast /dmcast</code>"
    ),
    "raid": (
        "🔥 <b>RAID / SPAM</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.raid 10 text</code> · <code>.raid off</code>\n"
        "<code>.spam 10 text</code> · <code>.spam off</code>"
    ),
    "bro": (
        "💕 <b>BRO / SHAYARI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.bro .brodm .brogroup .broall .unbro .brolist</code>\n"
        "<code>.sha .love .sad .attitude .dard</code>\n"
        "<code>.friendship .motivational</code>\n"
        "<code>.goodmorning .goodnight</code>"
    ),
    "welcome": (
        "👋 <b>WELCOME</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.welcome on/off .setwelcome</code>"
    ),
    "afk": (
        "💤 <b>AFK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.afk [reason] .unafk .back .afkstatus</code>"
    ),
    "protect": (
        "🔒 <b>PROTECT</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.protect on/off</code> · reply+protect\n"
        "<code>.psend .pfile</code>"
    ),
    "notes": (
        "📌 <b>NOTES</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.save .get .notes .clearnote .clearallnotes</code>\n"
        "<code>#name</code>"
    ),
    "dl": (
        "📥 <b>DOWNLOAD</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ytmp3 .ytmp4 .song .video .dl</code>\n"
        "<code>.insta .tiktok .fb .social</code>"
    ),
    "media": (
        "🎨 <b>MEDIA</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.kang .steal .tts .stt .tg .tgmode</code>\n"
        "<code>.nuinfo .qr .paste .captiongen .secretlink</code>"
    ),
    "ghost": (
        "👁 <b>GHOST / TRACK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ghostmod .ghost .ghostview .vanish</code>\n"
        "<code>.track .trackadd .trackdel .tracklist</code>\n"
        "<code>.profiletrack on/off/list</code>\n"
        "<code>.secretlog .pmlog</code>"
    ),
    "tools": (
        "🛠 <b>TOOLS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.calc .time .weather .translate .tr .short</code>\n"
        "<code>.remind 10m text .filter add x | y</code>\n"
        "<code>.autobio .autojoin .join .leave</code>\n"
        "<code>.autoreply .gclone .idbackup</code>\n"
        "<code>.leadsaver .leads .followup</code>\n"
        "<code>.copycap .hashtaggen .fakelocation</code>\n"
        "<code>.del .purge .msginfo .idtouser .usertoid</code>"
    ),
    "anims": (
        "🎬 <b>ANIMATIONS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.hack .moon .loveanim .type .loading</code>\n"
        "<code>.boom .heartbeat .party .congo .birthday</code>\n"
        "<code>.animlist</code> — full list\n"
        "<i>+ bomb heart fire king queen …</i>"
    ),
    "flowers": (
        "🌸 <b>FLOWERS 50+</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.rose .lotus .gulab .sunflower .propose</code>\n"
        "<code>.bouquet .flowerrain .rosefall</code>\n"
        "<code>.flowerlist</code>"
    ),
    "gbf": (
        "💑 <b>GF-BF</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.propose .iloveu .rainbow .lovecalc</code>\n"
        "<code>.sorry .manau .missu .ring .heartlock</code>"
    ),
    "spy": (
        "🕵️ <b>SPY PACK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.whois .spy .profile .picspy .flagspy</code>\n"
        "<code>.mutual .msgspy .chattrace</code>\n"
        "<code>.spylist .darklist</code>\n"
        "<i>Limit cards: .iptrace .lastseen (honest)</i>"
    ),
    "system": (
        "⚙️ <b>SYSTEM</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>.ping .alive .id .info .help .helpanim</code>\n"
        "<code>.uptime .about .version .stats</code>\n"
        "<code>.restart .shutdown .logs</code>"
    ),
    "fun": (
        "🎮 <b>GAMES / ECO / FUN</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>/dice /dart /basket /couple /td /bomb /ludo</code>\n"
        "<code>/bal /daily /rob /kill /protect</code>\n"
        "<code>/kiss /hug /slap</code>\n"
        "<code>.joke .quote .roast .fact .pickup</code>"
    ),
    "ai": (
        "🤖 <b>AI</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        "<code>/chatbot on/off</code>\n"
        "<code>/ai /ask /learn /aiclear</code>\n"
        "DM = auto chatbot"
    ),
    # aliases
    "antilink": None,  # filled below
    "broadcast": None,
    "utility": None,
    "sha": None,
    "raid": None,
}

# aliases
HELP_PAGES["antilink"] = HELP_PAGES["anti"]
HELP_PAGES["broadcast"] = HELP_PAGES["cast"]
HELP_PAGES["utility"] = HELP_PAGES["system"]
HELP_PAGES["sha"] = HELP_PAGES["bro"]
HELP_PAGES["track"] = HELP_PAGES["ghost"]
HELP_PAGES["login"] = HELP_PAGES["login"]
HELP_PAGES["nuinfo"] = HELP_PAGES["media"]
HELP_PAGES["chat"] = HELP_PAGES["tools"]
HELP_PAGES["eco"] = HELP_PAGES["fun"]
HELP_PAGES["dl"] = HELP_PAGES["dl"]


@app.on_message(cmd("help"))
@sudo_only
async def help_cmd(client, message: Message):
    if len(message.command) > 1:
        key = message.command[1].lower()
        page = HELP_PAGES.get(key)
        if not page:
            await message.reply_text(
                f"❌ No page: <code>{key}</code>\n"
                f"<code>.help</code> for menu."
            )
            return
        await message.reply_text(page)
        return
    await message.reply_text(HELP_INDEX)


@app.on_message(cmd("helpanim"))
@sudo_only
async def helpanim_cmd(client, message: Message):
    """Short premium color-frame intro then full index."""
    frames = [
        "✨",
        "✨👑",
        "👑 <b>YASHIKA</b>",
        "👑 <b>YASHIKA</b>\n💎 Premium",
        "👑 <b>YASHIKA</b>\n💎 Premium\n📜 Loading commands…",
    ]
    msg = await message.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(0.45)
        try:
            await msg.edit_text(f)
        except Exception:
            break
    await asyncio.sleep(0.4)
    try:
        await msg.edit_text(HELP_INDEX)
    except Exception:
        await message.reply_text(HELP_INDEX)
