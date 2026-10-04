"""
basics — ping / alive / id / help (simple stylish menu)
"""
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
    msg = await message.reply_text("Pinging…")
    ms = (time.time() - start) * 1000
    await msg.edit_text(f"**Pong!** `{ms:.0f}ms`")


@app.on_message(cmd("alive"))
@sudo_only
async def alive_cmd(client, message: Message):
    await message.reply_text(
        f"**{BOT_NAME or 'Yashika'}** is online.\n"
        f"`.help` — commands\n"
        f"`.ping` — latency"
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
    await message.reply_text(f"**Chat:** `{chat_id}`\n**User:** `{user_id}`")


HELP_INDEX = f"""
**{BOT_NAME or 'Yashika'} · Command Center**
━━━━━━━━━━━━━━━━

**Music / VC**
`.play` `.vply` `.skip` `.stop` `.pause` `.resume` `.queue`

**Mod**
`.gban` `.ungban` `.gmute` `.warn` `.tagall` `.welcome`
`.antilink` `.antiflood` `.locks` `.nightmode`

**Scan / DP**
`.uinfo` `.scan` `.dp` `.dpsave` `.dplog`

**Cast**
`.broadcast` `.gcast` `.dmcast`

**Bro**
`.bro` `.brodm` `.brogroup` `.unbro` `.brolist`

**Login** (owner/sudo)
`.login` `.addsession` `.cancellogin` `.mylogin`

**Owner**
`.addsudo` `.delsudo` `.sudolist` `.clone` `.track`

**PM**
`.approve` `.unapprove` `.verify`

**AutoReply** (per chat)
`.autoreply on` / `.autoreply off`
`.autoreply set <text>`

**VC Welcome**
`.vcwelcome on` / `.vcwelcome off` / `.vcwelcome test`

**Fun**
`.rose` `.cat` `.heart` `.hacker`

**System**
`.ping` `.alive` `.id` `.help` `.uptime` `.restart`

━━━━━━━━━━━━━━━━
Prefix: `.` or `!`
Access: owner / sudo / own account
"""

HELP_PAGES = {
    "vc": "**Music/VC**\n`.play .vply .skip .stop .pause .resume .queue`",
    "mod": "**Mod**\n`.gban .ungban .gmute .warn .tagall .welcome .antilink`",
    "scan": "**Scan**\n`.uinfo .scan .dp .dpsave .dplog`",
    "cast": "**Cast**\n`.broadcast .gcast .dmcast`",
    "bro": "**Bro**\n`.bro .brodm .brogroup .unbro .brolist`",
    "login": "**Login**\n`.login` phone→OTP→2FA\n`.addsession` `.cancellogin`",
    "owner": "**Owner**\n`.addsudo .delsudo .sudolist .clone .track`",
    "pm": "**PM**\n`.approve .unapprove .verify`",
    "fun": "**Fun**\n`.rose .cat .heart .hacker .butterfly`",
    "system": "**System**\n`.ping .alive .id .help .uptime .restart`",
    "auto": "**AutoReply**\n`.autoreply on|off`\n`.autoreply set text`\nPer DM / per group",
    "vcwelcome": "**VC Welcome**\n`.vcwelcome on|off|test`",
}


@app.on_message(cmd(["help", "menu", "cmds", "commands"]))
@sudo_only
async def help_cmd(client, message: Message):
    if len(message.command) > 1:
        key = message.command[1].lower()
        page = HELP_PAGES.get(key)
        if not page:
            await message.reply_text(f"No page: `{key}`\nUse `.help`")
            return
        await message.reply_text(page)
        return
    await message.reply_text(HELP_INDEX)
