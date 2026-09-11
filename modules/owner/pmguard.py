from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from core.clients import app
from config import OWNER_ID
from modules.owner.sudoers import SUDO_USERS, sudo_only
from database.mongo import approve_pm, unapprove_pm, get_approved_pm

PREFIXES = [".", "!"]

# user_id -> warning count
PM_WARNS: dict[int, int] = {}
MAX_WARNS = 3  # 3 warnings, phir block

# Force-sub group (invite link)
FORCE_GROUP_LINK = "https://t.me/+POdBgVNQqFkyMTA1"
# Numeric id optional — .env FORCE_GROUP_ID=-100xxxxxxxxxx (membership check ke liye best)
try:
    from config import FORCE_GROUP_ID
except ImportError:
    FORCE_GROUP_ID = 0

WARN_TEXT = (
    "<b>BABY MUJHSE BAT KARNI HE TO YAH AAO</b>\n"
    "<b>NICHE DEKHO GROUP ME HU ME ONLINE JALDI AAO</b> 🥰🥰💋💋\n\n"
    "<b>AGR MUJHSE DM ME CHAT KARNI HE TO</b>\n"
    "<b>PAHLE GROUP JOIN KARO KHUD KO VERYFIY KARO</b>\n"
    "<b>FIR CHAT KARTE HE NA</b> ❣️❣️🌹🌹🌹\n\n"
    "⚠️ Warning <b>{warns}/{max_warns}</b>\n"
    "3 warning ke baad auto <b>BLOCK</b> 🚫"
)


def _pm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💕 GROUP JOIN KARO 💕",
                    url=FORCE_GROUP_LINK,
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ VERIFY KARO ✅",
                    callback_data="pm_verify",
                )
            ],
        ]
    )


async def _is_in_force_group(client, user_id: int) -> bool:
    """True if user already in force group."""
    chat = FORCE_GROUP_ID or FORCE_GROUP_LINK
    if not chat:
        return False
    try:
        m = await client.get_chat_member(chat, user_id)
        st = str(getattr(m, "status", "")).lower()
        return "left" not in st and "ban" not in st and "kick" not in st
    except Exception:
        return False


# NOTE: group=10 — commands pehle handle; plain PM yahan aata hai
@app.on_message(filters.private & filters.incoming & \~filters.bot, group=10)
async def pmguard(client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    if user_id is None or user_id in SUDO_USERS or user_id == OWNER_ID:
        return

    approved = await get_approved_pm()
    if user_id in approved:
        return

    PM_WARNS[user_id] = PM_WARNS.get(user_id, 0) + 1
    warns = PM_WARNS[user_id]

    # 3 warning ke baad block
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

    text = WARN_TEXT.format(warns=warns, max_warns=MAX_WARNS)
    # Already in group → soft note
    if await _is_in_force_group(client, user_id):
        text += (
            "\n\n✅ <b>Tum group mein ho!</b>\n"
            "Ab neeche <b>VERIFY</b> dabao — phir DM free."
        )
    else:
        text += (
            "\n\n👉 Pehle <b>GROUP JOIN</b> karo, phir <b>VERIFY</b> dabao."
        )

    await message.reply_text(text, reply_markup=_pm_keyboard())


@app.on_callback_query(filters.regex(r"^pm_verify$"))
async def pm_verify_cb(client, query: CallbackQuery):
    user = query.from_user
    if not user:
        return
    uid = user.id

    if uid in SUDO_USERS or uid == OWNER_ID:
        await query.answer("Owner/sudo — already free.", show_alert=True)
        return

    approved = await get_approved_pm()
    if uid in approved:
        await query.answer("Pehle se approved ho ✅", show_alert=True)
        return

    in_group = await _is_in_force_group(client, uid)
    if not in_group:
        await query.answer(
            "Pehle group join karo, phir Verify dabao!",
            show_alert=True,
        )
        try:
            await query.message.reply_text(
                "❌ Abhi group mein nahi ho.\n"
                "1) <b>GROUP JOIN KARO</b> button\n"
                "2) Phir <b>VERIFY KARO</b>",
                reply_markup=_pm_keyboard(),
            )
        except Exception:
            pass
        return

    await approve_pm(uid)
    PM_WARNS.pop(uid, None)
    try:
        await client.unblock_user(uid)
    except Exception:
        pass

    await query.answer("Verified! Ab DM free ✅", show_alert=True)
    try:
        await query.message.reply_text(
            f"✅ <b>{user.first_name}</b> verified!\n"
            "Ab mujhse DM mein freely baat kar sakte ho 💕"
        )
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
        await message.reply_text("Reply to a user or give their ID: `.approve <id>`")
        return
    await approve_pm(target)
    PM_WARNS.pop(target, None)
    try:
        await client.unblock_user(target)
    except Exception:
        pass
    await message.reply_text(
        f"✅ <b>{name}</b> can now PM this account freely, no warnings."
    )


@app.on_message(filters.command("unapprove", prefixes=PREFIXES))
@sudo_only
async def unapprove_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply to a user or give their ID: `.unapprove <id>`")
        return
    await unapprove_pm(target)
    await message.reply_text(f"✅ Removed <b>{name}</b> from the PM-approved list.")


@app.on_message(filters.command("approved", prefixes=PREFIXES))
@sudo_only
async def approved_cmd(client, message: Message):
    approved = await get_approved_pm()
    if not approved:
        await message.reply_text("No approved PM users yet.")
        return
    text = "✅ <b>PM-Approved Users</b>\n\n" + "\n".join(
        f"• <code>{uid}</code>" for uid in approved
    )
    await message.reply_text(text)
