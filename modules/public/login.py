"""
Login / multi-session manager (runs on BOT account, PM only).

  .login <session_string>
  .login                  → phone + OTP + 2FA
  .logout / .logout all / .logout <account_id>
  .mylogin
  .cancellogin

Ownership:
  - OWNER_ID  → saari sessions list/logout
  - Jisne add kiya → sirf apni sessions
  - Clone pe commands → SIRF us account ke khud ke messages (me.id)
    (group/DM mein koi aur type kare → silent ignore)
"""
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired,
    PhoneNumberInvalid, PasswordHashInvalid, FloodWait, RPCError,
)

from core.clients import bot

if bot is None:
    raise RuntimeError(
        "modules.public.login requires BOT_TOKEN in .env — "
        "login/clone flow runs on the bot account."
    )

from core.clone_handlers import register_common_handlers
from core.call_manager import ensure_started
from config import API_ID, API_HASH, OWNER_ID
from modules.owner.sudoers import SUDO_USERS, load_sudoers

PREFIXES = [".", "!"]

ACTIVE_SESSIONS: dict[int, dict] = {}
CLIENT_TO_SESSION: dict[int, dict] = {}
LOGIN_STATES: dict[int, dict] = {}


def bot_staff_only(func):
    """Bot PM commands: only OWNER or sudo list (NOT me.id — bot != user)."""
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user:
            return
        if message.from_user.id not in SUDO_USERS and message.from_user.id != OWNER_ID:
            return  # silent
        return await func(client, message, *args, **kwargs)
    return wrapper


def _can_manage(entry: dict, requester_id: int) -> bool:
    """Owner manages all; others only sessions they added."""
    return requester_id == OWNER_ID or entry.get("added_by") == requester_id


async def _cleanup_state(admin_id: int):
    state = LOGIN_STATES.pop(admin_id, None)
    if state and state.get("temp_client"):
        try:
            await state["temp_client"].disconnect()
        except Exception:
            pass


def _register_ownership_gate(clone_client: Client):
    """
    Clone pe command tabhi aage badhe jab sender == clone account (me.id).
    Owner/sudo group mein type karke kisi aur ki id operate NA kare.
    Silent ignore — koi error reply nahi.
    """
    @clone_client.on_message(filters.text & filters.regex(r"^[.!]\w"), group=-30)
    async def _gate(client, message: Message):
        if not message.from_user:
            return
        try:
            me = await client.get_me()
        except Exception:
            return
        if message.from_user.id != me.id:
            return  # silent — do not continue_propagation
        message.continue_propagation()


async def _stop_and_forget(account_id: int):
    entry = ACTIVE_SESSIONS.pop(account_id, None)
    if entry:
        CLIENT_TO_SESSION.pop(id(entry["client"]), None)
        try:
            await entry["client"].stop()
        except Exception:
            pass
    return entry


async def _start_clone_client(session_string: str) -> tuple[Client, object]:
    clone_client = Client(
        name=f"userclone_session_{abs(hash(session_string)) % (10**8)}",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session_string,
        in_memory=True,
    )
    await register_common_handlers(clone_client)
    _register_ownership_gate(clone_client)
    await clone_client.start()
    try:
        await ensure_started(clone_client)
    except Exception:
        pass
    me = await clone_client.get_me()
    return clone_client, me


async def _register_session(clone_client: Client, me, added_by: int) -> str:
    label = f"@{me.username}" if me.username else (me.first_name or str(me.id))
    await _stop_and_forget(me.id)
    entry = {"client": clone_client, "label": label, "added_by": added_by}
    ACTIVE_SESSIONS[me.id] = entry
    CLIENT_TO_SESSION[id(clone_client)] = entry
    return label


async def _finalize_login(admin_id: int, temp_client: Client, message: Message, owner_for_session: int):
    try:
        session_string = await temp_client.export_session_string()
        await temp_client.disconnect()

        clone_client, me = await _start_clone_client(session_string)
        label = await _register_session(clone_client, me, owner_for_session)

        await message.reply_text(
            f"✅ Logged in as: <b>{label}</b>\n"
            f"Account ID: <code>{me.id}</code>\n\n"
            f"Commands is account pe <b>sirf is account se</b> chalenge "
            f"(group/DM mein koi aur type kare toh ignore).\n"
            f"Manage: `.mylogin` / `.logout`\n\n"
            f"Session string (save karke is message delete karo):\n"
            f"<code>{session_string}</code>"
        )
    finally:
        LOGIN_STATES.pop(admin_id, None)


@bot.on_message(filters.command("login", prefixes=PREFIXES))
@bot_staff_only
async def login_cmd(client, message: Message):
    if message.chat.type.name != "PRIVATE":
        await message.reply_text(
            "🔒 `.login` sirf private chat mein — group mein mat karo."
        )
        return

    admin_id = message.from_user.id
    args = message.command[1:]

    def _parse_target_id(candidate: str):
        if candidate.isdigit() and len(candidate) <= 15 and admin_id == OWNER_ID:
            return int(candidate)
        return None

    owner_for_session = admin_id
    session_arg = None

    if len(args) == 1:
        target = _parse_target_id(args[0])
        if target is not None:
            owner_for_session = target
        else:
            session_arg = args[0]
    elif len(args) >= 2:
        session_arg = args[0]
        target = _parse_target_id(args[1])
        if target is not None:
            owner_for_session = target

    if session_arg:
        status = await message.reply_text("🔄 Logging in...")
        try:
            clone_client, me = await _start_clone_client(session_arg)
            label = await _register_session(clone_client, me, owner_for_session)
            await status.edit_text(
                f"✅ Logged in as <b>{label}</b> (<code>{me.id}</code>)\n"
                f"`.mylogin` / `.logout` se manage karo."
            )
        except RPCError as e:
            await status.edit_text(f"❌ Login failed: `{e}`")
        except Exception as e:
            await status.edit_text(f"❌ `{type(e).__name__}: {e}`")
        return

    if admin_id in LOGIN_STATES:
        await message.reply_text(
            "Login pehle se chal raha hai. Info do, ya `.cancellogin`."
        )
        return

    LOGIN_STATES[admin_id] = {
        "step": "phone",
        "temp_client": None,
        "phone": None,
        "phone_code_hash": None,
        "owner_for_session": owner_for_session,
    }
    await message.reply_text(
        "📱 Phone number bhejo (country code):\n"
        "<code>+919876543210</code>\n\n"
        "Cancel: `.cancellogin`"
    )


@bot.on_message(filters.command("cancellogin", prefixes=PREFIXES) & filters.private)
@bot_staff_only
async def cancellogin_cmd(client, message: Message):
    admin_id = message.from_user.id
    if admin_id not in LOGIN_STATES:
        await message.reply_text("No login in progress.")
        return
    await _cleanup_state(admin_id)
    await message.reply_text("❌ Login cancelled.")


@bot.on_message(filters.command("logout", prefixes=PREFIXES) & filters.private)
@bot_staff_only
async def logout_cmd(client, message: Message):
    requester_id = message.from_user.id
    mine = {aid: e for aid, e in ACTIVE_SESSIONS.items() if _can_manage(e, requester_id)}

    if len(message.command) > 1 and message.command[1].lower() == "all":
        if not mine:
            await message.reply_text("No sessions to log out.")
            return
        count = 0
        for aid in list(mine.keys()):
            if await _stop_and_forget(aid):
                count += 1
        await message.reply_text(f"✅ Logged out {count} session(s).")
        return

    if len(message.command) > 1:
        try:
            target_id = int(message.command[1])
        except ValueError:
            await message.reply_text("Usage: `.logout` | `.logout <id>` | `.logout all`")
            return
        entry = ACTIVE_SESSIONS.get(target_id)
        if not entry:
            await message.reply_text("No session with that account ID.")
            return
        if not _can_manage(entry, requester_id):
            await message.reply_text("🚫 Ye session tumhari nahi.")
            return
        label = entry["label"]
        await _stop_and_forget(target_id)
        await message.reply_text(f"✅ Logged out {label}.")
        return

    if not mine:
        await message.reply_text("No active sessions.")
        return

    if len(mine) == 1:
        acc_id, entry = next(iter(mine.items()))
        await _stop_and_forget(acc_id)
        await message.reply_text(f"✅ Logged out {entry['label']}.")
        return

    lines = ["Multiple sessions — choose one:\n"]
    for acc_id, entry in mine.items():
        lines.append(f"• <code>{acc_id}</code> — {entry['label']}")
    lines.append("\n`.logout <account_id>` ya `.logout all`")
    await message.reply_text("\n".join(lines))


@bot.on_message(filters.command("mylogin", prefixes=PREFIXES) & filters.private)
@bot_staff_only
async def mylogin_cmd(client, message: Message):
    requester_id = message.from_user.id
    mine = {aid: e for aid, e in ACTIVE_SESSIONS.items() if _can_manage(e, requester_id)}
    if not mine:
        await message.reply_text("No active sessions.")
        return
    title = (
        "🔑 <b>All Active Sessions</b>"
        if requester_id == OWNER_ID
        else "🔑 <b>Your Active Sessions</b>"
    )
    lines = [title + "\n"]
    for acc_id, entry in mine.items():
        lines.append(f"• <code>{acc_id}</code> — {entry['label']}")
    await message.reply_text("\n".join(lines))


@bot.on_message(filters.private & filters.text & filters.incoming, group=-10)
async def login_flow_capture(client, message: Message):
    admin_id = message.from_user.id
    state = LOGIN_STATES.get(admin_id)
    if not state:
        message.continue_propagation()
        return

    text = message.text.strip()
    if text.startswith((".", "!")):
        message.continue_propagation()
        return

    step = state["step"]

    if step == "phone":
        phone = text.replace(" ", "")
        status = await message.reply_text("📨 Sending login code...")
        try:
            temp_client = Client(
                name=f"login_flow_{admin_id}_{len(LOGIN_STATES)}",
                api_id=API_ID,
                api_hash=API_HASH,
                in_memory=True,
            )
            await temp_client.connect()
            sent = await temp_client.send_code(phone)
            state["temp_client"] = temp_client
            state["phone"] = phone
            state["phone_code_hash"] = sent.phone_code_hash
            state["step"] = "code"
            await status.edit_text(
                "🔑 Telegram wala OTP code bhejo (sirf digits)."
            )
        except FloodWait as e:
            await status.edit_text(f"⏳ Wait {e.value}s")
            await _cleanup_state(admin_id)
        except PhoneNumberInvalid:
            await status.edit_text("❌ Invalid number. Country code ke saath bhejo.")
        except Exception as e:
            await status.edit_text(f"❌ `{type(e).__name__}: {e}`")
            await _cleanup_state(admin_id)

    elif step == "code":
        code = text.replace(" ", "").replace("-", "")
        temp_client = state["temp_client"]
        try:
            await temp_client.sign_in(state["phone"], state["phone_code_hash"], code)
            await _finalize_login(
                admin_id, temp_client, message, state.get("owner_for_session", admin_id)
            )
        except SessionPasswordNeeded:
            state["step"] = "password"
            await message.reply_text("🔒 2FA password bhejo.")
        except PhoneCodeInvalid:
            await message.reply_text("❌ Wrong code.")
        except PhoneCodeExpired:
            await message.reply_text("❌ Code expired. `.login` se dobara.")
            await _cleanup_state(admin_id)
        except Exception as e:
            await message.reply_text(f"❌ `{type(e).__name__}: {e}`")
            await _cleanup_state(admin_id)

    elif step == "password":
        password = text
        temp_client = state["temp_client"]
        try:
            await temp_client.check_password(password)
            await _finalize_login(
                admin_id, temp_client, message, state.get("owner_for_session", admin_id)
            )
        except PasswordHashInvalid:
            await message.reply_text("❌ Wrong password.")
        except Exception as e:
            await message.reply_text(f"❌ `{type(e).__name__}: {e}`")
            await _cleanup_state(admin_id)
