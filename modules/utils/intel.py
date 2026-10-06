"""
Intel tools (premium detail)
  .msginfo          reply required
  .chatinfo / .groupinfo  [id|@]
  .common / .common2      reply|@|id
  .idtouser / .id2user    id
  .usertoid / .user2id    @username
"""
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter, ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only


def _link(chat) -> str:
    uname = getattr(chat, "username", None)
    if uname:
        return f"https://t.me/{uname}"
    cid = getattr(chat, "id", 0) or 0
    s = str(cid)
    if s.startswith("-100"):
        return f"https://t.me/c/{s[4:]}/1"
    return f"tg://openmessage?chat_id={cid}"


@app.on_message(ub_cmd("msginfo", "messageinfo"))
@sudo_only
async def msginfo_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        await message.reply_text("Reply + <code>.msginfo</code>")
        return

    fwd = "No"
    fwd_detail = "—"
    if r.forward_from_chat:
        fc = r.forward_from_chat
        fwd = "Yes"
        fwd_detail = f"{fc.title or fc.id} (<code>{fc.id}</code>)\n{_link(fc)}"
    elif r.forward_from:
        fu = r.forward_from
        fwd = "Yes"
        fwd_detail = f"{fu.mention} (<code>{fu.id}</code>)"
    elif r.forward_sender_name:
        fwd = "Yes (hidden)"
        fwd_detail = r.forward_sender_name
    elif r.forward_date:
        fwd = "Yes"

    media = "text"
    if r.photo:
        media = "photo"
    elif r.video:
        media = "video"
    elif r.animation:
        media = "gif/animation"
    elif r.sticker:
        media = f"sticker ({'animated' if r.sticker.is_animated else 'static'}"
        if getattr(r.sticker, "is_video", False):
            media = "sticker (video)"
        else:
            media += ")"
    elif r.voice:
        media = f"voice ({getattr(r.voice, 'duration', '?')}s)"
    elif r.video_note:
        media = "video_note"
    elif r.audio:
        media = f"audio ({getattr(r.audio, 'title', '') or 'file'})"
    elif r.document:
        media = f"document ({getattr(r.document, 'file_name', '') or 'file'})"
    elif r.contact:
        media = "contact"
    elif r.location or r.venue:
        media = "location"
    elif r.poll:
        media = "poll"
    elif r.dice:
        media = f"dice ({r.dice.emoji})"

    sender = "—"
    if r.from_user:
        sender = f"{r.from_user.mention} (<code>{r.from_user.id}</code>)"
    elif r.sender_chat:
        sender = f"{r.sender_chat.title} (<code>{r.sender_chat.id}</code>)"

    text_preview = (r.text or r.caption or "")[:120]
    if text_preview:
        text_preview = text_preview.replace("\n", " ")

    body = (
        f"╔══ 📋 <b>MSG INFO</b> ══╗\n\n"
        f"🆔 Msg ID: <code>{r.id}</code>\n"
        f"📅 Date: <code>{r.date}</code>\n"
        f"✏️ Edited: <b>{'Yes' if r.edit_date else 'No'}</b>"
        f"{f' (<code>{r.edit_date}</code>)' if r.edit_date else ''}\n"
        f"📤 Forward: <b>{fwd}</b>\n"
        f"↪️ Fwd from: {fwd_detail}\n"
        f"👤 Sender: {sender}\n"
        f"📎 Media: <code>{media}</code>\n"
        f"🔗 Via bot: <code>{bool(r.via_bot)}</code>\n"
        f"💬 Reply to msg: <code>{r.reply_to_message_id or '—'}</code>\n"
        f"👁 Views: <code>{getattr(r, 'views', None) or '—'}</code>\n"
        f"🔁 Forwards count: <code>{getattr(r, 'forwards', None) or '—'}</code>\n"
        f"📝 Text: <i>{text_preview or '—'}</i>\n"
        f"╚════════════════╝"
    )
    await message.reply_text(body, disable_web_page_preview=True)


@app.on_message(ub_cmd("chatinfo", "groupinfo", "chatinfo2", "groupinfo2"))
@sudo_only
async def chatinfo_cmd(client, message: Message):
    parts = (message.text or "").split()
    target = message.chat.id if message.chat else 0
    if len(parts) > 1:
        a = parts[1]
        target = int(a) if a.lstrip("-").isdigit() else a

    try:
        chat = await client.get_chat(target)
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return

    title = chat.title or chat.first_name or "—"
    desc = getattr(chat, "description", None) or getattr(chat, "bio", None) or "—"
    members = getattr(chat, "members_count", None) or "—"
    linked = getattr(chat, "linked_chat", None)
    linked_s = f"{linked.title} (<code>{linked.id}</code>)" if linked else "—"
    slow = getattr(chat, "slowmode_delay", None)
    protect = getattr(chat, "has_protected_content", None)
    verified = getattr(chat, "is_verified", None)
    scam = getattr(chat, "is_scam", None)
    fake = getattr(chat, "is_fake", None)
    restricted = getattr(chat, "is_restricted", None)
    creator = "—"
    try:
        if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
            async for m in client.get_chat_members(
                chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            ):
                if m.status.name == "OWNER" or str(m.status).endswith("OWNER"):
                    u = m.user
                    if u:
                        creator = f"{u.mention} (<code>{u.id}</code>)"
                    break
    except Exception:
        pass

    body = (
        f"╔══ 📊 <b>CHAT INFO</b> ══╗\n\n"
        f"🏷 <b>Title:</b> {title}\n"
        f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        f"📂 <b>Type:</b> <code>{chat.type}</code>\n"
        f"🔗 <b>Username:</b> @{chat.username or '—'}\n"
        f"👥 <b>Members:</b> <code>{members}</code>\n"
        f"📝 <b>About:</b> {str(desc)[:200]}\n"
        f"👑 <b>Owner:</b> {creator}\n"
        f"📣 <b>Linked:</b> {linked_s}\n"
        f"⏱ <b>Slowmode:</b> <code>{slow if slow is not None else '—'}</code>\n"
        f"🛡 <b>Protected content:</b> <code>{protect}</code>\n"
        f"✅ Verified: <code>{verified}</code> · Scam: <code>{scam}</code> · Fake: <code>{fake}</code>\n"
        f"🔒 Restricted: <code>{restricted}</code>\n"
        f"🌐 <b>Link:</b> {_link(chat)}\n"
        f"╚════════════════╝"
    )
    await message.reply_text(body, disable_web_page_preview=True)


@app.on_message(ub_cmd("common", "common2", "mutual"))
@sudo_only
async def common_cmd(client, message: Message):
    uid = None
    name = ""
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        uid, name = u.id, u.first_name or str(u.id)
    else:
        parts = (message.text or "").split()
        if len(parts) > 1:
            arg = parts[1]
            try:
                u = await client.get_users(int(arg) if arg.lstrip("-").isdigit() else arg)
                uid, name = u.id, u.first_name or str(u.id)
            except Exception as e:
                await message.reply_text(f"❌ <code>{e}</code>")
                return
    if not uid:
        await message.reply_text("Reply / <code>.common @user</code>")
        return

    lines = []
    n = 0
    try:
        async for c in client.get_common_chats(uid):
            n += 1
            title = c.title or c.first_name or str(c.id)
            lines.append(
                f"• <b>{title}</b>\n  <code>{c.id}</code> · {_link(c)}"
            )
            if len(lines) >= 30:
                break
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return

    body = (
        f"╔══ 👥 <b>COMMON CHATS</b> ══╗\n"
        f"Target: <b>{name}</b> (<code>{uid}</code>)\n"
        f"Count: <code>{n}</code>\n\n"
        + ("\n".join(lines) if lines else "None / hidden")
        + "\n╚════════════════╝"
    )
    await message.reply_text(body, disable_web_page_preview=True)


@app.on_message(ub_cmd("idtouser", "id2user"))
@sudo_only
async def idtouser_cmd(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].lstrip("-").isdigit():
        await message.reply_text("Usage: <code>.idtouser 123456789</code>")
        return
    try:
        u = await client.get_users(int(parts[1]))
        body = (
            f"╔══ 🆔 → 👤 ══╗\n"
            f"{u.mention}\n"
            f"Name: <b>{u.first_name or ''} {u.last_name or ''}</b>\n"
            f"ID: <code>{u.id}</code>\n"
            f"User: @{u.username or '—'}\n"
            f"Premium: <code>{bool(getattr(u, 'is_premium', False))}</code>\n"
            f"Bot: <code>{u.is_bot}</code>\n"
            f"<a href='tg://user?id={u.id}'>Open</a>\n"
            f"╚════════════╝"
        )
        await message.reply_text(body, disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(ub_cmd("usertoid", "user2id"))
@sudo_only
async def usertoid_cmd(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.reply_text("Usage: <code>.usertoid @username</code>")
        return
    try:
        u = await client.get_users(parts[1])
        await message.reply_text(
            f"╔══ 👤 → 🆔 ══╗\n"
            f"{u.mention}\n"
            f"ID: <code>{u.id}</code>\n"
            f"@{u.username or '—'}\n"
            f"╚════════════╝"
        )
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
