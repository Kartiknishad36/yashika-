"""
Intel tools — max Telegram detail (premium)
  .msginfo
  .chatinfo / .groupinfo
  .common
  .idtouser / .usertoid
"""
import html
from datetime import datetime, timezone

from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter, ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only


def _esc(s) -> str:
    return html.escape(str(s)) if s is not None else "—"


def _yn(v) -> str:
    return "✅ Yes" if v else "❌ No"


def _link(chat) -> str:
    uname = getattr(chat, "username", None)
    if uname:
        return f"https://t.me/{uname}"
    cid = getattr(chat, "id", 0) or 0
    s = str(cid)
    if s.startswith("-100"):
        return f"https://t.me/c/{s[4:]}/1"
    return f"tg://openmessage?chat_id={cid}"


async def _send_long(message: Message, text: str):
    chunk = 3900
    for i in range(0, len(text), chunk):
        await message.reply_text(text[i : i + chunk], disable_web_page_preview=True)


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
        fwd = "Yes (chat)"
        fwd_detail = f"{_esc(fc.title or fc.id)} (<code>{fc.id}</code>)\n{_link(fc)}"
    elif r.forward_from:
        fu = r.forward_from
        fwd = "Yes (user)"
        fwd_detail = f"{fu.mention} (<code>{fu.id}</code>) @{fu.username or '—'}"
    elif r.forward_sender_name:
        fwd = "Yes (hidden name)"
        fwd_detail = _esc(r.forward_sender_name)
    elif r.forward_date:
        fwd = "Yes"

    media = "text only"
    media_extra = []
    if r.photo:
        media = "photo"
        media_extra.append(f"file_id=<code>{r.photo.file_id[:40]}…</code>")
        media_extra.append(f"size≈{getattr(r.photo, 'file_size', '—')}")
    elif r.video:
        media = "video"
        media_extra.append(f"duration={getattr(r.video, 'duration', '?')}s")
        media_extra.append(f"{getattr(r.video, 'width', '?')}x{getattr(r.video, 'height', '?')}")
    elif r.animation:
        media = "gif/animation"
    elif r.sticker:
        st = r.sticker
        media = "sticker"
        if getattr(st, "is_video", False):
            media = "sticker (video)"
        elif st.is_animated:
            media = "sticker (animated)"
        media_extra.append(f"emoji={st.emoji or '—'}")
        media_extra.append(f"set={getattr(st, 'set_name', None) or '—'}")
    elif r.voice:
        media = f"voice ({getattr(r.voice, 'duration', '?')}s)"
    elif r.video_note:
        media = f"video_note ({getattr(r.video_note, 'duration', '?')}s)"
    elif r.audio:
        media = "audio"
        media_extra.append(f"title={getattr(r.audio, 'title', None) or '—'}")
        media_extra.append(f"performer={getattr(r.audio, 'performer', None) or '—'}")
        media_extra.append(f"duration={getattr(r.audio, 'duration', '?')}s")
    elif r.document:
        media = "document"
        media_extra.append(f"name={getattr(r.document, 'file_name', None) or '—'}")
        media_extra.append(f"mime={getattr(r.document, 'mime_type', None) or '—'}")
        media_extra.append(f"size={getattr(r.document, 'file_size', None) or '—'}")
    elif r.contact:
        media = "contact"
        c = r.contact
        media_extra.append(f"name={c.first_name or ''} {c.last_name or ''}")
        media_extra.append(f"phone={c.phone_number or '—'}")
        media_extra.append(f"user_id={getattr(c, 'user_id', None) or '—'}")
    elif r.location:
        media = "location"
        media_extra.append(f"lat={r.location.latitude} lon={r.location.longitude}")
    elif r.venue:
        media = "venue"
        media_extra.append(f"title={r.venue.title or '—'}")
        media_extra.append(f"address={r.venue.address or '—'}")
    elif r.poll:
        media = "poll"
        media_extra.append(f"q={r.poll.question or '—'}")
        media_extra.append(f"votes={len(r.poll.options or [])}")
    elif r.dice:
        media = f"dice ({r.dice.emoji} = {r.dice.value})"
    elif r.game:
        media = f"game ({getattr(r.game, 'title', '—')})"

    sender = "—"
    if r.from_user:
        u = r.from_user
        sender = (
            f"{u.mention} (<code>{u.id}</code>)\n"
            f"  @{u.username or '—'} · prem={bool(getattr(u, 'is_premium', False))}"
        )
    elif r.sender_chat:
        sc = r.sender_chat
        sender = f"{_esc(sc.title)} (<code>{sc.id}</code>)"

    text_preview = (r.text or r.caption or "")[:200]
    if text_preview:
        text_preview = text_preview.replace("\n", " ")

    entities_n = len(r.entities or []) + len(r.caption_entities or [])
    reactions = getattr(r, "reactions", None)
    react_s = "—"
    if reactions and getattr(reactions, "reactions", None):
        bits = []
        for rx in reactions.reactions[:8]:
            emoji = getattr(getattr(rx, "emoji", None), "emoji", None) or getattr(rx, "emoji", "?")
            bits.append(f"{emoji}×{getattr(rx, 'count', 1)}")
        react_s = " ".join(bits) if bits else "—"

    body = (
        f"╔══ 📋 <b>MESSAGE INFO (FULL)</b> ══╗\n\n"
        f"🆔 Msg ID: <code>{r.id}</code>\n"
        f"💬 Chat ID: <code>{message.chat.id if message.chat else '—'}</code>\n"
        f"📅 Date: <code>{r.date}</code>\n"
        f"✏️ Edited: <b>{'Yes' if r.edit_date else 'No'}</b>"
        f"{f' (<code>{r.edit_date}</code>)' if r.edit_date else ''}\n"
        f"📤 Forward: <b>{fwd}</b>\n"
        f"↪️ Fwd from: {fwd_detail}\n"
        f"👤 Sender: {sender}\n"
        f"📎 Media type: <code>{media}</code>\n"
        + ("\n".join(f"   · {x}" for x in media_extra) + "\n" if media_extra else "")
        + f"🔗 Via bot: {_yn(bool(r.via_bot))}"
        + (f" (@{r.via_bot.username})" if r.via_bot and r.via_bot.username else "") + "\n"
        + f"💬 Reply to msg: <code>{r.reply_to_message_id or '—'}</code>\n"
        + f"🧵 Topic ID: <code>{getattr(r, 'message_thread_id', None) or '—'}</code>\n"
        + f"👁 Views: <code>{getattr(r, 'views', None) or '—'}</code>\n"
        + f"🔁 Forwards count: <code>{getattr(r, 'forwards', None) or '—'}</code>\n"
        + f"🏷 Entities: <code>{entities_n}</code>\n"
        + f"❤️ Reactions: {react_s}\n"
        + f"🔒 Protected: {_yn(bool(getattr(r, 'has_protected_content', False)))}\n"
        + f"📌 Pinned: {_yn(bool(getattr(r, 'pinned', None) or False))}\n"
        + f"📝 Text/caption: <i>{_esc(text_preview) or '—'}</i>\n"
        + f"⏱ Report: <code>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</code>\n"
        + f"╚════════════════════════════╝"
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
    linked_s = f"{_esc(linked.title)} (<code>{linked.id}</code>)" if linked else "—"
    slow = getattr(chat, "slowmode_delay", None)
    protect = getattr(chat, "has_protected_content", None)
    verified = getattr(chat, "is_verified", None)
    scam = getattr(chat, "is_scam", None)
    fake = getattr(chat, "is_fake", None)
    restricted = getattr(chat, "is_restricted", None)
    creator = "—"
    admins = []
    try:
        if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
            async for m in client.get_chat_members(
                chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            ):
                u = m.user
                if not u:
                    continue
                st = str(getattr(m.status, "name", m.status))
                if "OWNER" in st.upper():
                    creator = f"{u.mention} (<code>{u.id}</code>)"
                title_a = getattr(m, "title", None) or ""
                admins.append(
                    f"• {u.mention} <code>{u.id}</code> "
                    f"{('@' + u.username) if u.username else ''} "
                    f"[{st}]" + (f" «{_esc(title_a)}»" if title_a else "")
                )
    except Exception:
        pass

    photo_n = 0
    try:
        async for _ in client.get_chat_photos(chat.id, limit=20):
            photo_n += 1
    except Exception:
        pass

    perms = getattr(chat, "permissions", None)
    perm_lines = []
    if perms:
        for attr in [
            "can_send_messages",
            "can_send_media_messages",
            "can_send_other_messages",
            "can_send_polls",
            "can_add_web_page_previews",
            "can_change_info",
            "can_invite_users",
            "can_pin_messages",
            "can_manage_topics",
        ]:
            if hasattr(perms, attr):
                perm_lines.append(f"  · {attr}: {_yn(getattr(perms, attr))}")

    body = (
        f"╔══ 📊 <b>CHAT INFO (FULL)</b> ══╗\n\n"
        f"🏷 <b>Title:</b> {_esc(title)}\n"
        f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        f"📂 <b>Type:</b> <code>{chat.type}</code>\n"
        f"🔗 <b>Username:</b> @{chat.username or '—'}\n"
        f"👥 <b>Members:</b> <code>{members}</code>\n"
        f"🖼 <b>Chat photos:</b> <code>{photo_n}</code>\n"
        f"📝 <b>About:</b> {_esc(str(desc)[:400])}\n"
        f"👑 <b>Owner:</b> {creator}\n"
        f"📣 <b>Linked:</b> {linked_s}\n"
        f"⏱ <b>Slowmode:</b> <code>{slow if slow is not None else '—'}</code>s\n"
        f"🛡 <b>Protected content:</b> <code>{protect}</code>\n"
        f"✅ Verified: <code>{verified}</code>\n"
        f"⚠️ Scam: <code>{scam}</code> · Fake: <code>{fake}</code>\n"
        f"🔒 Restricted: <code>{restricted}</code>\n"
        f"🌐 <b>Link:</b> {_link(chat)}\n"
        f"\n<b>── Default permissions ──</b>\n"
        + ("\n".join(perm_lines) if perm_lines else "—")
        + f"\n\n<b>── Admins ({len(admins)}) ──</b>\n"
        + ("\n".join(admins[:30]) if admins else "— / hidden")
        + f"\n\n⏱ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        + "\n╚════════════════════════════╝"
    )
    await _send_long(message, body)


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
    n_g = n_c = 0
    try:
        common = await client.get_common_chats(uid)
        for c in common:
            title = _esc(c.title or c.first_name or str(c.id))
            tname = getattr(c.type, "name", str(c.type))
            tag = "📢" if "CHANNEL" in tname else "👥"
            if "CHANNEL" in tname:
                n_c += 1
            else:
                n_g += 1
            lines.append(
                f"{tag} <b>{title}</b>\n"
                f"  <code>{c.id}</code> · type=<code>{tname}</code>\n"
                f"  {_link(c)}"
            )
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return

    body = (
        f"╔══ 👥 <b>COMMON CHATS (FULL)</b> ══╗\n"
        f"Target: <b>{_esc(name)}</b> (<code>{uid}</code>)\n"
        f"Total: <code>{len(lines)}</code> · Groups≈{n_g} · Channels≈{n_c}\n\n"
        + ("\n".join(lines[:60]) if lines else "None / hidden")
        + "\n╚════════════════════════════╝"
    )
    await _send_long(message, body)


@app.on_message(ub_cmd("idtouser", "id2user"))
@sudo_only
async def idtouser_cmd(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].lstrip("-").isdigit():
        await message.reply_text("Usage: <code>.idtouser 123456789</code>")
        return
    try:
        u = await client.get_users(int(parts[1]))
        try:
            common = len(await client.get_common_chats(u.id))
        except Exception:
            common = "?"
        body = (
            f"╔══ 🆔 → 👤 FULL ══╗\n"
            f"{u.mention}\n"
            f"Name: <b>{_esc(u.first_name or '')} {_esc(u.last_name or '')}</b>\n"
            f"ID: <code>{u.id}</code>\n"
            f"User: @{u.username or '—'}\n"
            f"DC: <code>{getattr(u, 'dc_id', '—')}</code>\n"
            f"Premium: {_yn(bool(getattr(u, 'is_premium', False)))}\n"
            f"Verified: {_yn(bool(getattr(u, 'is_verified', False)))}\n"
            f"Bot: {_yn(u.is_bot)} · Deleted: {_yn(getattr(u, 'is_deleted', False))}\n"
            f"Scam: {_yn(getattr(u, 'is_scam', False))} · Fake: {_yn(getattr(u, 'is_fake', False))}\n"
            f"Common chats: <code>{common}</code>\n"
            f"<a href='tg://user?id={u.id}'>Open profile</a>\n"
            f"╚════════════════╝"
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
            f"Name: <b>{_esc(u.first_name or '')} {_esc(u.last_name or '')}</b>\n"
            f"ID: <code>{u.id}</code>\n"
            f"@{u.username or '—'}\n"
            f"Premium: {_yn(bool(getattr(u, 'is_premium', False)))}\n"
            f"DC: <code>{getattr(u, 'dc_id', '—')}</code>\n"
            f"╚════════════╝"
        )
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
