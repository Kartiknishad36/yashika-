"""Chat moderation — ban kick mute promote pin"""
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import RPCError
from pyrogram.enums import ChatMemberStatus

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

MUTED = ChatPermissions()
UNMUTED = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
)


def _target_from(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        return u.id, u.first_name or str(u.id)
    parts = (message.text or "").split()
    if len(parts) > 1:
        arg = parts[1]
        if arg.lstrip("-").isdigit():
            return int(arg), arg
    return None, None


@app.on_message(ub_cmd("ban"))
@sudo_only
async def ban_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.ban id</code>")
        return
    try:
        await client.ban_chat_member(message.chat.id, target)
        await message.reply_text(f"Banned <b>{name}</b>.")
    except RPCError as e:
        await message.reply_text(f"Ban fail: <code>{e}</code>")


@app.on_message(ub_cmd("unban"))
@sudo_only
async def unban_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.unban id</code>")
        return
    try:
        await client.unban_chat_member(message.chat.id, target)
        await message.reply_text(f"Unbanned <b>{name}</b>.")
    except RPCError as e:
        await message.reply_text(f"Unban fail: <code>{e}</code>")


@app.on_message(ub_cmd("kick"))
@sudo_only
async def kick_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.kick id</code>")
        return
    try:
        await client.ban_chat_member(message.chat.id, target)
        await client.unban_chat_member(message.chat.id, target)
        await message.reply_text(f"Kicked <b>{name}</b>.")
    except RPCError as e:
        await message.reply_text(f"Kick fail: <code>{e}</code>")


@app.on_message(ub_cmd("mute"))
@sudo_only
async def mute_user_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.mute id</code>")
        return
    try:
        await client.restrict_chat_member(message.chat.id, target, MUTED)
        await message.reply_text(f"Muted <b>{name}</b>.")
    except RPCError as e:
        await message.reply_text(f"Mute fail: <code>{e}</code>")


@app.on_message(ub_cmd("unmute"))
@sudo_only
async def unmute_user_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.unmute id</code>")
        return
    try:
        await client.restrict_chat_member(message.chat.id, target, UNMUTED)
        await message.reply_text(f"Unmuted <b>{name}</b>.")
    except RPCError as e:
        await message.reply_text(f"Unmute fail: <code>{e}</code>")


@app.on_message(ub_cmd("promote"))
@sudo_only
async def promote_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.promote id</code>")
        return
    try:
        await client.promote_chat_member(
            message.chat.id, target,
            can_manage_chat=True, can_delete_messages=True,
            can_restrict_members=True, can_invite_users=True,
        )
        await message.reply_text(f"Promoted <b>{name}</b>.")
    except RPCError as e:
        await message.reply_text(f"Promote fail: <code>{e}</code>")


@app.on_message(ub_cmd("demote"))
@sudo_only
async def demote_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply or <code>.demote id</code>")
        return
    try:
        await client.promote_chat_member(
            message.chat.id, target,
            can_manage_chat=False, can_delete_messages=False,
            can_restrict_members=False, can_invite_users=False,
            can_pin_messages=False, can_promote_members=False,
        )
        await message.reply_text(f"Demoted <b>{name}</b>.")
    except RPCError as e:
        await message.reply_text(f"Demote fail: <code>{e}</code>")


@app.on_message(ub_cmd("pin"))
@sudo_only
async def pin_cmd(client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message + <code>.pin</code>")
        return
    try:
        await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.reply_text("Pinned.")
    except RPCError as e:
        await message.reply_text(f"Pin fail: <code>{e}</code>")


@app.on_message(ub_cmd("unpin"))
@sudo_only
async def unpin_cmd(client, message: Message):
    try:
        if message.reply_to_message:
            await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
        else:
            await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("Unpinned.")
    except RPCError as e:
        await message.reply_text(f"Unpin fail: <code>{e}</code>")


async def _iter_non_admin_members(client, chat_id):
    async for member in client.get_chat_members(chat_id):
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            continue
        if member.user.is_bot or getattr(member.user, "is_self", False):
            continue
        yield member.user.id, member.user.first_name


@app.on_message(ub_cmd("banall"))
@sudo_only
async def banall_cmd(client, message: Message):
    status = await message.reply_text("Banning non-admins…")
    count = 0
    async for uid, _ in _iter_non_admin_members(client, message.chat.id):
        try:
            await client.ban_chat_member(message.chat.id, uid)
            count += 1
        except RPCError:
            continue
    await status.edit_text(f"Banned {count} member(s).")


@app.on_message(ub_cmd("kickall"))
@sudo_only
async def kickall_cmd(client, message: Message):
    status = await message.reply_text("Kicking non-admins…")
    count = 0
    async for uid, _ in _iter_non_admin_members(client, message.chat.id):
        try:
            await client.ban_chat_member(message.chat.id, uid)
            await client.unban_chat_member(message.chat.id, uid)
            count += 1
        except RPCError:
            continue
    await status.edit_text(f"Kicked {count} member(s).")


@app.on_message(ub_cmd("muteall"))
@sudo_only
async def muteall_cmd(client, message: Message):
    status = await message.reply_text("Muting non-admins…")
    count = 0
    async for uid, _ in _iter_non_admin_members(client, message.chat.id):
        try:
            await client.restrict_chat_member(message.chat.id, uid, MUTED)
            count += 1
        except RPCError:
            continue
    await status.edit_text(f"Muted {count} member(s).")


@app.on_message(ub_cmd("unmuteall"))
@sudo_only
async def unmuteall_cmd(client, message: Message):
    status = await message.reply_text("Unmuting non-admins…")
    count = 0
    async for uid, _ in _iter_non_admin_members(client, message.chat.id):
        try:
            await client.restrict_chat_member(message.chat.id, uid, UNMUTED)
            count += 1
        except RPCError:
            continue
    await status.edit_text(f"Unmuted {count} member(s).")
