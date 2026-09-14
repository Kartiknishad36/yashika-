"""
.pin .unpin .invitelink .tagadmins
"""
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


@app.on_message(filters.command("pin", prefixes=PREFIXES) & filters.group)
@sudo_only
async def pin_cmd(client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply karke <code>.pin</code>")
        return
    try:
        await client.pin_chat_message(
            message.chat.id,
            message.reply_to_message.id,
            disable_notification=True,
        )
        await message.reply_text("📌 Pinned (silent)")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command("unpin", prefixes=PREFIXES) & filters.group)
@sudo_only
async def unpin_cmd(client, message: Message):
    try:
        if message.reply_to_message:
            await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
        else:
            await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("📌 Unpinned")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command(["invitelink", "link"], prefixes=PREFIXES) & filters.group)
@sudo_only
async def invitelink_cmd(client, message: Message):
    try:
        chat = await client.get_chat(message.chat.id)
        if chat.username:
            await message.reply_text(f"🔗 https://t.me/{chat.username}")
            return
        link = await client.export_chat_invite_link(message.chat.id)
        await message.reply_text(f"🔗 {link}")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>\nInvite permission chahiye.")


@app.on_message(filters.command("tagadmins", prefixes=PREFIXES) & filters.group)
@sudo_only
async def tagadmins_cmd(client, message: Message):
    mentions = []
    try:
        async for m in client.get_chat_members(
            message.chat.id, filter=filters.ChatMembersFilter.ADMINISTRATORS
            if hasattr(filters, "ChatMembersFilter")
            else None
        ):
            u = m.user
            if u and not u.is_bot:
                mentions.append(u.mention)
    except Exception:
        # fallback
        try:
            from pyrogram.enums import ChatMembersFilter
            async for m in client.get_chat_members(
                message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            ):
                if m.user and not m.user.is_bot:
                    mentions.append(m.user.mention)
        except Exception as e:
            await message.reply_text(f"❌ <code>{e}</code>")
            return
    if not mentions:
        await message.reply_text("No admins found.")
        return
    text = "👮 <b>Admins</b>\n" + " ".join(mentions[:50])
    await message.reply_text(text)
