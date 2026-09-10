from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from core.clients import app
from config import OWNER_ID
from modules.owner.sudoers import SUDO_USERS, sudo_only
from database.mongo import approve_pm, unapprove_pm, get_approved_pm

PREFIXES = [".", "!"]

# user_id -> warning count
PM_WARNS: dict[int, int] = {}
MAX_WARNS = 3

PM_GUARD_GROUP_LINK = "https://t.me/+POdBgVNQqFkyMTA1"

# NOTE: group=10 (a late group) is deliberate — command handlers (.login,
# .ping, etc, all registered in the default group 0) get first chance at
# any private message. Only messages that don't match ANY command (i.e.
# plain PM chatter, not part of a recognized flow) fall through to here.
# This also means the .login phone/OTP flow's plain-text replies are safe:
# login_flow_capture (group=-10) intercepts those earlier and stops
# propagation itself when a login is in progress, so pmguard never sees them.
@app.on_message(filters.private & filters.incoming & ~filters.bot, group=10)
async def pmguard(client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    if user_id is None or user_id in SUDO_USERS or user_id == OWNER_ID:
        return

    approved = await get_approved_pm()
    if user_id in approved:
        return

    PM_WARNS[user_id] = PM_WARNS.get(user_id, 0) + 1
    warns = PM_WARNS[user_id]

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💋 GROUP JOIN KARO 💋", url=PM_GUARD_GROUP_LINK)],
            [InlineKeyboardButton("✅ VERIFY KARO ✅", callback_data=f"pm_verify_{user_id}")]
        ]
    )

    if warns >= MAX_WARNS:
        await message.reply_text(
            f"🚫 You've been blocked from messaging this account after repeated warnings.\n\n"
            f"🥰 𝐁𝐀𝐁𝐘 𝐌𝐔𝐉𝐇𝐒𝐄 𝐁𝐀𝐓 𝐊𝐀𝐑𝐍𝐈 𝐇𝐄 𝐓𝐎 𝐘𝐀𝐇 𝐀𝐀𝐎 𝐍𝐈𝐂𝐇𝐄 𝐃𝐄𝐊𝐇𝐎 𝐆𝐑𝐎𝐔𝐏 𝐌𝐄 𝐇𝐔 𝐌𝐄 𝐎𝐍𝐋𝐈𝐍𝐄 𝐉𝐀𝐋𝐃𝐈 𝐀𝐀𝐎 🥰🥰💋💋\n\n"                       
            f"❣️ 𝐀𝐆𝐑 𝐌𝐔𝐉𝐇𝐒𝐄 𝐃𝐌 𝐌𝐄 𝐂𝐇𝐀𝐓 𝐊𝐀𝐑𝐍𝐈 𝐇𝐄 𝐓𝐎 𝐏𝐀𝐇𝐋𝐄 𝐆𝐑𝐎𝐔𝐏 𝐉𝐎𝐈𝐍 𝐊𝐀𝐑𝐎 𝐊𝐇𝐔𝐃 𝐊𝐎 𝐕𝐄𝐑𝐘𝐅𝐈𝐘 𝐊𝐀𝐑𝐎 𝐅𝐈𝐑 𝐂𝐇𝐀𝐓 𝐊𝐀𝐑𝐓𝐄 𝐇𝐄 𝐍𝐀 ❣️❣️🌹🌹🌹",
            f"🔗 𝙈𝙔 𝙂𝙍𝙊𝙐𝙋} https://t.me/+POdBgVNQqFkyMTA1",
            reply_markup=buttons
        )
        try:
            await client.block_user(user_id)
        except Exception:
            pass
        return

    await message.reply_text(
        f"👋 This is a personal userbot account, not a support bot.\n"
        f"Warning {warns}/{MAX_WARNS} — further messages may result in a block.\n\n"
        f"🥰 𝐁𝐀𝐁𝐘 𝐌𝐔𝐉𝐇𝐒𝐄 𝐁𝐀𝐓 𝐊𝐀𝐑𝐍𝐈 𝐇𝐄 𝐓𝐎 𝐘𝐀𝐇 𝐀𝐀𝐎 𝐍𝐈𝐂𝐇𝐄 𝐃𝐄𝐊𝐇𝐎 𝐆𝐑𝐎𝐔𝐏 𝐌𝐄 𝐇𝐔 𝐌𝐄 𝐎𝐍𝐋𝐈𝐍𝐄 𝐉𝐀𝐋𝐃𝐈 𝐀𝐀𝐎 🥰🥰💋💋\n\n"
        f"❣️ 𝐀𝐆𝐑 𝐌𝐔𝐉𝐇𝐒𝐄 𝐃𝐌 𝐌𝐄 𝐂𝐇𝐀𝐓 𝐊𝐀𝐑𝐍𝐈 𝐇𝐄 𝐓𝐎 𝐏𝐀𝐇𝐋𝐄 𝐆𝐑𝐎𝐔𝐏 𝐉𝐎𝐈𝐍 𝐊𝐀𝐑𝐎 𝐊𝐇𝐔𝐃 𝐊𝐎 𝐕𝐄𝐑𝐘𝐅𝐈𝐘 𝐊𝐀𝐑𝐎 𝐅𝐈𝐑 𝐂𝐇𝐀𝐓 𝐊𝐀𝐑𝐓𝐄 𝐇𝐄 𝐍𝐀 ❣️❣️🌹🌹🌹", 
        f"🔗 𝙈𝙔 𝙂𝙍𝙊𝙐𝙋} https://t.me/+POdBgVNQqFkyMTA1",
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex(r"^pm_verify_"))
async def pm_verify_cb(client, query: CallbackQuery):
    try:
        target_id = int(query.data.split("_")[-1])
    except:
        target_id = query.from_user.id

    if query.from_user.id != target_id:
        await query.answer("Ye button tumhare liye nahi hai!", show_alert=True)
        return

    await approve_pm(target_id)
    PM_WARNS.pop(target_id, None)
    try:
        await client.unblock_user(target_id)
    except Exception:
        pass

    await query.message.edit_text(
        "✅ 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃 𝐁𝐀𝐁𝐘 🥰\n\nAb tum DM me chat kar sakte ho, auto-approve ho gaye ho 💋🌹"
    )
    await query.answer("✅ Verified!", show_alert=True)

def _target_from(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name
   
