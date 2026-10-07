"""
.tagall [msg]  — tag sab members ek-ek
.tag [msg]     — same
.tagadmins / .tagme / .tagallstop
"""
import asyncio
import html

from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError
from pyrogram.enums import ChatMembersFilter

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

TAG_RUNNING: dict[int, bool] = {}


def _mention(u) -> str:
    name = html.escape(u.first_name or "User")
    return '<a href="tg://user?id=' + str(u.id) + '">' + name + '</a>'


@app.on_message(ub_cmd("tagall", "tag"))
@sudo_only
async def tagall_cmd(client, message: Message):
    if message.chat.type.name not in ("GROUP", "SUPERGROUP"):
        await message.reply_text("Sirf group me.")
        return
    chat_id = message.chat.id
    if TAG_RUNNING.get(chat_id):
        await message.reply_text("Pehle se chal raha — <code>.tagallstop</code>")
        return

    parts = (message.text or "").split(None, 1)
    extra = parts[1] if len(parts) > 1 else ""
    TAG_RUNNING[chat_id] = True
    status = await message.reply_text("👥 Tagall start…")
    n = 0
    try:
        async for m in client.get_chat_members(chat_id):
            if not TAG_RUNNING.get(chat_id):
                break
            u = m.user
            if not u or u.is_bot or getattr(u, "is_deleted", False):
                continue
            try:
                text = _mention(u)
                if extra:
                    text = text + "\n" + html.escape(extra)
                await client.send_message(chat_id, text)
                n += 1
                await asyncio.sleep(1.5)
            except FloodWait as e:
                await asyncio.sleep(e.value + 1)
            except RPCError:
                continue
            except Exception:
                continue
        msg = ("🛑 Stopped" if not TAG_RUNNING.get(chat_id) else "✅ Done") + " — tagged <code>" + str(n) + "</code>"
        try:
            await status.edit_text(msg)
        except Exception:
            pass
    except Exception as e:
        await message.reply_text("❌ <code>" + type(e).__name__ + ": " + str(e) + "</code>")
    finally:
        TAG_RUNNING[chat_id] = False


@app.on_message(ub_cmd("tagadmins"))
@sudo_only
async def tagadmins_cmd(client, message: Message):
    if message.chat.type.name not in ("GROUP", "SUPERGROUP"):
        await message.reply_text("Sirf group me.")
        return
    parts = (message.text or "").split(None, 1)
    extra = parts[1] if len(parts) > 1 else ""
    lines = []
    try:
        async for m in client.get_chat_members(
            message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            u = m.user
            if not u or u.is_bot:
                continue
            lines.append(_mention(u))
        if not lines:
            await message.reply_text("No admins found.")
            return
        text = "🛡 <b>Admins</b>\n" + " ".join(lines)
        if extra:
            text = text + "\n" + html.escape(extra)
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text("❌ <code>" + str(e) + "</code>")


@app.on_message(ub_cmd("tagme"))
@sudo_only
async def tagme_cmd(client, message: Message):
    me = await client.get_me()
    await message.reply_text(_mention(me))


@app.on_message(ub_cmd("tagallstop", "tagstop"))
@sudo_only
async def tagstop_cmd(client, message: Message):
    TAG_RUNNING[message.chat.id] = False
    await message.reply_text("🛑 Tagall stop signal.")
