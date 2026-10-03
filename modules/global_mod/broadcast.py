"""
Broadcast (OWNER / sudo only) — pure userbot

  .broadcast [text]   → saari tracked chats (groups + DMs)
  .gcast [text]       → sirf groups / supergroups
  .dmcast [text]      → sirf private DMs

Reply kisi message pe + command → us message ko copy karke bhejo.
Tracked list = storage.json chats (groups auto-track; DM tab add jab koi
private message aaye — main.py tracker).
"""
import asyncio
import functools

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait, PeerIdInvalid, UserIsBlocked, ChatWriteForbidden
from pyrogram.enums import ChatType

from core.clients import app
from config import OWNER_ID
from database.mongo import get_all_chats, get_sudoers

PREFIXES = [".", "!"]


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
            await message.reply_text("❌ Sirf OWNER / sudo use kar sakte hain.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper


async def _classify_chats(client, chat_ids: list) -> tuple:
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
            if isinstance(cid, int) and cid < 0:
                groups.append(cid)
            else:
                dms.append(cid)
    return groups, dms


async def _do_broadcast(client, message: Message, mode: str = "all"):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text(
            "📢 <b>Broadcast</b>\n"
            "━━━━━━━━━━━━━━\n"
            "<code>.broadcast text</code> — sab tracked\n"
            "<code>.gcast text</code> — sirf <b>groups</b>\n"
            "<code>.dmcast text</code> — sirf <b>DMs</b>\n"
            "Ya kisi msg pe <b>reply</b> + command\n\n"
            "Tip: pehle groups/DM me activity chahiye taaki list bane."
        )
        return

    chats = await get_all_chats()
    if not chats:
        await message.reply_text(
            "❌ Koi tracked chat nahi.\n"
            "Pehle kuch groups me message aane do, ya kisi se DM exchange karo."
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
        await message.reply_text(
            f"❌ Koi <b>{label}</b> target nahi.\n"
            f"Total tracked: <code>{len(chats)}</code>"
        )
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
            await asyncio.sleep(min(e.value, 30) + 1)
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(chat_id)
                else:
                    await client.send_message(chat_id, text)
                sent += 1
            except Exception:
                failed += 1
        except (PeerIdInvalid, UserIsBlocked, ChatWriteForbidden, RPCError):
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.2)

    try:
        await status.edit_text(
            f"📢 <b>Done</b> ({label})\n"
            f"✅ Sent: <b>{sent}</b>\n"
            f"❌ Failed: <b>{failed}</b>"
        )
    except Exception:
        pass


@app.on_message(filters.command(["broadcast"], prefixes=PREFIXES))
@owner_or_sudo
async def broadcast_all(client, message: Message):
    await _do_broadcast(client, message, mode="all")


@app.on_message(filters.command(["gcast"], prefixes=PREFIXES))
@owner_or_sudo
async def broadcast_groups(client, message: Message):
    await _do_broadcast(client, message, mode="groups")


@app.on_message(filters.command(["dmcast"], prefixes=PREFIXES))
@owner_or_sudo
async def broadcast_dms(client, message: Message):
    await _do_broadcast(client, message, mode="dms")
