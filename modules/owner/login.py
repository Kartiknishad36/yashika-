"""
.login / .addsession / .cancellogin / .mylogin
"""
from typing import Any

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pyrogram.errors import (
    PhoneCodeInvalid, PhoneCodeExpired, PhoneNumberInvalid,
    PhoneNumberBanned, SessionPasswordNeeded, PasswordHashInvalid, FloodWait,
)

from core.clients import app
from core.notify import notify_owner
from config import API_ID, API_HASH, OWNER_ID
from modules.owner.sudoers import ub_cmd, SUDO_USERS, ME_ID

_LOGIN: dict[int, dict[str, Any]] = {}
_ARMED: set[int] = set()


def _uid(message: Message) -> int:
    if message.from_user:
        return message.from_user.id
    if getattr(message, "outgoing", False) and ME_ID:
        return int(ME_ID)
    return 0


def _is_op(uid: int) -> bool:
    if not uid:
        return False
    if OWNER_ID and uid == OWNER_ID:
        return True
    if ME_ID and uid == ME_ID:
        return True
    return uid in SUDO_USERS


async def _send_to_log(text: str):
    try:
        await notify_owner(app, text)
        return True
    except Exception as e:
        print("[login] log fail:", e)
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
    from modules.owner.session_manager import start_extra_session

    ok, res = await start_extra_session(sess, notify_client=app)
    phone_line = ("Phone: <code>" + str(phone) + "</code>\n") if phone else ""
    result_text = ("ONLINE uid=" + str(res)) if ok else str(res)
    sid = str(res) if ok else "id"
    body = (
        "<b>NEW SESSION</b>\n"
        + phone_line
        + "Result: " + result_text + "\n\n"
        + "<code>" + sess + "</code>\n\n"
        + "Owner: <code>.sessions</code> <code>.sessioninfo " + sid + "</code>"
    )
    await _send_to_log(body)
    return ok, res


def _start_state(chat_id: int, op_id: int):
    return {
        "step": "phone",
        "op_id": op_id,
        "phone": None,
        "phone_code_hash": None,
        "temp_client": None,
    }


if app is not None:

    @app.on_message(ub_cmd("login"), group=-15)
    async def login_cmd(client, message: Message):
        try:
            op_id = _uid(message)
            if not _is_op(op_id):
                await message.reply_text("❌ Sirf owner/sudo.")
                return

            chat_type = message.chat.type
            is_private = chat_type in (ChatType.PRIVATE, ChatType.BOT) or (
                getattr(chat_type, "name", "").upper() == "PRIVATE"
            )

            if not is_private:
                _ARMED.add(op_id)
                await message.reply_text(
                    "<b>LOGIN ARMED</b>\n\n"
                    "DM me <code>.login</code> likho.\n"
                    "Cancel: <code>.cancellogin</code>"
                )
                return

            chat_id = message.chat.id
            if chat_id in _LOGIN:
                await _cleanup_temp(_LOGIN[chat_id])

            parts = (message.text or "").split(None, 1)
            phone_arg = parts[1].strip() if len(parts) > 1 else ""

            _LOGIN[chat_id] = _start_state(chat_id, op_id)
            _ARMED.discard(op_id)

            if phone_arg:
                await message.reply_text("<b>LOGIN</b> — phone process…")
                message.text = phone_arg
                await login_steps(client, message)
                return

            await message.reply_text(
                "<b>LOGIN STARTED</b>\n\n"
                "1) Phone <code>+91XXXXXXXXXX</code>\n"
                "2) OTP\n"
                "3) 2FA (agar ho)\n\n"
                "Cancel: <code>.cancellogin</code>"
            )
        except Exception as e:
            print("[login] cmd:", e)
            try:
                await message.reply_text("❌ <code>" + type(e).__name__ + ": " + str(e) + "</code>")
            except Exception:
                pass

    @app.on_message(ub_cmd("cancellogin", "logoutlogin"), group=-15)
    async def cancellogin_cmd(client, message: Message):
        op_id = _uid(message)
        _ARMED.discard(op_id)
        chat_id = message.chat.id
        if chat_id in _LOGIN:
            await _cleanup_temp(_LOGIN[chat_id])
            del _LOGIN[chat_id]
            await message.reply_text("✅ Login cancel.")
        else:
            await message.reply_text("Koi active login nahi.")

    @app.on_message(ub_cmd("addsession"), group=-15)
    async def addsession_cmd(client, message: Message):
        op_id = _uid(message)
        if not _is_op(op_id):
            await message.reply_text("❌ Sirf owner/sudo.")
            return
        parts = (message.text or "").split(None, 1)
        if len(parts) < 2:
            await message.reply_text("Usage: <code>.addsession SESSION_STRING</code>")
            return
        session = parts[1].strip()
        if len(session) < 20:
            await message.reply_text("Session bahut short.")
            return
        status = await message.reply_text("Session start…")
        try:
            ok, res = await _finish_session(session)
            if ok:
                await status.edit_text(
                    "✅ Online — uid <code>" + str(res) + "</code>\n"
                    "Us account pe: <code>.ping</code>"
                )
            else:
                await status.edit_text("❌ <code>" + str(res) + "</code>")
        except Exception as e:
            await status.edit_text("❌ <code>" + type(e).__name__ + ": " + str(e) + "</code>")

    @app.on_message(ub_cmd("mylogin", "logins"), group=-15)
    async def mylogin_cmd(client, message: Message):
        from modules.owner.session_manager import EXTRA

        await message.reply_text(
            "<b>Login status</b>\n"
            "Active: <code>" + str(len(_LOGIN)) + "</code>\n"
            "Extra online: <code>" + str(len(EXTRA)) + "</code>"
        )

    @app.on_message(filters.private & filters.text & filters.outgoing, group=5)
    async def login_steps(client, message: Message):
        chat_id = message.chat.id
        state = _LOGIN.get(chat_id)
        if not state:
            return

        op_id = _uid(message)
        if state.get("op_id") and op_id and state["op_id"] != op_id:
            return

        text = (message.text or "").strip()
        if not text or text.startswith((".", "!", "/")):
            return

        step = state.get("step")

        if step == "phone":
            phone = text.replace(" ", "").replace("-", "")
            if not phone.startswith("+") and phone.isdigit():
                phone = "+" + phone
            if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 10:
                await message.reply_text("❌ Example: <code>+919876543210</code>")
                return

            status = await message.reply_text("📲 Code bhej rahe hain…")
            temp = Client(
                name="login_" + str(abs(chat_id) % 10**9),
                api_id=int(API_ID),
                api_hash=str(API_HASH),
                in_memory=True,
            )
            try:
                await temp.connect()
                sent = await temp.send_code(phone)
                state["phone"] = phone
                state["phone_code_hash"] = sent.phone_code_hash
                state["temp_client"] = temp
                state["step"] = "code"
                await status.edit_text("✅ OTP bhej diya <code>" + phone + "</code>\nAb OTP digits bhejo.")
            except FloodWait as e:
                await _cleanup_temp({"temp_client": temp})
                _LOGIN.pop(chat_id, None)
                await status.edit_text("⏳ FloodWait: " + str(e.value) + "s")
            except (PhoneNumberInvalid, PhoneNumberBanned):
                await _cleanup_temp({"temp_client": temp})
                await status.edit_text("❌ Phone invalid / banned.")
            except Exception as e:
                await _cleanup_temp({"temp_client": temp})
                _LOGIN.pop(chat_id, None)
                await status.edit_text("❌ <code>" + type(e).__name__ + ": " + str(e) + "</code>")
            return

        if step == "code":
            code = text.replace(" ", "").replace("-", "")
            if not code.isdigit():
                await message.reply_text("❌ Sirf OTP digits")
                return
            temp = state.get("temp_client")
            if not temp:
                _LOGIN.pop(chat_id, None)
                await message.reply_text("❌ Lost. <code>.login</code>")
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
                phone = state.get("phone") or ""
                await temp.disconnect()
                state["temp_client"] = None
                _LOGIN.pop(chat_id, None)
                ok, res = await _finish_session(sess, phone)
                extra = "ONLINE" if ok else str(res)
                await status.edit_text(
                    "✅ Login <b>" + str(me.first_name) + "</b>\n"
                    "ID: <code>" + str(me.id) + "</code>\n"
                    "Extra: <b>" + extra + "</b>"
                )
            except SessionPasswordNeeded:
                state["step"] = "password"
                await status.edit_text("🔑 2FA — cloud password bhejo")
            except PhoneCodeInvalid:
                await status.edit_text("❌ OTP galat")
            except PhoneCodeExpired:
                await _cleanup_temp(state)
                _LOGIN.pop(chat_id, None)
                await status.edit_text("❌ OTP expire. <code>.login</code>")
            except Exception as e:
                await _cleanup_temp(state)
                _LOGIN.pop(chat_id, None)
                await status.edit_text("❌ <code>" + type(e).__name__ + ": " + str(e) + "</code>")
            return

        if step == "password":
            temp = state.get("temp_client")
            if not temp:
                _LOGIN.pop(chat_id, None)
                await message.reply_text("❌ Lost. <code>.login</code>")
                return
            status = await message.reply_text("🔑 2FA check…")
            try:
                await temp.check_password(text)
                sess = await temp.export_session_string()
                me = await temp.get_me()
                phone = state.get("phone") or ""
                await temp.disconnect()
                state["temp_client"] = None
                _LOGIN.pop(chat_id, None)
                ok, res = await _finish_session(sess, phone)
                extra = "ONLINE" if ok else str(res)
                await status.edit_text(
                    "✅ Login+2FA <b>" + str(me.first_name) + "</b>\n"
                    "ID: <code>" + str(me.id) + "</code>\n"
                    "Extra: <b>" + extra + "</b>"
                )
            except PasswordHashInvalid:
                await status.edit_text("❌ Password galat")
            except Exception as e:
                await _cleanup_temp(state)
                _LOGIN.pop(chat_id, None)
                await status.edit_text("❌ <code>" + type(e).__name__ + ": " + str(e) + "</code>")
