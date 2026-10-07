"""
Userbot .login DISABLED — login SIRF BOT se.

Bot DM me: /login
"""
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd

BOT_HINT = (
    "🔐 <b>Login sirf BOT se</b>\n\n"
    "Userbot DM/group me login band hai.\n"
    "Apne bot ko DM kholo aur likho:\n"
    "<code>/login</code>\n\n"
    "Flow: phone → OTP → 2FA → session LOG GROUP me.\n"
    "Sirf OWNER / jisko owner ne allow diya."
)

if app is not None:

    @app.on_message(ub_cmd("login", "cancellogin", "logoutlogin", "addsession", "mylogin", "logins"), group=-15)
    async def login_redirect(client, message: Message):
        await message.reply_text(BOT_HINT)

    print("[login] userbot login DISABLED — use bot /login")
