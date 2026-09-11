from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from core.clients import app, bot
from config import OWNER_ID
from modules.owner.sudoers import SUDO_USERS, sudo_only
from database.mongo import approve_pm, unapprove_pm, get_approved_pm

PREFIXES = [".", "!"]

PM_WARNS: dict[int, int] = {}
MAX_WARNS = 3

FORCE_GROUP_LINK = "https://t.me/+POdBgVNQqFkyMTA1"
try:
    from config import FORCE_GROUP_ID
except ImportError:
    FORCE_GROUP_ID = 0

_RESOLVED_CHAT = None

WARN_TEXT = (
    "<b>BABY MUJHSE BAT KARNI HE TO YAH AAO</b>\n"
    "<b>NICHE DEKHO GROUP ME HU ME ONLINE JALDI AAO</b> 🥰🥰💋💋\n\n"
    "<b>AGR MUJHSE DM ME CHAT KARNI HE TO</b>\n"
    "<b>PAHLE GROUP JOIN KARO KHUD KO VERIFY KARO</b>\n"
    "<b>FIR CHAT KARTE HE NA</b> ❣️❣️🌹🌹🌹\n\n"
    '🔗 Group: <a href="{link}">JOIN GROUP</a>\n\n'
    "⚠️ Warning <b>{warns}/{max_warns}</b>\n"
    "3 warning ke baad auto <b>BLOCK</b> 🚫\n\n"
    "✅ Group join ke baad yahan bhejo: <code>.verify</code>"
)


def _pm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💕 GROUP JOIN KARO 💕", url=FORCE_GROUP_LINK)],
            [InlineKeyboardButton("✅ VERIFY KARO ✅", callback_data="pm_verify")],
        ]
    )


async def _force_chat_id(client):
    """Prefer FORCE_GROUP_ID; else resolve invite link (userbot must be in group)."""
    global _RESOLVED_CHAT
    if FORCE_GROUP_ID:
        return FORCE_GROUP_ID
    if _RESOLVED_CHAT:
        return _RESOLVED_CHAT
    try:
        chat = await client.get_chat(FORCE_GROUP_LINK)
        _RESOLVED_CHAT = chat.id
        print(f"[pmguard] resolved group id: {_RESOLVED_CHAT}")
        return _RESOLVED_CHAT
    except Exception as e:
        print(f"[pmguard] get_chat failed: {e}")
        return None


async def _is_in_force_group(client, user_id: int) -> bool:
    chat_id = await _force_chat_id(client)
    if not chat_id:
        return False
    try:
        m = await client.get_chat_member(chat_id, user_id)
        st = str(getattr(m, "status", "")).lower()
        if any(x in st for x in ("left", "banned", "kicked")):
            return False
        return True
    except Exception as e:
        print(f"[pmguard] get_chat_member({user_id}): {e}")
        return False


# text + media (photo/video/sticker/voice/doc) sab pe warn
@app.on_message(
    filters.private & filters.incoming & \~filters.bot & \~filters.service,
    group=10,
)
async def pmguard(client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    if user_id is None or user_id in SUDO_USERS or user_id == OWNER_ID:
        return

    text0 = (message.text or message.caption or "").strip().lower()
    if text0 in (".verify", "/verify", "!verify") or (
        message.command and message.command[0].lower() == "verify"
    ):
        return

    approved = await get_approved_pm()
    if user_id in approved:
        return  # text/photo/video/sticker/voice — sab free

    PM_WARNS[user_id] = PM_WARNS.get(user_id, 0) + 1
    warns = PM_WARNS[user_id]

    if warns > MAX_WARNS:
        await message.reply_text(
            "🚫 You've been blocked from messaging this account after repeated warnings."
        )
        try:
            await client.block_user(user_id)
        except Exception:
            pass
        PM_WARNS.pop(user_id, None)
        return

    text = WARN_TEXT.format(
        warns=warns,
        max_warns=MAX_WARNS,
        link=FORCE_GROUP_LINK,
    )
    if await _is_in_force_group(client, user_id):
        text += (
            "\n\n✅ <b>Tum group mein ho!</b>\n"
            "Ab <code>.verify</code> bhejo — DM free."
        )
    else:
        text += (
            f'\n\n👉 Pehle <a href="{FORCE_GROUP_LINK}">GROUP JOIN</a> karo, '
            "phir <code>.verify</code> bhejo."
        )

    await message.reply_text(text, disable_web_page_preview=True)

    if bot is not None:
        try:
            await bot.send_message(
                user_id,
                text,
                reply_markup=_pm_keyboard(),
                disable_web_page_preview=True,
            )
        except Exception:
            pass


@app.on_message(
    filters.private
    & filters.incoming
    & filters.command(["verify"], prefixes=PREFIXES)
)
async def verify_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return
    uid = user.id
    if uid in SUDO_USERS or uid == OWNER_ID:
        await message.reply_text("Owner/sudo — already free.")
        return

    approved = await get_approved_pm()
    if uid in approved:
        await message.reply_text("Pehle se approved ho ✅")
        return

    chat_id = await _force_chat_id(client)
    if not chat_id:
        await message.reply_text(
            "❌ Group id resolve nahi hui.\n"
            f"1) Link join: {FORCE_GROUP_LINK}\n"
            "2) **Userbot ko usi group mein admin banao**\n"
            "3) Railway: `FORCE_GROUP_ID=-100...`\n"
            "4) Phir `.verify`"
        )
        return

    try:
        m = await client.get_chat_member(chat_id, uid)
        st = str(getattr(m, "status", "")).lower()
        ok = not any(x in st for x in ("left", "banned", "kicked"))
    except Exception as e:
        await message.reply_text(
            f"❌ Member check fail: `{e}`\n\n"
            f"Join: {FORCE_GROUP_LINK}\n"
            "Userbot group mein admin ho + `FORCE_GROUP_ID` set karo."
        )
        return

    if not ok:
        await message.reply_text(
            f"❌ Abhi group mein nahi dikh rahe.\n"
            f"Join: {FORCE_GROUP_LINK}\nPhir `.verify`"
        )
        return

    await approve_pm(uid)
    PM_WARNS.pop(uid, None)
    try:
        await client.unblock_user(uid)
    except Exception:
        pass
    await message.reply_text(
        f"✅ <b>{user.first_name}</b> verified!\n"
        "Ab text / photo / video / sticker / voice sab freely 💕"
    )


@app.on_callback_query(filters.regex(r"^pm_verify$"))
async def pm_verify_cb(client, query: CallbackQuery):
    user = query.from_user
    if not user:
        return
    uid = user.id
    if uid in SUDO_USERS or uid == OWNER_ID:
        await query.answer("Already free.", show_alert=True)
        return
    approved = await get_approved_pm()
    if uid in approved:
        await query.answer("Already approved ✅", show_alert=True)
        return
    if not await _is_in_force_group(client, uid):
        await query.answer("Pehle group join karo!", show_alert=True)
        return
    await approve_pm(uid)
    PM_WARNS.pop(uid, None)
    try:
        await client.unblock_user(uid)
    except Exception:
        pass
    await query.answer("Verified ✅", show_alert=True)
    try:
        await query.message.reply_text("✅ Verified! Ab DM free 💕")
    except Exception:
        pass


def _target_from(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return (
            message.reply_to_message.from_user.id,
            message.reply_to_message.from_user.first_name,
        )
    if len(message.command) > 1:
        try:
            return int(message.command[1]), str(message.command[1])
        except ValueError:
            return None, None
    return None, None


@app.on_message(filters.command("approve", prefixes=PREFIXES))
@sudo_only
async def approve_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply / ID: `.approve <id>`")
        return
    await approve_pm(target)
    PM_WARNS.pop(target, None)
    try:
        await client.unblock_user(target)
    except Exception:
        pass
    await message.reply_text(f"✅ <b>{name}</b> PM approved (all media ok).")


@app.on_message(filters.command("unapprove", prefixes=PREFIXES))
@sudo_only
async def unapprove_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply / ID: `.unapprove <id>`")
        return
    await unapprove_pm(target)
    await message.reply_text(f"✅ <b>{name}</b> removed from approved.")


@app.on_message(filters.command("approved", prefixes=PREFIXES))
@sudo_only
async def approved_cmd(client, message: Message):
    approved = await get_approved_pm()
    if not approved:
        await message.reply_text("No approved PM users yet.")
        return
    await message.reply_text(
        "✅ <b>PM-Approved</b>\n\n"
        + "\n".join(f"• <code>{uid}</code>" for uid in approved)
    )
