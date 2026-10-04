"""Broadcast — OWNER / sudo"""
import asyncio

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait, PeerIdInvalid, UserIsBlocked, ChatWriteForbidden
from pyrogram.enums import ChatType

from core.clients import app
from config import OWNER_ID
from database.mongo import get_all_chats, get_sudoers
from modules.owner.sudoers import ub_cmd, SUDO_USERS


async def _allowed(user_id: int) -> bool:
    if OWNER_ID and user_id == OWNER_ID:
        return True
    if user_id in SUDO_USERS:
        return True
    try:
        if user_id in await get_sudoers():
            return True
    except Exception:
        pass
    return False


async def _classify_chats(client, chat_ids: list):
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
    parts = (message.text or "").split(None, 1)
    if not message.reply_to_message and len(parts) < 2:
        await message.reply_text(
            "<b>Broadcast</b>\n"
            "<code>.broadcast text</code> — sab\n"
            "<code>.gcast text</code> — groups\n"
            "<code>.dmcast text</code> — DMs\n"
            "Ya reply + command"
        )
        return
    chats = await get_all_chats()
    if not chats:
        await message.reply_text("Koi tracked chat nahi.")
        return
    if mode == "groups":
        targets, _ = await _classify_chats(client, chats)
        label = "groups"
    elif mode == "dms":
        _, targets = await _classify_chats(client, chats)
        label = "DMs"
    else:
        targets = list(chats)
        label = "all"
    if not targets:
        await message.reply_text(f"Koi {label} target nahi.")
        return
    status = await message.reply_text(f"Broadcasting to <b>{len(targets)}</b> {label}…")
    text = None if message.reply_to_message else parts[1]
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
        await asyncio.sleep(0.25)
    try:
        await status.edit_text(
            f"<b>Done</b> ({label})\nSent: <b>{sent}</b> · Failed: <b>{failed}</b>"
        )
    except Exception:
        pass


@app.on_message(ub_cmd("broadcast") & filters.me)
async def broadcast_all(client, message: Message):
    uid = message.from_user.id if message.from_user else 0
    if not await _allowed(uid):
        return
    await _do_broadcast(client, message, mode="all")


@app.on_message(ub_cmd("gcast") & filters.me)
async def broadcast_groups(client, message: Message):
    uid = message.from_user.id if message.from_user else 0
    if not await _allowed(uid):
        return
    await _do_broadcast(client, message, mode="groups")


@app.on_message(ub_cmd("dmcast") & filters.me)
async def broadcast_dms(client, message: Message):
    uid = message.from_user.id if message.from_user else 0
    if not await _allowed(uid):
        return
    await _do_broadcast(client, message, mode="dms")
