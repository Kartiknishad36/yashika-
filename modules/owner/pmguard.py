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

WARN_TEXT = (
    "<b>BABY MUJHSE BAT KARNI HE TO YAH AAO</b>\n"
    "<b>NICHE DEKHO GROUP ME HU ME ONLINE JALDI AAO</b> 🥰🥰💋💋\n\n"
    "<b>AGR MUJHSE DM ME CHAT KARNI HE TO</b>\n"
    "<b>PAHLE GROUP JOIN KARO KHUD KO VERIFY KARO</b>\n"
    "<b>FIR CHAT KARTE HE NA</b> ❣️❣️🌹🌹🌹\n\n"
    "🔗 Group: <a href=\"{link}\">JOIN GROUP</a>\n\n"
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


async def _is_in_force_group(client, user_id: int) -> bool:
    chat = FORCE_GROUP_ID or FORCE_GROUP_LINK
    if not chat:
        return False
    try:
        m = await client.get_chat_member(chat, user_id)
        st = str(getattr(m, "status", "")).lower()
        return "left" not in st and "ban" not in st and "kick" not in st
    except Exception:
        return False


@app.on_message(filters.private & filters.incoming & \~filters.bot, group=10)
async def pmguard(client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    if user_id is None or user_id in SUDO_USERS or user_id == OWNER_ID:
        return

    # verify command alag handler mein
    text0 = (message.text or "").strip().lower()
    if text0 in (".verify", "/verify", "!verify"):
        return

    approved = await get_approved_pm()
    if user_id in approved:
        return

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
            "\n\n👉 Pehle <a href=\"{0}\">GROUP JOIN</a> karo, "
            "phir <code>.verify</code> bhejo."
        ).format(FORCE_GROUP_LINK)

    # Userbot: text + link (buttons user account pe hide ho sakte hain)
    await message.reply_text(text, disable_web_page_preview=True)

    # Optional: agar BOT user ko message kar sake (user ne /start kiya ho)
    if bot is not None:
        try:
            await bot.send_message(
                user_id,
                text,
                reply_markup=_pm_keyboard(),
                disable_web_page_preview=True,
            )
        except Exception:
            pass  # user ne bot start nahi kiya


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

    if not await _is_in_force_group(client, uid):
        await message.reply_text(
            f"❌ Pehle group join karo:\n{FORCE_GROUP_LINK}\n\n"
            "Phir dubara <code>.verify</code> bhejo.",
            disable_web_page_preview=False,
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
        "Ab freely baat kar sakte ho 💕"
    )


@app.on_callback_query(filters.regex(r"^pm_verify$"))
async def pm_verify_cb(client, query: CallbackQuery):
    # Bot message pe button dabaya ho toh
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
    await query.answer("Verified ✅", show_alert=True)
    try:
        await query.message.reply_text("✅ Verified! Ab DM free 💕")
    except Exception:
        pass


# ... baaki approve / unapprove / approved same rakho ...
