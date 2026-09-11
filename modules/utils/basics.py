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
    msg = await message.reply_text("🏓 Pinging...")
    ms = (time.time() - start) * 1000
    await msg.edit_text(f"🏓 <b>Pong!</b> <code>{ms:.2f}ms</code>")


@app.on_message(cmd(["alive"]))
@sudo_only
async def alive_cmd(client, message: Message):
    await message.reply_text(
        f"✨ <b>{BOT_NAME}</b> is <b>ALIVE</b> 🔥\n"
        f"📖 <code>.help</code> — full command list\n"
        f"⚡ <code>.ping</code> — speed check"
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
        f"🆔 <b>IDs</b>\n"
        f"Chat: <code>{chat_id}</code>\n"
        f"User: <code>{user_id}</code>"
    )


# ===================== HELP =====================

HELP_INDEX = f"""
╔══════════════════════════╗
║  ⚡ <b>{BOT_NAME.upper()}</b> COMMAND CENTER ⚡
╚══════════════════════════╝

╭─ 🎵 <b>MUSIC / VC</b>
│ ▶️ .play .vply .cplay .cvply
│ ⏸️ .pause ▶️ .resume ⏭️ .skip ⏹️ .stop
│ 🔇 .vmute 🔊 .vunmute
╰──────────────

╭─ 👑 <b>OWNER / SUDO</b>
│ 🌟 .addsudo 🗑️ .delsudo 📜 .sudolist
│ ✅ .approve ❌ .unapprove 📋 .approved
│ 👥 .clone 🚫 .unclone 📚 .clonelist
╰──────────────

╭─ 🔑 <b>LOGIN</b>
│ 📱 .login  🚫 .cancellogin
│ 👋 .logout  ℹ️ .mylogin
╰──────────────

╭─ 🛡 <b>PM SECURITY</b>
│ 🚨 Auto warn + block (3x)
│ ✅ .verify  (group join ke baad)
│ 🛡 .antispam on/off
│ 🗑 .pmlog on/off
╰──────────────

╭─ 🌐 <b>GLOBAL MOD</b>
│ 🔨 .gban 🕊️ .ungban 📜 .gbanlist
│ 🔇 .gmute 🔊 .gunmute
╰──────────────

╭─ 👮 <b>CHAT MOD</b>
│ 🔨 .ban 🕊️ .unban 👢 .kick
│ 🔇 .mute 🔊 .unmute
│ 💥 .banall .kickall .muteall .unmuteall
│ 📢 .tagall 🛑 .tagallstop 🙋 .tagme
╰──────────────

╭─ 🔗 <b>ANTI-LINK / BOT / DELETE</b>
│ 🔗 .antilink on/off
│ 🤖 .antibot on/off
│ 👻 .antidelete on/off
│ 📊 .antilinkstatus
╰──────────────

╭─ ⚠️ <b>WARN</b>
│ ⚠️ .warn ✅ .unwarn 📊 .warns 🔄 .resetwarns
╰──────────────

╭─ 📢 <b>BROADCAST</b>
│ 📣 .broadcast  |  /broadcast (bot)
╰──────────────

╭─ 📜 <b>SHAYARI / LOVE / BRO</b>
│ 🌹 .sha  ❤️ .love  😎 .bro
╰──────────────

╭─ 👋 <b>WELCOME</b>
│ 🔛 .welcome on/off
│ ✍️ .setwelcome
╰──────────────

╭─ 💤 <b>AFK</b>
│ 💤 .afk [reason]  ✅ .unafk / .back
│ 📊 .afkstatus
╰──────────────

╭─ 🔒 <b>PROTECT</b>
│ 🔒 .protect on/off | reply+.protect
│ 📝 .psend text  📎 .pfile
╰──────────────

╭─ 📌 <b>NOTES</b>
│ 💾 .save  📖 .get  📋 .notes
│ 🗑 .clearnote  🧹 .clearallnotes
│ ＃ #name shortcut
╰──────────────

╭─ 📥 <b>DOWNLOAD</b>
│ 🎵 .ytmp3  🎬 .ytmp4  📥 .dl
│ 📷 .insta  🎵 .tiktok  📘 .fb
│ 🌐 .social
╰──────────────

╭─ 🎨 <b>STICKER / VOICE</b>
│ 🔪 .kang / .steal
│ 🗣 .tts  🎧 .stt
╰──────────────

╭─ 👁 <b>TRACKER</b>
│ 👁 .track on/off
│ ➕ .trackadd  ➖ .trackdel  📋 .tracklist
╰──────────────

╭─ 🧹 <b>CHAT TOOLS</b>
│ 🗑 .del  🧹 .purge
╰──────────────

╭─ 🎮 <b>GAMES / FUN / ECO</b>
│ 🎲 /dice /dart /basket
│ 💑 /couple  🎭 /td  💣 /bomb
│ 💰 /bal /daily /rob /kill /protect
│ 💋 /kiss /hug /slap …
│ 🐱 .cat 🌹 .rose 💖 .heart …
╰──────────────

╭─ 🤖 <b>AI CHATBOT</b>
│ 🔛 /chatbot on/off (group)
│ 💬 /ai /ask  🧠 /learn  🧹 /aiclear
│ DM = auto ON
╰──────────────

╭─ ⚙️ <b>UTILITY</b>
│ ⚡ .ping  ✅ .alive  🆔 .id
│ ℹ️ .info  📖 .help
╰──────────────

📌 Detail: <code>.help &lt;category&gt;</code>
Categories:
<code>vc owner login pmsec global mod antilink warn broadcast sha bro welcome afk protect notes dl media track chat fun eco ai utility</code>
"""

HELP_PAGES = {
    "vc": """
🎵 <b>MUSIC / VC</b>
━━━━━━━━━━━━━━━━━━
<code>.play</code> <code>.vply</code> <code>.cplay</code> <code>.cvply</code>
<code>.pause</code> <code>.resume</code> <code>.skip</code> <code>.stop</code>
<code>.vmute</code> <code>.vunmute</code>

Queue support • cookies / yt-dlp stream
""",
    "owner": """
👑 <b>OWNER</b>
━━━━━━━━━━━━━━━━━━
<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>
<code>.approve</code> <code>.unapprove</code> <code>.approved</code>
<code>.clone</code> <code>.unclone</code> <code>.clonelist</code>
""",
    "login": """
🔑 <b>LOGIN</b>
━━━━━━━━━━━━━━━━━━
<code>.login</code> — guided phone/OTP
<code>.login &lt;session&gt;</code>
<code>.cancellogin</code> <code>.logout</code> <code>.mylogin</code>
""",
    "pmsec": """
🛡 <b>PM SECURITY</b>
━━━━━━━━━━━━━━━━━━
Anjaan DM → warn (1/3…3/3) → block
Group join + <code>.verify</code> → approve

<code>.antispam on/off</code> — 5 msg / 10s → block
<code>.pmlog on/off</code> — deleted DM → Saved/LOG
""",
    "global": """
🌐 <b>GLOBAL MOD</b>
━━━━━━━━━━━━━━━━━━
<code>.gban</code> <code>.ungban</code> <code>.gbanlist</code>
<code>.gmute</code> <code>.gunmute</code>
""",
    "mod": """
👮 <b>CHAT MOD</b>
━━━━━━━━━━━━━━━━━━
<code>.ban</code> <code>.unban</code> <code>.kick</code>
<code>.mute</code> <code>.unmute</code>
<code>.banall</code> <code>.kickall</code> <code>.muteall</code> <code>.unmuteall</code>
<code>.tagall</code> <code>.tagallstop</code> <code>.tagme</code>
""",
    "antilink": """
🔗 <b>ANTI-LINK / BOT / DELETE</b>
━━━━━━━━━━━━━━━━━━
<code>.antilink on/off</code> — links delete
<code>.antibot on/off</code> — bots kick
<code>.antidelete on/off</code> — delete alerts
<code>.antilinkstatus</code>
Per-group • default OFF
""",
    "warn": """
⚠️ <b>WARN</b>
━━━━━━━━━━━━━━━━━━
<code>.warn</code> <code>.unwarn</code> <code>.warns</code> <code>.resetwarns</code>
3 warns → auto ban
""",
    "broadcast": """
📢 <b>BROADCAST</b>
━━━━━━━━━━━━━━━━━━
<code>.broadcast</code> — userbot
<code>/broadcast</code> — bot client (owner/sudo)
""",
    "sha": """
📜 <b>SHAYARI / LOVE</b>
━━━━━━━━━━━━━━━━━━
<code>.sha</code> <code>.love</code>
reply / group / timed / stop
""",
    "bro": """
😎 <b>BRO</b>
━━━━━━━━━━━━━━━━━━
<code>.bro</code> — auto-reply target system
<code>.unbro</code> <code>.brolist</code>
""",
    "welcome": """
👋 <b>WELCOME</b>
━━━━━━━━━━━━━━━━━━
<code>.welcome on/off</code>
<code>.setwelcome</code> — {mention} {chat} {name} {id}
""",
    "afk": """
💤 <b>AFK</b>
━━━━━━━━━━━━━━━━━━
<code>.afk [reason]</code>
<code>.unafk</code> / <code>.back</code>
<code>.afkstatus</code>
Auto-reply: DM / reply / @mention
""",
    "protect": """
🔒 <b>PROTECT CONTENT</b>
━━━━━━━━━━━━━━━━━━
<code>.protect on/off</code>
Reply + <code>.protect</code> — protected copy
<code>.psend text</code> <code>.pfile</code>
""",
    "notes": """
📌 <b>NOTES</b>
━━━━━━━━━━━━━━━━━━
<code>.save name text</code>
<code>.get name</code> · <code>#name</code>
<code>.notes</code>
<code>.clearnote</code> <code>.clearallnotes</code>
""",
    "dl": """
📥 <b>DOWNLOAD</b>
━━━━━━━━━━━━━━━━━━
<code>.ytmp3</code> <code>.ytmp4</code> <code>.dl</code>
<code>.insta</code> <code>.tiktok</code> <code>.fb</code> <code>.social</code>
cookies.txt recommended
""",
    "media": """
🎨 <b>STICKER / VOICE</b>
━━━━━━━━━━━━━━━━━━
<code>.kang</code> / <code>.steal</code> [emoji]
<code>.tts text</code>
Reply voice + <code>.stt</code>
""",
    "track": """
👁 <b>ONLINE TRACKER</b>
━━━━━━━━━━━━━━━━━━
<code>.track on/off</code>
<code>.trackadd</code> <code>.trackdel</code> <code>.tracklist</code>
Alerts → Saved + LOG
""",
    "chat": """
🧹 <b>CHAT TOOLS</b>
━━━━━━━━━━━━━━━━━━
<code>.del</code> — reply delete
<code>.purge</code> — range delete
""",
    "fun": """
🎉 <b>FUN / GAMES</b>
━━━━━━━━━━━━━━━━━━
<code>.cat</code> <code>.rose</code> <code>.heart</code> <code>.hacker</code> …
<code>/dice</code> <code>/couple</code> <code>/td</code> <code>/bomb</code>
<code>/kiss</code> <code>/hug</code> <code>/slap</code>
""",
    "eco": """
💰 <b>ECONOMY</b>
━━━━━━━━━━━━━━━━━━
<code>/bal</code> <code>/daily</code>
<code>/rob</code> <code>/kill</code> <code>/protect</code>
""",
    "ai": """
🤖 <b>AI CHATBOT</b>
━━━━━━━━━━━━━━━━━━
<code>/chatbot on/off</code> — groups
<code>/ai</code> <code>/ask</code> <code>/learn</code> <code>/aiclear</code>
DM auto-on • tag/reply/plain in group
""",
    "utility": """
⚙️ <b>UTILITY</b>
━━━━━━━━━━━━━━━━━━
<code>.ping</code> <code>.alive</code> <code>.id</code>
<code>.info</code> <code>.help</code> <code>.help ai</code>
""",
}


@app.on_message(cmd("help"))
@sudo_only
async def help_cmd(client, message: Message):
    if len(message.command) > 1:
        key = message.command[1].lower()
        page = HELP_PAGES.get(key)
        if not page:
            await message.reply_text(
                f"❌ No page for <code>{key}</code>\n"
                f"Send <code>.help</code> for index."
            )
            return
        await message.reply_text(page)
        return
    await message.reply_text(HELP_INDEX)
