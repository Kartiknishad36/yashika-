"""
Premium Tag

  .tagall [text]     — sab members BATCH me (ek sath groups)
  .tag [text]        — ek-ek user alag message
  .tagallstop / .tagstop
  .tagme
  .tagadmins

Premium account → bade batches (zyada mentions / msg).
"""
import asyncio
import html

from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait
from pyrogram.enums import ChatMembersFilter, ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

TAG_TASKS: dict[int, asyncio.Task] = {}

# non-premium / premium batch sizes (Telegram ~4096 char limit)
BATCH_NORMAL = 5
BATCH_PREMIUM = 10
DELAY_BATCH = 1.5
DELAY_ONE = 1.8


def _mention(u) -> str:
    name = html.escape(u.first_name or "User")
    return f'<a href="tg://user?id={u.id}">{name}</a>'


async def _is_premium(client) -> bool:
    try:
        me = await client.get_me()
        return bool(getattr(me, "is_premium", False))
    except Exception:
        return False


async def _fetch_members(client, chat_id: int) -> list:
    members = []
    try:
        async for member in client.get_chat_members(chat_id):
            u = member.user
            if not u or u.is_bot or getattr(u, "is_deleted", False):
                continue
            members.append(u)
    except RPCError as e:
        await client.send_message(chat_id, f"❌ Members fail: <code>{e}</code>")
        return []
    return members


async def _worker_batch(client, chat_id: int, custom_text: str, batch_size: int):
    members = await _fetch_members(client, chat_id)
    if not members:
        try:
            await client.send_message(chat_id, "No taggable members.")
        except Exception:
            pass
        return

    total = len(members)
    header = custom_text or "👋"
    try:
        await client.send_message(
            chat_id,
            f"╔══ 💎 <b>TAGALL BATCH</b> ══╗\n"
            f"Members: <code>{total}</code> · Batch: <code>{batch_size}</code>\n"
            f"Stop: <code>.tagallstop</code>",
        )
        for i in range(0, total, batch_size):
            chunk = members[i : i + batch_size]
            mentions = " ".join(_mention(u) for u in chunk)
            body = f"{header}\n{mentions}"
            try:
                await client.send_message(chat_id, body)
            except FloodWait as e:
                await asyncio.sleep(min(int(e.value), 90))
                try:
                    await client.send_message(chat_id, body)
                except Exception:
                    pass
            except RPCError:
                pass
            await asyncio.sleep(DELAY_BATCH)

        await client.send_message(
            chat_id,
            f"✅ <b>Tagall complete</b> — <code>{total}</code> members",
        )
    except asyncio.CancelledError:
        try:
            await client.send_message(chat_id, "🛑 Tagall stopped.")
        except Exception:
            pass
        raise
    finally:
        TAG_TASKS.pop(chat_id, None)


async def _worker_one(client, chat_id: int, custom_text: str):
    members = await _fetch_members(client, chat_id)
    if not members:
        try:
            await client.send_message(chat_id, "No taggable members.")
        except Exception:
            pass
        return

    total = len(members)
    try:
        await client.send_message(
            chat_id,
            f"╔══ 👤 <b>TAG ONE-BY-ONE</b> ══╗\n"
            f"Members: <code>{total}</code>\n"
            f"Stop: <code>.tagstop</code>",
        )
        for n, user in enumerate(members, 1):
            text = f"{n}/{total} {_mention(user)}"
            if custom_text:
                text = f"{text}\n{custom_text}"
            try:
                await client.send_message(chat_id, text)
            except FloodWait as e:
                await asyncio.sleep(min(int(e.value), 90))
                try:
                    await client.send_message(chat_id, text)
                except Exception:
                    pass
            except RPCError:
                pass
            await asyncio.sleep(DELAY_ONE)

        await client.send_message(
            chat_id,
            f"✅ <b>Tag done</b> — <code>{total}</code> users",
        )
    except asyncio.CancelledError:
        try:
            await client.send_message(chat_id, "🛑 Tag stopped.")
        except Exception:
            pass
        raise
    finally:
        TAG_TASKS.pop(chat_id, None)


def _is_group(message: Message) -> bool:
    return bool(
        message.chat
        and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
    )


@app.on_message(ub_cmd("tagall"))
@sudo_only
async def tagall_cmd(client, message: Message):
    """Sab members — batch (ek sath groups)."""
    if not _is_group(message):
        await message.reply_text("Sirf <b>group</b> me.")
        return
    chat_id = message.chat.id
    if chat_id in TAG_TASKS:
        await message.reply_text("Already running. <code>.tagallstop</code>")
        return

    parts = (message.text or "").split(None, 1)
    custom = parts[1] if len(parts) > 1 else ""
    premium = await _is_premium(client)
    batch = BATCH_PREMIUM if premium else BATCH_NORMAL

    await message.reply_text(
        f"💎 <b>TAGALL BATCH</b>\n"
        f"Premium: <b>{'Yes' if premium else 'No'}</b> · "
        f"Batch size: <code>{batch}</code>\n"
        f"Stop: <code>.tagallstop</code>"
    )
    task = asyncio.create_task(_worker_batch(client, chat_id, custom, batch))
    TAG_TASKS[chat_id] = task


@app.on_message(ub_cmd("tag"))
@sudo_only
async def tag_one_cmd(client, message: Message):
    """Ek-ek user alag message."""
    if not _is_group(message):
        await message.reply_text("Sirf <b>group</b> me.")
        return
    chat_id = message.chat.id
    if chat_id in TAG_TASKS:
        await message.reply_text("Already running. <code>.tagstop</code>")
        return

    parts = (message.text or "").split(None, 1)
    custom = parts[1] if len(parts) > 1 else ""

    await message.reply_text(
        "👤 <b>TAG one-by-one</b> started\n"
        "Stop: <code>.tagstop</code>"
    )
    task = asyncio.create_task(_worker_one(client, chat_id, custom))
    TAG_TASKS[chat_id] = task


@app.on_message(ub_cmd("tagallstop", "tagstop"))
@sudo_only
async def tagstop_cmd(client, message: Message):
    task = TAG_TASKS.get(message.chat.id if message.chat else 0)
    if not task:
        await message.reply_text("Koi tag running nahi.")
        return
    task.cancel()
    await message.reply_text("🛑 Stopping…")


@app.on_message(ub_cmd("tagme"))
@sudo_only
async def tagme_cmd(client, message: Message):
    user = message.from_user
    if not user:
        me = await client.get_me()
        user = me
    await message.reply_text(
        f"💎 {_mention(user)}\n<code>{user.id}</code>"
    )


@app.on_message(ub_cmd("tagadmins"))
@sudo_only
async def tagadmins_cmd(client, message: Message):
    if not _is_group(message):
        await message.reply_text("Sirf group me.")
        return
    admins = []
    try:
        async for m in client.get_chat_members(
            message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            u = m.user
            if u and not u.is_bot:
                admins.append(_mention(u))
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return
    if not admins:
        await message.reply_text("No admins.")
        return

    premium = await _is_premium(client)
    batch = BATCH_PREMIUM if premium else BATCH_NORMAL
    await message.reply_text(f"🛡 <b>Admins</b> ({len(admins)})")
    for i in range(0, len(admins), batch):
        chunk = " ".join(admins[i : i + batch])
        try:
            await message.reply_text(chunk)
        except Exception:
            pass
        await asyncio.sleep(1.0)
