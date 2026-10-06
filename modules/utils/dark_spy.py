"""
.user — full info + groups/channels/DMs + activity (API limits)

Other user: mutual chats + activity (text/sticker/voice/photo/video)
Self: full dialogs breakdown
Report → reply + Saved Messages (links)
"""
import asyncio

from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only


def _status_text(status) -> str:
    if status is None:
        return "hidden / unknown"
    n = type(status).__name__
    if "Online" in n:
        return "online"
    if "Offline" in n:
        was = getattr(status, "was_online", None)
        return f"offline (last_seen={was})" if was else "offline"
    if "Recently" in n:
        return "recently"
    if "LastWeek" in n:
        return "last week"
    if "LastMonth" in n:
        return "last month"
    if "Empty" in n:
        return "long ago / hidden"
    return n


def _chat_link(chat) -> str:
    uname = getattr(chat, "username", None)
    if uname:
        return f"https://t.me/{uname}"
    cid = getattr(chat, "id", 0) or 0
    s = str(cid)
    if s.startswith("-100"):
        return f"https://t.me/c/{s[4:]}/1"
    return f"tg://openmessage?chat_id={cid}"


async def _resolve_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    parts = (message.text or "").split()
    if len(parts) > 1:
        arg = parts[1].lstrip("@")
        try:
            if arg.lstrip("-").isdigit():
                return await client.get_users(int(arg))
            return await client.get_users(arg)
        except Exception:
            return None
    return message.from_user


async def _scan_user_activity(client, chat_id: int, user_id: int, limit: int = 120) -> dict:
    stats = {"text": 0, "sticker": 0, "voice": 0, "photo": 0, "video": 0, "other": 0, "total": 0}
    try:
        async for msg in client.get_chat_history(chat_id, limit=limit):
            if not msg.from_user or msg.from_user.id != user_id:
                continue
            stats["total"] += 1
            if msg.sticker:
                stats["sticker"] += 1
            elif msg.voice or msg.video_note:
                stats["voice"] += 1
            elif msg.photo:
                stats["photo"] += 1
            elif msg.video or msg.animation:
                stats["video"] += 1
            elif msg.text or msg.caption:
                stats["text"] += 1
            else:
                stats["other"] += 1
    except Exception:
        pass
    return stats


async def _self_dialogs_report(client) -> str:
    groups, channels, dms, bots = [], [], [], []
    async for d in client.get_dialogs():
        c = d.chat
        if not c:
            continue
        link = _chat_link(c)
        title = c.title or c.first_name or str(c.id)
        line = f"• {title}\n  {link}"
        t = c.type
        if t in (ChatType.GROUP, ChatType.SUPERGROUP):
            groups.append(line)
        elif t == ChatType.CHANNEL:
            channels.append(line)
        elif t == ChatType.PRIVATE:
            phone = getattr(c, "phone_number", None) or getattr(c, "phone", None) or "—"
            un = f"@{c.username}" if c.username else "—"
            is_bot = bool(getattr(c, "is_bot", False))
            dm_line = (
                f"• {title} | {un} | id=<code>{c.id}</code> | phone=<code>{phone}</code>\n"
                f"  {link}"
            )
            if is_bot:
                bots.append(dm_line)
            else:
                dms.append(dm_line)

    parts = [
        "<b>═══ MY DIALOGS ═══</b>",
        f"Groups: <code>{len(groups)}</code>",
        f"Channels: <code>{len(channels)}</code>",
        f"DMs: <code>{len(dms)}</code>",
        f"Bot DMs: <code>{len(bots)}</code>",
        "",
        f"<b>── Groups ({len(groups)}) ──</b>",
        "\n".join(groups[:40]) or "—",
        "",
        f"<b>── Channels ({len(channels)}) ──</b>",
        "\n".join(channels[:40]) or "—",
        "",
        f"<b>── DMs ({len(dms)}) ──</b>",
        "\n".join(dms[:50]) or "—",
    ]
    if len(groups) > 40 or len(channels) > 40 or len(dms) > 50:
        parts.append("\n<i>(list truncated)</i>")
    parts.append("\n<i>Phone tab dikhe jab contact/privacy allow kare.</i>")
    return "\n".join(parts)


async def _other_user_chats_report(client, u) -> str:
    groups, channels = [], []
    g_n = c_n = 0
    activity_lines = []
    common = []
    try:
        async for ch in client.get_common_chats(u.id):
            common.append(ch)
    except Exception as e:
        return f"Common chats fail: <code>{e}</code>"

    for ch in common:
        link = _chat_link(ch)
        title = ch.title or ch.first_name or str(ch.id)
        line = f"• <b>{title}</b>\n  id=<code>{ch.id}</code>\n  {link}"
        if ch.type == ChatType.CHANNEL:
            channels.append(line)
            c_n += 1
        else:
            groups.append(line)
            g_n += 1

        st = await _scan_user_activity(client, ch.id, u.id, limit=100)
        if st["total"]:
            activity_lines.append(
                f"• <b>{title}</b>\n"
                f"  msgs=<code>{st['total']}</code> "
                f"text=<code>{st['text']}</code> "
                f"sticker=<code>{st['sticker']}</code> "
                f"voice=<code>{st['voice']}</code> "
                f"photo=<code>{st['photo']}</code> "
                f"video=<code>{st['video']}</code>"
            )
        await asyncio.sleep(0.05)

    phone = getattr(u, "phone_number", None) or "— (privacy)"
    parts = [
        "<b>═══ MUTUAL / VISIBLE CHATS ═══</b>",
        "<i>Dusre user ke saare groups/DMs API nahi deta — sirf common.</i>",
        f"Phone: <code>{phone}</code>",
        f"Common groups: <code>{g_n}</code>",
        f"Common channels: <code>{c_n}</code>",
        "",
        "<b>── Groups ──</b>",
        "\n".join(groups[:30]) or "—",
        "",
        "<b>── Channels ──</b>",
        "\n".join(channels[:30]) or "—",
        "",
        "<b>── Activity (recent ~100 msgs / chat) ──</b>",
        "\n".join(activity_lines[:25]) or "No recent msgs found in common chats",
    ]
    return "\n".join(parts)


async def _send_saved_chunks(client, text: str):
    chunk = 3500
    for i in range(0, len(text), chunk):
        try:
            await client.send_message("me", text[i : i + chunk], disable_web_page_preview=False)
        except Exception as e:
            print(f"[user] saved: {e}")
            break
        await asyncio.sleep(0.3)


@app.on_message(ub_cmd("user", "userinfo", "uinfo"))
@sudo_only
async def user_full_cmd(client, message: Message):
    u = await _resolve_user(client, message)
    if not u:
        await message.reply_text("Reply / <code>.user @name</code> / <code>.user id</code>")
        return

    status = await message.reply_text("Full info + chats scan…")

    try:
        u = await client.get_users(u.id)
    except Exception:
        pass

    me = await client.get_me()
    is_self = u.id == me.id

    chat = None
    try:
        chat = await client.get_chat(u.id)
    except Exception:
        pass

    bio = getattr(chat, "bio", None) or getattr(u, "bio", None) or "—"
    status_line = _status_text(getattr(u, "status", None))

    photo_n = 0
    first_photo = None
    try:
        async for p in client.get_chat_photos(u.id, limit=50):
            photo_n += 1
            if first_photo is None:
                first_photo = p.file_id
    except Exception:
        pass

    phone = getattr(u, "phone_number", None) or "—"

    header = (
        f"<b>═══ USER FULL INFO ═══</b>\n\n"
        f"<b>Name:</b> {u.first_name or '—'} {u.last_name or ''}\n"
        f"<b>Username:</b> @{u.username or '—'}\n"
        f"<b>ID:</b> <code>{u.id}</code>\n"
        f"<b>Phone:</b> <code>{phone}</code>\n"
        f"<b>DC:</b> <code>{getattr(u, 'dc_id', '—')}</code>\n"
        f"<b>Status:</b> <code>{status_line}</code>\n"
        f"<b>Bio:</b> {str(bio)[:200]}\n\n"
        f"<b>── Flags ──</b>\n"
        f"Premium: <code>{bool(getattr(u, 'is_premium', False))}</code>\n"
        f"Verified: <code>{bool(getattr(u, 'is_verified', False))}</code>\n"
        f"Bot: <code>{bool(u.is_bot)}</code>\n"
        f"Deleted: <code>{bool(getattr(u, 'is_deleted', False))}</code>\n"
        f"Fake: <code>{bool(getattr(u, 'is_fake', False))}</code>\n"
        f"Scam: <code>{bool(getattr(u, 'is_scam', False))}</code>\n"
        f"Contact: <code>{bool(getattr(u, 'is_contact', False))}</code>\n"
        f"Mutual contact: <code>{bool(getattr(u, 'is_mutual_contact', False))}</code>\n"
        f"Photos: <code>{photo_n}</code>\n"
        f"<a href='tg://user?id={u.id}'>Open profile</a>\n"
    )

    try:
        await status.edit_text(header + "\n⏳ Chats / activity scan…", disable_web_page_preview=True)
    except Exception:
        pass

    if is_self:
        chats_report = await _self_dialogs_report(client)
    else:
        chats_report = await _other_user_chats_report(client, u)

    full = header + "\n" + chats_report

    try:
        short = header + "\n<i>Full list + links → Saved Messages</i>"
        await status.edit_text(short[:4000], disable_web_page_preview=True)
    except Exception:
        pass

    await _send_saved_chunks(client, full)
    try:
        await client.send_message(
            "me",
            f"✅ <b>.user report done</b>\nTarget: <code>{u.id}</code> {u.first_name or ''}",
        )
    except Exception:
        pass

    if first_photo:
        try:
            await client.send_photo("me", first_photo, caption=f"DP — {u.first_name or u.id}")
        except Exception:
            pass
        try:
            await client.send_photo(
                message.chat.id, first_photo, caption=f"DP — {u.first_name or u.id}"
            )
        except Exception:
            pass

    try:
        await message.reply_text("✅ Full report <b>Saved Messages</b> me bhej diya (links ke saath).")
    except Exception:
        pass
