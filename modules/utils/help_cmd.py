"""
.help — command overview (pure userbot)
"""
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

HELP_TEXT = """
✨ <b>Yashika Userbot — Help</b>
━━━━━━━━━━━━━━━━

🎵 <b>Music</b>
<code>.play</code> <code>.vply</code> <code>.skip</code> <code>.stop</code>
<code>.pause</code> <code>.resume</code>

👑 <b>Owner / Sudo</b>
<code>.addsudo</code> <code>.delsudo</code> <code>.sudolist</code>
<code>.clone</code> <code>.back</code> <code>.clonemode</code>

📢 <b>Broadcast</b>
<code>.broadcast</code> — all tracked
<code>.gcast</code> — groups only
<code>.dmcast</code> — DMs only

💕 <b>Bro</b>
<code>.bro</code> reply — DM+group auto-reply
<code>.brodm</code> / <code>.brogroup</code>
<code>.unbro</code> <code>.brolist</code>

👮 <b>Mod</b>
<code>.gban</code> <code>.gmute</code> <code>.warn</code>
<code>.tagall</code> <code>.welcome</code> <code>.antilink</code>

🛡 <b>PM</b>
<code>.approve</code> <code>.antispam</code> <code>.secretlog</code>

💰 <b>Economy</b>
<code>.bal</code> <code>.daily</code> <code>.rob</code>

🔧 <b>Utils</b>
<code>.afk</code> <code>.info</code> <code>.id</code> <code>.notes</code>
"""


@app.on_message(filters.command(["help", "cmds", "commands"], prefixes=PREFIXES))
@sudo_only
async def help_cmd(client, message: Message):
    await message.reply_text(HELP_TEXT)
