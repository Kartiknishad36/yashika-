"""
.bro — Global Auto-Reply system.

Usage:
  Reply to someone + .bro        → Enable global auto-reply for that user
  .bro off  (or .unbro)          → Disable auto-reply (reply to user or give ID)
  .brolist                       → Show all users with auto-reply enabled

Once enabled, whenever that user sends a message (in any group or DM),
the userbot will automatically reply with:  @Name, <random line>
"""
import random
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import (
    add_bro_target,
    remove_bro_target,
    get_bro_targets,
    is_bro_target,
)

PREFIXES = [".", "!"]

BRO_LINES = [
    "Heyy, kya ho raha hai? Bas tumhe yaad kar raha tha.",
    "Kya kar rahe ho abhi? Batao kuch interesting.",
    "Lagta hai aaj tum bahut busy ho, koi baat nahi… par ek smile dedo.",
    "Socha tumhe text karun… kaise ho?",
    "Aaj ka din kaisa guzar raha hai? Thoda break lo aur mujhe batao.",
    "Kya kar rahe ho? Agar free ho toh thodi der baat karte hain.",
    "Bas yun hi aaya khayal, socha haal-chaal pooch lun.",
    "Miss ho rahe ho… bas itna kehna tha.",
    "Batao, aaj kya naya seekha ya kya acha hua?",
    "Ek number ka sawaal: Kya aaj mujhe reply milega? 😄",
    "Aaj mood kaisa hai? Thoda share karo na.",
    "Tumhara message dekh ke smile aa gayi 😊",
    "Kahan busy ho itne? Thoda time nikal lo na.",
    "Just checking up on you… sab theek hai na?",
    "Aaj kuch special plan hai kya?",
]


def cmd(name):
    return filters.command(name, prefixes=PREFIXES)


# ===================== Enable Auto-Reply =====================
@app.on_message(cmd("bro"))
@sudo_only
async def bro_cmd(client, message: Message):
    # .bro off / .bro stop
    if len(message.command) > 1 and message.command[1].lower() in ("off", "stop", "remove", "del"):
        return await _disable_bro(client, message)

    # Must reply to a user
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text(
            "Kisi user ko **reply** karke `.bro` likho.\n"
            "Uspe Global Auto-Reply lag jayega.\n\n"
            "Hataane ke liye: reply + `.bro off` ya `.unbro`"
        )
        return

    target = message.reply_to_message.from_user
    target_id = target.id

    # Don't allow on self
    me = await client.get_me()
    if target_id == me.id:
        await message.reply_text("Khud pe auto-reply nahi laga sakte 😅")
        return

    await add_bro_target(target_id)

    name = target.first_name or str(target_id)
    await message.reply_text(
        f"✅ Global Auto-Reply **ON** for <a href='tg://user?id={target_id}'>{name}</a>\n"
        f"Ab jab bhi yeh user kahin message karega (group/DM), auto reply jayega."
    )


# ===================== Disable Auto-Reply =====================
@app.on_message(cmd(["unbro", "brooff"]))
@sudo_only
async def unbro_cmd(client, message: Message):
    await _disable_bro(client, message)


async def _disable_bro(client, message: Message):
    target_id = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1 and message.command[-1].isdigit():
        target_id = int(message.command[-1])

    if not target_id:
        await message.reply_text(
            "User ko reply karke `.bro off` / `.unbro` likho,\n"
            "ya ID do: `.unbro 123456789`"
        )
        return

    await remove_bro_target(target_id)
    await message.reply_text(f"✅ Auto-Reply **OFF** for `<code>{target_id}</code>`")


# ===================== List =====================
@app.on_message(cmd("brolist"))
@sudo_only
async def brolist_cmd(client, message: Message):
    targets = await get_bro_targets()
    if not targets:
        await message.reply_text("Koi bhi user auto-reply list mein nahi hai.")
        return

    lines = [f"• <code>{uid}</code>" for uid in targets]
    await message.reply_text(
        "💕 <b>Auto-Reply ON for:</b>\n\n" + "\n".join(lines)
    )


# ===================== Global Auto-Reply Handler =====================
@app.on_message(
    filters.incoming
    & filters.text
    & \~filters.bot
    & \~filters.via_bot
    & \~filters.service,
    group=50,
)
async def bro_auto_reply(client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id

    # Skip if not a target
    if not await is_bro_target(user_id):
        return

    # Don't reply to own messages
    try:
        me = await client.get_me()
        if user_id == me.id:
            return
    except Exception:
        pass

    # Don't reply to commands
    if message.text and message.text.startswith((".", "!")):
        return

    line = random.choice(BRO_LINES)
    user = message.from_user

    # Mention + message
    mention = user.mention if (user.username or user.first_name) else f"<a href='tg://user?id={user.id}'>{user.first_name or 'User'}</a>"
    text = f"{mention}, {line}"

    try:
        await message.reply_text(text)
    except Exception:
        pass
