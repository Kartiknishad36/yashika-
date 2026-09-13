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


# ===================== ROYAL HELP =====================

HELP_INDEX = f"""
👑 <b>✦ YASHIKA COMMAND CENTER ✦</b>
━━━━━━━━━━━━━━━━━━━━
✨ <i>ONE BOT • ENDLESS POSSIBILITIES</i>
🏷 <b>{BOT_NAME}</b> — Premium Userbot
━━━━━━━━━━━━━━━━━━━━

🎵 <b>1. MUSIC / VC</b>
<code>.play</code> <code>.vply</code> <code>.cplay</code> <code>.cvply</code>
<code>.pause</code> <code>.resume</code> <code>.skip</code> <code>.stop</code>
<code>.vmute</code> <code>.vunmute</code>

👑 <b>2. OWNER / SUDO</b>
<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>
<code>.approve</code> <code>.unapprove</code> <code>.approved</code>
<code>.clone</code> <code>.unclone</code> <code>.clonelist</code>
<code>.clonemode</code> <code>.back</code>

🔑 <b>3. LOGIN</b>
<code>.login</code> <code>.cancellogin</code>
<code>.logout</code> <code>.mylogin</code>

🛡 <b>4. PM SECURITY</b>
<code>.antispam on/off</code> <code>.pmlog on/off</code>
<code>.secretlog on/off</code> <code>.verify</code>
⚠️ Auto warn + block (3x)

🌐 <b>5. GLOBAL MOD</b>
<code>.gban</code> <code>.ungban</code> <code>.gbanlist</code>
<code>.gmute</code> <code>.gunmute</code>

👮 <b>6. CHAT MOD</b>
<code>.ban</code> <code>.unban</code> <code>.kick</code>
<code>.mute</code> <code>.unmute</code>
<code>.banall</code> <code>.kickall</code> <code>.muteall</code> <code>.unmuteall</code>
<code>.tagall</code> <code>.tagallstop</code> <code>.tagme</code>

🔗 <b>7. ANTI-LINK / BOT / DELETE</b>
<code>.antilink on/off</code> <code>.antibot on/off</code>
<code>.antidelete on/off</code> <code>.antilinkstatus</code>

⚠️ <b>8. WARN</b>
<code>.warn</code> <code>.unwarn</code> <code>.warns</code> <code>.resetwarns</code>

📢 <b>9. BROADCAST</b>
<code>.broadcast</code> | <code>/broadcast</code> (bot)

🔥 <b>10. RAID / SPAM</b>
<code>.raid 10 text</code> <code>.raid off</code>
<code>.spam 10 text</code> <code>.spam off</code>

💕 <b>11. SHAYARI / LOVE / BRO</b>
<code>.sha</code> <code>.love</code>
<code>.bro</code> <code>.brodm</code> <code>.brogroup</code>
<code>.unbro</code> <code>.brolist</code>

👋 <b>12. WELCOME</b>
<code>.welcome on/off</code> <code>.setwelcome</code>

💤 <b>13. AFK</b>
<code>.afk [reason]</code> <code>.unafk</code> <code>.back</code>
<code>.afkstatus</code>

🔒 <b>14. PROTECT</b>
<code>.protect on/off</code> | reply+<code>.protect</code>
<code>.psend</code> <code>.pfile</code>

📌 <b>15. NOTES</b>
<code>.save</code> <code>.get</code> <code>.notes</code>
<code>.clearnote</code> <code>.clearallnotes</code> <code>#name</code>

📥 <b>16. DOWNLOAD</b>
<code>.ytmp3</code> <code>.ytmp4</code> <code>.dl</code>
<code>.insta</code> <code>.tiktok</code> <code>.fb</code> <code>.social</code>

🎨 <b>17. STICKER / VOICE / NUMBER</b>
<code>.kang</code> <code>.steal</code> <code>.tts</code> <code>.stt</code>
<code>.nuinfo</code>

👁 <b>18. TRACKER / GHOST</b>
<code>.track on/off</code> <code>.trackadd</code> <code>.trackdel</code> <code>.tracklist</code>
<code>.ghostmod on/off</code>

🧹 <b>19. CHAT TOOLS</b>
<code>.del</code> <code>.purge</code>

🎮 <b>20. GAMES / FUN / ECO</b>
<code>/dice</code> <code>/dart</code> <code>/basket</code> <code>/couple</code> <code>/td</code> <code>/bomb</code>
<code>/bal</code> <code>/daily</code> <code>/rob</code> <code>/kill</code> <code>/protect</code>
<code>/kiss</code> <code>/hug</code> <code>/slap</code>
<code>.cat</code> <code>.rose</code> <code>.heart</code> …

🤖 <b>21. AI CHATBOT</b>
<code>/chatbot on/off</code>
<code>/ai</code> <code>/ask</code> <code>/learn</code> <code>/aiclear</code>
DM = auto ON

⚙️ <b>22. UTILITY</b>
<code>.ping</code> <code>.alive</code> <code>.id</code> <code>.info</code> <code>.help</code>

━━━━━━━━━━━━━━━━━━━━
📌 Detail: <code>.help &lt;category&gt;</code>
<code>vc owner login pmsec raid ghost track global mod antilink warn broadcast bro sha welcome afk protect notes dl media nuinfo chat fun eco ai utility</code>
━━━━━━━━━━━━━━━━━━━━
👑 <b>YASHIKA BOT</b> — Your Commands • Your Rules
"""

HELP_PAGES = {
    "vc": "🎵 <b>MUSIC / VC</b>\n<code>.play .vply .cplay .cvply .pause .resume .skip .stop .vmute .vunmute</code>",
    "owner": "👑 <b>OWNER</b>\n<code>.addsudo .delsudo .sudolist .approve .unapprove .approved .clone .unclone .clonelist .clonemode .back</code>",
    "login": "🔑 <b>LOGIN</b>\n<code>.login .cancellogin .logout .mylogin</code>",
    "pmsec": "🛡 <b>PM SECURITY</b>\n<code>.antispam .pmlog .secretlog .verify</code>\nAuto warn + block (3x)",
    "raid": "🔥 <b>RAID / SPAM</b>\n<code>.raid 10 text</code> | <code>.raid off</code>\n<code>.spam 10 text</code> | <code>.spam off</code>",
    "ghost": "👻 <b>GHOST</b>\n<code>.ghostmod on/off/status</code>",
    "track": "👁 <b>TRACKER</b>\n<code>.track on/off .trackadd .trackdel .tracklist</code>",
    "global": "🌐 <b>GLOBAL</b>\n<code>.gban .ungban .gbanlist .gmute .gunmute</code>",
    "mod": "👮 <b>CHAT MOD</b>\n<code>.ban .unban .kick .mute .unmute .banall .kickall .muteall .unmuteall .tagall .tagallstop .tagme</code>",
    "antilink": "🔗 <b>ANTI</b>\n<code>.antilink .antibot .antidelete .antilinkstatus</code>",
    "warn": "⚠️ <b>WARN</b>\n<code>.warn .unwarn .warns .resetwarns</code>",
    "broadcast": "📢 <b>BROADCAST</b>\n<code>.broadcast</code> | <code>/broadcast</code>",
    "bro": "💕 <b>BRO</b>\n<code>.bro .broall .brodm .brogroup .unbro .brolist</code>",
    "sha": "📜 <b>SHAYARI</b>\n<code>.sha .love</code>",
    "welcome": "👋 <b>WELCOME</b>\n<code>.welcome on/off .setwelcome</code>",
    "afk": "💤 <b>AFK</b>\n<code>.afk .unafk .back .afkstatus</code>",
    "protect": "🔒 <b>PROTECT</b>\n<code>.protect .psend .pfile</code>",
    "notes": "📌 <b>NOTES</b>\n<code>.save .get .notes .clearnote .clearallnotes #name</code>",
    "dl": "📥 <b>DOWNLOAD</b>\n<code>.ytmp3 .ytmp4 .dl .insta .tiktok .fb .social</code>",
    "media": "🎨 <b>MEDIA</b>\n<code>.kang .steal .tts .stt</code>",
    "nuinfo": "📞 <b>NUMBER</b>\n<code>.nuinfo +91…</code>",
    "chat": "🧹 <b>CHAT</b>\n<code>.del .purge</code>",
    "fun": "🎮 <b>FUN</b>\n<code>/dice /couple /td /bomb /kiss /hug .cat .rose .heart</code>",
    "eco": "💰 <b>ECO</b>\n<code>/bal /daily /rob /kill /protect</code>",
    "ai": "🤖 <b>AI</b>\n<code>/chatbot /ai /ask /learn /aiclear</code>",
    "utility": "⚙️ <b>UTILITY</b>\n<code>.ping .alive .id .info .help</code>",
}


@app.on_message(cmd("help"))
@sudo_only
async def help_cmd(client, message: Message):
    if len(message.command) > 1:
        key = message.command[1].lower()
        page = HELP_PAGES.get(key)
        if not page:
            await message.reply_text(
                f"❌ No page: <code>{key}</code>\n<code>.help</code> for full menu."
            )
            return
        await message.reply_text(page)
        return
    await message.reply_text(HELP_INDEX)
