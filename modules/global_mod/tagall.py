"""
.tagall [text] — tag members one by one
.tagallstop — cancel
.tagme — tag yourself
"""
import asyncio

from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

DELAY_BETWEEN_TAGS = 2.0
TAGALL_TASKS: dict[int, asyncio.Task] = {}


async def _tagall_worker(client, chat_id: int, custom_text: str):
    members = []
    try:
        async for member in client.get_chat_members(chat_id):
            u = member.user
            if not u or u.is_bot or getattr(u, "is_deleted", False):
                continue
            members.append(u)
    except RPCError as e:
        try:
            await client.send_message(chat_id, f"Couldn't fetch members: <code>{e}</code>")
        except Exception:
            pass
        return

    if not members:
        try:
            await client.send_message(chat_id, "No taggable members found.")
        except Exception:
            pass
        return

    total = len(members)
    try:
        for user in members:
            name = user.first_name or "User"
            mention = f'<a href="tg://user?id={user.id}">{name}</a>'
            text = f"{mention} {custom_text}" if custom_text else mention
            try:
                await client.send_message(chat_id, text)
            except FloodWait as e:
                await asyncio.sleep(min(int(e.value), 60))
                try:
                    await client.send_message(chat_id, text)
                except Exception:
                    pass
            except RPCError:
                pass
            await asyncio.sleep(DELAY_BETWEEN_TAGS)

        try:
            await client.send_message(chat_id, f"Tagall complete — <b>{total}</b> members.")
        except Exception:
            pass
    except asyncio.CancelledError:
        try:
            await client.send_message(chat_id, "Tagall stopped.")
        except Exception:
            pass
        raise
    finally:
        TAGALL_TASKS.pop(chat_id, None)


@app.on_message(ub_cmd("tagall"))
@sudo_only
async def tagall_cmd(client, message: Message):
    if not message.chat or message.chat.type.name not in ("GROUP", "SUPERGROUP"):
        await message.reply_text("Sirf <b>group</b> me use karo.")
        return

    chat_id = message.chat.id
    if chat_id in TAGALL_TASKS:
        await message.reply_text("Tagall already running. <code>.tagallstop</code>")
        return

    parts = (message.text or "").split(None, 1)
    custom_text = parts[1] if len(parts) > 1 else ""

    await message.reply_text(
        "Tagging everyone user-by-user…\n"
        "Stop: <code>.tagallstop</code>"
    )
    task = asyncio.create_task(_tagall_worker(client, chat_id, custom_text))
    TAGALL_TASKS[chat_id] = task


@app.on_message(ub_cmd("tagallstop"))
@sudo_only
async def tagallstop_cmd(client, message: Message):
    task = TAGALL_TASKS.get(message.chat.id if message.chat else 0)
    if not task:
        await message.reply_text("No tagall running here.")
        return
    task.cancel()
    await message.reply_text("Stopping tagall…")


@app.on_message(ub_cmd("tagme"))
@sudo_only
async def tagme_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return
    await message.reply_text(
        f'<a href="tg://user?id={user.id}">{user.first_name or "You"}</a>'
    )


@app.on_message(ub_cmd("tagadmins"))
@sudo_only
async def tagadmins_cmd(client, message: Message):
    if not message.chat or message.chat.type.name not in ("GROUP", "SUPERGROUP"):
        await message.reply_text("Sirf group me.")
        return
    admins = []
    try:
        async for m in client.get_chat_members(message.chat.id, filter="administrators"):
            u = m.user
            if u and not u.is_bot:
                admins.append(f'<a href="tg://user?id={u.id}">{u.first_name or "Admin"}</a>')
    except Exception as e:
        await message.reply_text(f"Error: <code>{e}</code>")
        return
    if not admins:
        await message.reply_text("No admins found.")
        return
    # batch of 5
    for i in range(0, len(admins), 5):
        chunk = " ".join(admins[i : i + 5])
        try:
            await message.reply_text(chunk)
        except Exception:
            pass
        await asyncio.sleep(1.2)
