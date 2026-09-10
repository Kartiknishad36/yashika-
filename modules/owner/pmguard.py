from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from core.clients import app
from config import OWNER_ID
from modules.owner.sudoers import SUDO_USERS, sudo_only
from database.mongo import approve_pm, unapprove_pm, get_approved_pm

PREFIXES = [".", "!"]

PM_GUARD_GROUP_LINK = "https://t.me/+POdBgVNQqFkyMTA1"
PM_GUARD_GROUP_ID = -1003064291686

PM_WARNS: dict[int, int] = {}
MAX_WARNS = 2

def get_pm_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💋 𝐉𝐎𝐈𝐍 𝐆𝐑𝐎𝐔𝐏 💋", url=PM_GUARD_GROUP_LINK)],
            [InlineKeyboardButton("💖 𝐕𝐄𝐑𝐈𝐅𝐘 𝐊𝐀𝐑𝐎 💖", callback_data="pm_verify")]
        ]
    )

# Stylish 3D Text
BIG_LINE_1 = "🥰 𝐁𝐀𝐁𝐘 𝐌𝐔𝐉𝐇𝐒𝐄 𝐁𝐀𝐓 𝐊𝐀𝐑𝐍𝐈 𝐇𝐄 𝐓𝐎 𝐘𝐀𝐇 𝐀𝐀𝐎 𝐍𝐈𝐂𝐇𝐄 𝐃𝐄𝐊𝐇𝐎 𝐆𝐑𝐎𝐔𝐏 𝐌𝐄 𝐇𝐔 𝐌𝐄 𝐎𝐍𝐋𝐈𝐍𝐄 𝐉𝐀𝐋𝐃𝐈 𝐀𝐀𝐎 🥰💋💋"
BIG_LINE_2 = "❣️ 𝐀𝐆𝐑 𝐌𝐔𝐉𝐇𝐒𝐄 𝐃𝐌 𝐌𝐄 𝐂𝐇𝐀𝐓 𝐊𝐀𝐑𝐍𝐈 𝐇𝐄 𝐓𝐎 𝐏𝐀𝐇𝐋𝐄 𝐆𝐑𝐎𝐔𝐏 𝐉𝐎𝐈𝐍 𝐊𝐀𝐑𝐎 𝐊𝐇𝐔𝐃 𝐊𝐎 𝐕𝐄𝐑𝐈𝐅𝐘 𝐊𝐀𝐑𝐎 𝐅𝐈𝐑 𝐂𝐇𝐀𝐓 𝐊𝐀𝐑𝐓𝐄 𝐇𝐄 𝐍𝐀 🌹🌹❣️"

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

    if warns >= MAX_WARNS:
        await message.reply_text(
            f"{BIG_LINE_1}\n\n{BIG_LINE_2}\n\n🚫 𝐖𝐚𝐫𝐧𝐢𝐧𝐠 {warns}/{MAX_WARNS}",
            reply_markup=get_pm_buttons()
        )
        try:
            await client.block_user(user_id)
        except Exception:
            pass
        return

    try:
        member = await client.get_chat_member(PM_GUARD_GROUP_ID, user_id)
        is_in_group = member.status not in ["left", "kicked", "banned"]
    except Exception:
        is_in_group = False

    if is_in_group:
        text = (
            f"{BIG_LINE_1}\n\n"
            f"✅ 𝐓𝐮𝐦 𝐆𝐫𝐨𝐮𝐩 𝐌𝐞 𝐇𝐨, 𝐁𝐚𝐬 𝐕𝐞𝐫𝐢𝐟𝐲 𝐊𝐚𝐫𝐨 𝐁𝐚𝐛𝐲 🥰\n\n"
            f"{BIG_LINE_2}\n\n"
            f"⚠️ 𝐖𝐚𝐫𝐧𝐢𝐧𝐠 {warns}/{MAX_WARNS}"
        )
    else:
        text = (
            f"{BIG_LINE_1}\n\n"
            f"{BIG_LINE_2}\n\n"
            f"⚠️ 𝐖𝐚𝐫𝐧𝐢𝐧𝐠 {warns}/{MAX_WARNS}"
        )

    await message.reply_text(text, reply_markup=get_pm_buttons())

@app.on_callback_query(filters.regex("pm_verify"))
async def pm_verify_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    try:
        member = await client.get_chat_member(PM_GUARD_GROUP_ID, user_id)
        is_in_group = member.status not in ["left", "kicked", "banned"]
    except Exception:
        await query.answer("Bot group me admin nahi hai!", show_alert=True)
        return

    if not is_in_group:
        await query.answer("❌ 𝐏𝐚𝐡𝐥𝐞 𝐆𝐫𝐨𝐮𝐩 𝐉𝐨𝐢𝐧 𝐊𝐚𝐫𝐨 𝐁𝐚𝐛𝐲 😘", show_alert=True)
        return

    await approve_pm(user_id)
    PM_WARNS.pop(user_id, None)
    try:
        await client.unblock_user(user_id)
    except Exception:
        pass

    await query.message.edit_text(
        f"💋 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃 💋\n\n🥰 𝐀𝐛 𝐭𝐮𝐦 𝐃𝐌 𝐦𝐞 𝐜𝐡𝐚𝐭 𝐤𝐚𝐫 𝐬𝐚𝐤𝐭𝐞 𝐡𝐨 𝐁𝐚𝐛𝐲, 𝐣𝐚𝐥𝐝𝐢 𝐚𝐚𝐨 🌹"
    )
    await query.answer("✅ Verified Baby! Ab DM karo 💋", show_alert=True)

def _target_from(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name
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
    await message.reply_text(f"✅ <b>{name}</b> can now PM freely.")

@app.on_message(filters.command("unapprove", prefixes=PREFIXES))
@sudo_only
async def unapprove_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply to a user or give their ID: `.unapprove <id>`")
        return
    await unapprove_pm(target)
    await message.reply_text(f"✅ Removed <b>{name}</b> from approved.")

@app.on_message(filters.command("approved", prefixes=PREFIXES))
@sudo_only
async def approved_cmd(client, message: Message):
    approved = await get_approved_pm()
    if not approved:
        await message.reply_text("No approved PM users yet.")
        return
    text = "✅ <b>PM-Approved Users</b>\n\n" + "\n".join(f"• <code>{uid}</code>" for uid in approved)
    await message.reply_text(text)
