"""
Broadcast variants (OWNER / sudo only)

Userbot (app):
  .broadcast / .gcast   → saari tracked chats (groups + private jo list mein hain)
  .dmcast               → sirf private / DM chats
  .gcastonly            → alias nahi; .gcast = groups only

Actually per request:
  .dmcast   → sirf DM (private)
  .gcast    → sirf groups
  .broadcast → mixed / all tracked (messages everywhere)

Bot client:
  /broadcast /gcast /dmcast — same logic, prefixes /
"""
import asyncio
import functools

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait
from pyrogram.enums import ChatType

from core.clients import app, bot
from config import OWNER_ID
from database.mongo import get_all_chats, get_sudoers

PREFIX_UB = [".", "!"]
PREFIX_BOT = ["/"]


async def _allowed(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    try:
        if user_id in await get_sudoers():
            return True
    except Exception:
        pass
    try:
        from modules.owner.sudoers import SUDO_USERS
        if user_id in SUDO_USERS:
            return True
    except Exception:
        pass
    return False


def owner_or_sudo(func):
    @functools.wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        if not message.from_user:
            return
        if not await _allowed(message.from_user.id):
            await message.reply_text(
                "❌ Sirf OWNER / sudo is command ko use kar sakte hain."
            )
            return
        return await func(client, message, *args, **kwargs)
    return wrapper


async def _classify_chats(client, chat_ids: list[int]) -> tuple[list[int], list[int]]:
    """Returns (groups, dms). Unknown/fail → skip."""
    groups, dms = [], []
    for cid in chat_ids:
        try:
            chat = await client.get_chat(cid)
            t = chat.type
            if t in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
                groups.append(cid)
            elif t == ChatType.PRIVATE:
                dms.append(cid)
        except Exception:
            # heuristic: negative = group/channel-ish, positive private
            if cid < 0:
                groups.append(cid)
            else:
                dms.append(cid)
    return groups, dms


async def _do_broadcast(client, message: Message, mode: str = "all"):
    """
    mode: all | groups | dms
    """
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text(
            "📢 <b>Broadcast</b>\n"
            "━━━━━━━━━━━━━━\n"
            "<code>.broadcast text</code> — sab tracked chats\n"
            "<code>.gcast text</code> — <b>sirf groups</b>\n"
            "<code>.dmcast text</code> — <b>sirf DMs</b>\n"
            "Ya kisi msg pe <b>reply</b> + command\n"
            "Bot: <code>/broadcast</code> <code>/gcast</code> <code>/dmcast</code>"
        )
        return

    chats = await get_all_chats()
    if not chats:
        await message.reply_text(
            "Koi tracked chat nahi. Pehle groups/DM mein activity chahiye."
        )
        return

    if mode == "groups":
        targets, _ = await _classify_chats(client, chats)
        label = "groups"
    elif mode == "dms":
        _, targets = await _classify_chats(client, chats)
        label = "DMs"
    else:
        targets = list(chats)
        label = "all chats"

    if not targets:
        await message.reply_text(f"Koi {label} target nahi mila.")
        return

    status = await message.reply_text(
        f"📢 Broadcasting to <b>{len(targets)}</b> {label}…"
    )

    text = None
    if not message.reply_to_message:
        text = message.text.split(None, 1)[1]

    sent, failed = 0, 0
    for chat_id in targets:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(chat_id)
            else:
                await client.send_message(chat_id, text)
            sent += 1
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(chat_id)
                else:
                    await client.send_message(chat_id, text)
                sent += 1
            except RPCError:
                failed += 1
        except RPCError:
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.15)

    try:
        await status.edit_text(
            f"📢 <b>Done</b> ({label})\n"
            f"Sent: <b>{sent}</b> | Failed: <b>{failed}</b>"
        )
    except Exception:
        pass


# ---------- USERBOT ----------
@app.on_message(filters.command(["broadcast"], prefixes=PREFIX_UB))
@owner_or_sudo
async def broadcast_all_app(client, message: Message):
    await _do_broadcast(client, message, mode="all")


@app.on_message(filters.command(["gcast"], prefixes=PREFIX_UB))
@owner_or_sudo
async def broadcast_groups_app(client, message: Message):
    await _do_broadcast(client, message, mode="groups")


@app.on_message(filters.command(["dmcast"], prefixes=PREFIX_UB))
@owner_or_sudo
async def broadcast_dms_app(client, message: Message):
    await _do_broadcast(client, message, mode="dms")


# ---------- BOT ----------
if bot is not None:

    @bot.on_message(filters.command(["broadcast"], prefixes=PREFIX_BOT))
    @owner_or_sudo
    async def broadcast_all_bot(client, message: Message):
        await _do_broadcast(client, message, mode="all")

    @bot.on_message(filters.command(["gcast"], prefixes=PREFIX_BOT))
    @owner_or_sudo
    async def broadcast_groups_bot(client, message: Message):
        await _do_broadcast(client, message, mode="groups")

    @bot.on_message(filters.command(["dmcast"], prefixes=PREFIX_BOT))
    @owner_or_sudo
    async def broadcast_dms_bot(client, message: Message):
        await _do_broadcast(client, message, mode="dms")
