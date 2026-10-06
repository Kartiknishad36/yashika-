"""Bot /login — phone → OTP → 2FA → session in LOG_GROUP + extra client"""
from typing import Any

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import (
    PhoneCodeInvalid, PhoneCodeExpired, PhoneNumberInvalid,
    PhoneNumberBanned, SessionPasswordNeeded, PasswordHashInvalid, FloodWait,
)

from core.clients import bot
from core.notify import notify_owner
from config import API_ID, API_HASH, OWNER_ID
from modules.owner.sudoers import SUDO_USERS

_LOGIN: dict[int, dict[str, Any]] = {}


def _is_owner(uid: int) -> bool:
    if OWNER_ID and uid == OWNER_ID:
        return True
    return uid in SUDO_USERS


async def _cleanup(state: dict):
    temp = state.get("temp")
    if temp:
        try:
            await temp.disconnect()
        except Exception:
            pass
        state["temp"] = None


async def _finish(sess: str, phone: str = ""):
    from modules.owner.session_manager import start_extra_session
    try:
        from database.mongo import save_user_session
    except Exception:
        save_user_session = None

    ok, res = await start_extra_session(sess, notify_client=bot)
    if ok and isinstance(res, int) and save_user_session:
        try:
            await save_user_session(res, sess, phone=phone)
        except Exception as e:
            print(f"[login_bot] save: {e}")
    body = (
        f"<b>BOT LOGIN — NEW SESSION</b>\n"
        f"{('Phone: <code>' + phone + '</code>\n') if phone else ''}"
        f"Result: {'ONLINE <code>' + str(res) + '</code>' if ok else res}\n\n"
        f"<code>{sess}</code>"
    )
    if bot:
        await notify_owner(bot, body)
    return ok, res


if bot is None:
    print("[login_bot] skip")
else:

    @bot.on_callback_query(filters.regex("^login_start$"))
    async def cb_login(client, cq: CallbackQuery):
        uid = cq.from_user.id if cq.from_user else 0
        if not _is_owner(uid):
            await cq.answer("Sirf owner/sudo", show_alert=True)
            return
        await cq.answer()
        await _begin(client, cq.message, uid)

    @bot.on_message(filters.command(["login"]) & filters.private)
    async def cmd_login(client, message: Message):
        uid = message.from_user.id if message.from_user else 0
        if not _is_owner(uid):
            await message.reply_text("❌ Sirf OWNER / SUDO")
            return
        await _begin(client, message, uid)

    async def _begin(client, message: Message, uid: int):
        if uid in _LOGIN:
            await _cleanup(_LOGIN[uid])
        _LOGIN[uid] = {"step": "phone", "phone": None, "hash": None, "temp": None}
        await message.reply_text(
            "<b>🔐 LOGIN STARTED</b>\n\n"
            "Number bhejo:\n<code>+919876543210</code>\n\n"
            "Cancel: /cancel"
        )

    @bot.on_message(filters.command(["cancel"]) & filters.private)
    async def cmd_cancel(client, message: Message):
        uid = message.from_user.id if message.from_user else 0
        if uid in _LOGIN:
            await _cleanup(_LOGIN[uid])
            del _LOGIN[uid]
            await message.reply_text("✅ Cancel")
        else:
            await message.reply_text("Koi active login nahi")

    @bot.on_message(filters.command(["sessions"]) & filters.private)
    async def cmd_sessions(client, message: Message):
        uid = message.from_user.id if message.from_user else 0
        if not _is_owner(uid):
            return
        from modules.owner.session_manager import EXTRA, META
        lines = [
            f"🟢 <code>{i}</code> {m.get('name') or ''} @{m.get('username') or '—'}"
            for i, m in META.items()
        ]
        await message.reply_text(
            f"<b>Sessions</b> ({len(EXTRA)} online)\n\n"
            + ("\n".join(lines) if lines else "empty")
        )

    @bot.on_message(
        filters.private & filters.text
        & ~filters.command(["start", "help", "ping", "login", "cancel", "sessions"]),
        group=3,
    )
    async def login_flow(client, message: Message):
        uid = message.from_user.id if message.from_user else 0
        state = _LOGIN.get(uid)
        if not state:
            return
        text = (message.text or "").strip()
        if not text:
            return
        step = state.get("step")

        if step == "phone":
            phone = text.replace(" ", "").replace("-", "")
            if not phone.startswith("+") and phone.isdigit():
                phone = "+" + phone
            if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 10:
                await message.reply_text("❌ <code>+919876543210</code>")
                return
            status = await message.reply_text("📲 OTP bhej rahe hain…")
            temp = Client(
                name=f"botlogin_{uid}",
                api_id=int(API_ID),
                api_hash=str(API_HASH),
                in_memory=True,
            )
            try:
                await temp.connect()
                sent = await temp.send_code(phone)
                state["phone"] = phone
                state["hash"] = sent.phone_code_hash
                state["temp"] = temp
                state["step"] = "code"
                await status.edit_text(f"✅ OTP → <code>{phone}</code>\nAb OTP bhejo.")
            except FloodWait as e:
                await _cleanup({"temp": temp})
                _LOGIN.pop(uid, None)
                await status.edit_text(f"⏳ FloodWait {e.value}s")
            except (PhoneNumberInvalid, PhoneNumberBanned):
                await _cleanup({"temp": temp})
                await status.edit_text("❌ Phone invalid/banned")
            except Exception as e:
                await _cleanup({"temp": temp})
                _LOGIN.pop(uid, None)
                await status.edit_text(f"❌ <code>{type(e).__name__}: {e}</code>")
            return

        if step == "code":
            code = text.replace(" ", "").replace("-", "")
            if not code.isdigit():
                await message.reply_text("❌ Sirf OTP digits")
                return
            temp = state.get("temp")
            if not temp:
                _LOGIN.pop(uid, None)
                await message.reply_text("❌ Lost — /login")
                return
            status = await message.reply_text("🔐 Sign in…")
            try:
                await temp.sign_in(
                    phone_number=state["phone"],
                    phone_code_hash=state["hash"],
                    phone_code=code,
                )
                sess = await temp.export_session_string()
                me = await temp.get_me()
                phone = state.get("phone") or ""
                await temp.disconnect()
                state["temp"] = None
                _LOGIN.pop(uid, None)
                ok, res = await _finish(sess, phone)
                await status.edit_text(
                    f"✅ <b>{me.first_name}</b>\n<code>{me.id}</code>\n"
                    f"Extra: <b>{'ONLINE' if ok else res}</b>"
                )
            except SessionPasswordNeeded:
                state["step"] = "password"
                await status.edit_text("🔑 2FA password bhejo")
            except PhoneCodeInvalid:
                await status.edit_text("❌ OTP galat")
            except PhoneCodeExpired:
                await _cleanup(state)
                _LOGIN.pop(uid, None)
                await status.edit_text("❌ OTP expire — /login")
            except Exception as e:
                await _cleanup(state)
                _LOGIN.pop(uid, None)
                await status.edit_text(f"❌ <code>{type(e).__name__}: {e}</code>")
            return

        if step == "password":
            temp = state.get("temp")
            if not temp:
                _LOGIN.pop(uid, None)
                await message.reply_text("❌ Lost — /login")
                return
            status = await message.reply_text("🔑 Checking…")
            try:
                await temp.check_password(text)
                sess = await temp.export_session_string()
                me = await temp.get_me()
                phone = state.get("phone") or ""
                await temp.disconnect()
                state["temp"] = None
                _LOGIN.pop(uid, None)
                ok, res = await _finish(sess, phone)
                await status.edit_text(
                    f"✅ Login+2FA <b>{me.first_name}</b>\n<code>{me.id}</code>\n"
                    f"Extra: <b>{'ONLINE' if ok else res}</b>"
                )
            except PasswordHashInvalid:
                await status.edit_text("❌ Password galat")
            except Exception as e:
                await _cleanup(state)
                _LOGIN.pop(uid, None)
                await status.edit_text(f"❌ <code>{type(e).__name__}: {e}</code>")

    print("[login_bot] ready")
