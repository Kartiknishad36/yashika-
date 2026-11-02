"""
.tagall [msg]     — sab members (batch mention + message)
.tag [msg]        — same
.tagadmins [msg]  — sirf admins
.tagme            — khud ka mention
.tagallstop / .tagstop
"""
import asyncio
import html

from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError, ChatAdminRequired
from pyrogram.enums import ChatMembersFilter, ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

# chat_id -> running flag
TAG_RUNNING: dict[int, bool] = {}

# Kitne mentions ek message me (Telegram ~ visible mentions limit ~1–10000000 safe)
BATCH_SIZE = 999999
# Messages ke beech delay (flood se bachne ke liye)
DELAY = 1.5


def _mention(u) -> str:
    name = html.escape((u.first_name or "User").strip() or "User")
    return f'<a href="tg://user?id={u.id}">{name}</a>'


def _is_group(message: Message) -> bool:
    return bool(
        message.chat
        and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
    )


async def _collect_members(client, chat_id: int, admins_only: bool = False) -> list:
    """
    Saare members lao.
    Problem fix:
    - Default RECENT filter ~999999999 members deta hai → SEARCH + full iterate
    - Bots / deleted skip
    """
    seen: set[int] = set()
    users = []

    filters_to_try = []
    if admins_only:
        filters_to_try = [ChatMembersFilter.ADMINISTRATORS]
    else:
        # SEARCH se full list; RECENT sirf ~50 deta hai (purani problem)
        filters_to_try = [
            ChatMembersFilter.SEARCH,
            ChatMembersFilter.RECENT,
        ]

    for f in filters_to_try:
        try:
            kwargs = {"chat_id": chat_id, "filter": f}
            # SEARCH ke saath empty query = broadly all (client pe depend)
            if f == ChatMembersFilter.SEARCH:
                kwargs["query"] = ""
            async for m in client.get_chat_members(**kwargs):
                u = m.user
                if not u or u.id in seen:
                    continue
                if u.is_bot or getattr(u, "is_deleted", False):
                    continue
                seen.add(u.id)
                users.append(u)
        except ChatAdminRequired:
            # Non-admin: jo mil sake utna
            continue
        except Exception:
            continue

    # Fallback: filter ke bina (kuch clients me full list)
    if not users and not admins_only:
        try:
            async for m in client.get_chat_members(chat_id):
                u = m.user
                if not u or u.id in seen:
                    continue
                if u.is_bot or getattr(u, "is_deleted", False):
                    continue
                seen.add(u.id)
                users.append(u)
        except Exception:
            pass

    return users


async def _send_batches(client, chat_id: int, users: list, extra: str, status: Message):
    """Message + multiple mentions per batch — message har batch me dikhe."""
    n = 0
    total = len(users)
    batch = []

    async def flush():
        nonlocal n, batch
        if not batch:
            return
        # Pehle custom message, phir mentions — dono dikhenge
        if extra:
            body = html.escape(extra) + "\n\n" + " ".join(batch)
        else:
            body = " ".join(batch)
        try:
            await client.send_message(chat_id, body)
            n += len(batch)
        except FloodWait as e:
            await asyncio.sleep(min(int(e.value) + 1, 90))
            try:
                await client.send_message(chat_id, body)
                n += len(batch)
            except Exception:
                pass
        except RPCError:
            pass
        except Exception:
            pass
        batch = []
        try:
            await status.edit_text(
                f"👥 Tagall… <code>{n}/{total}</code>\n"
                f"Stop: <code>.tagallstop</code>"
            )
        except Exception:
            pass
        await asyncio.sleep(DELAY)

    for u in users:
        if not TAG_RUNNING.get(chat_id):
            break
        batch.append(_mention(u))
     
... 
