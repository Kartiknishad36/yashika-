"""
.user / .userinfo / .uinfo
Full identity + groups/channels/DMs + activity → reply + LOG_GROUP
Premium multi-chunk report with links + DP
"""
import asyncio
import html
from datetime import datetime, timezone

from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from core.notify import notify_owner, notify_owner_photo
from modules.owner.sudoers import ub_cmd, sudo_only

DC_MAP = {
    1: "Miami, USA",
    2: "Amsterdam, NL",
    3: "Miami, USA",
    4: "Amsterdam, NL",
    5: "Singapore",
}


def _esc(s) -> str:
    return html.escape(str(s)) if s is not None else "—"


def _yn(v) -> str:
    return "✅" if v else "❌"


def _status_text(status) -> str:
    if status is None:
        return "hidden / unknown"
    n = type(status).__name__
    if "Online" in n:
        return "🟢 online"
    if "Offline" in n:
        was = getattr(status, "was_online", None)
        return f"⚫ offline (last_seen={was})" if was else "⚫ offline"
    if "Recently" in n:
        return "🟡 recently"
    if "LastWeek" in n:
        return "🟠 last week"
    if "LastMonth" in n:
        return "🔴 last month"
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


async def _scan_user_activity(client, chat_id: int, user_id: int, limit: int = 150) -> dict:
    stats = {
        "text": 0, "sticker": 0, "voice": 0, "photo": 0,
        "video": 0, "document": 0, "other": 0, "total": 0,
    }
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
            elif msg.document:
                stats["document"] += 1
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
        title = _esc(c.title or c.first_name or str(c.id))
        t = c.type
        if t in (ChatType.GROUP, ChatType.SUPERGROUP):
            groups.append(f"• <b>{title}</b>\n  id=<code>{c.id}</code>\n  {link}")
        elif t == ChatType.CHANNEL:
            channels.append(f"• <b>{title}</b>\n  id=<code>{c.id}</code>\n  {link}")
        elif t == ChatType.PRIVATE:
            phone = getattr(c, "phone_number", None) or getattr(c, "phone", None) or "—"
            un = f"@{c.username}" if c.username else "—"
            is_bot = bool(getattr(c, "is_bot", False))
            dm_line = (
                f"• <b>{title}</b> | {un}\n"
                f"  id=<code>{c.id}</code> | phone=<code>{_esc(phone)}</code>\n"
                f"  {link}"
            )
            if is_bot:
                bots.append(dm_line)
            else:
                dms.append(dm_line)

    parts = [
        "╔══ 📂 <b>MY DIALOGS FULL</b> ══╗",
        f"Groups: <code>{len(groups)}</code> · Channels: <code>{len(channels)}</code>",
        f"DMs: <code>{len(dms)}</code> · Bots: <code>{len(bots)}</code>",
        "",
        "<b>── Groups ──</b>",
        "\n".join(groups[:80]) or "—",
        "",
        "<b>── Channels ──</b>",
        "\n".join(channels[:80]) or "—",
        "",
        "<b>── DMs (users) ──</b>",
        "\n".join(dms[:100]) or "—",
        "",
        "<b>── Bot DMs ──</b>",
        "\n".join(bots[:40]) or "—",
        "╚════════════════════════╝",
    ]
    return "\n".join(parts)


async def _other_user_chats_report(client, u) -> str:
    groups, channels, activity_lines = [], [], []
    g_n = c_n = 0
    try:
        common = await client.get_common_chats(u.id)
    except Exception as e:
        return f"Common chats fail: <code>{type(e).__name__}: {e}</code>"

    for ch in common:
        link = _chat_link(ch)
        title = _esc(ch.title or ch.first_name or str(ch.id))
        line = f"• <b>{title}</b>\n  id=<code>{ch.id}</code>\n  {link}"
        tname = getattr(ch.type, "name", str(ch.type))
        if "CHANNEL" in tname:
            channels.append(line)
            c_n += 1
        else:
            groups.append(line)
            g_n += 1
        st = await _scan_user_activity(client, ch.id, u.id, limit=120)
        if st["total"]:
            activity_lines.append(
                f"• <b>{title}</b>\n"
                f"  total=<code>{st['total']}</code> "
                f"text=<code>{st['text']}</code> "
                f"sticker=<code>{st['sticker']}</code> "
                f"voice=<code>{st['voice']}</code> "
                f"photo=<code>{st['photo']}</code> "
                f"video=<code>{st['video']}</code> "
                f"doc=<code>{st['document']}</code>"
            )
        await asyncio.sleep(0.04)

    phone = getattr(u, "phone_number", None) or "— (privacy)"
    return "\n".join([
        "╔══  Mutual chats ══╗",
        f"Phone: <code>{_esc(phone)}</code>",
        f"Groups: <code>{g_n}</code> · Channels: <code>{c_n}</code>",
        "",
        "<b>── Groups ──</b>",
        "\n".join(groups[:50]) or "—",
        "",
        "<b>── Channels ──</b>",
        "\n".join(channels[:50]) or "—",
        "",
        "<b>── Activity (recent history scan) ──</b>",
        "\n".join(activity_lines[:40]) or "No recent msgs visible",
        "╚════════════════╝",
    ])


async def _send_log_chunks(client, text: str):
    chunk = 3500
    for i in range(0, len(text), chunk):
        try:
            await notify_owner(client, text[i : i + chunk], disable_web_page_preview=False)
        except TypeError:
            try:
                await notify_owner(client, text[i : i + chunk])
            except Exception as e:
                print(f"[user] log: {e}")
                break
        except Exception as e:
            print(f"[user] log: {e}")
            break
        await asyncio.sleep(0.25)


@app.on_message(ub_cmd("user", "userinfo", "uinfo"))
@sudo_only
async def user_full_cmd(client, message: Message):
    u = await _resolve_user(client, message)
    if not u:
        await message.reply_text(
            "Usage:\n"
            "• Reply + <code>.user</code>\n"
            "• <code>.user @username</code>\n"
            "• <code>.user 123456789</code>"
        )
        return

    status = await message.reply_text("⏳ <b>Full scan</b> identity + chats…")
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
    dc = getattr(u, "dc_id", None)
    dc_loc = DC_MAP.get(dc, "?") if dc else "—"

    photo_n = 0
    first_photo = None
    try:
        async for p in client.get_chat_photos(u.id, limit=100):
            photo_n += 1
            if first_photo is None:
                first_photo = p.file_id
    except Exception:
        pass

    phone = getattr(u, "phone_number", None) or "—"
    full_name = f"{u.first_name or '—'} {u.last_name or ''}".strip()

    header = (
        f"╔════════════════════════════╗\n"
        f"║ 💎 <b>USER FULL REPORT</b> 💎 ║\n"
        f"╚════════════════════════════╝\n\n"
        f"👤 <b>Name:</b> {_esc(full_name)}\n"
        f"🔖 <b>Username:</b> @{u.username or '—'}\n"
        f"🆔 <b>ID:</b> <code>{u.id}</code>\n"
        f"📱 <b>Phone:</b> <code>{_esc(phone)}</code>\n"
        f"🏛 <b>DC:</b> <code>{dc or '—'}</code> ({dc_loc})\n"
        f"📡 <b>Status:</b> {status_line}\n"
        f"📝 <b>Bio:</b> {_esc(str(bio)[:250])}\n\n"
        f"⭐ Premium: {_yn(getattr(u, 'is_premium', False))} · "
        f"✅ Verified: {_yn(getattr(u, 'is_verified', False))}\n"
        f"🤖 Bot: {_yn(u.is_bot)} · 🗑 Deleted: {_yn(getattr(u, 'is_deleted', False))}\n"
        f"🎭 Fake: {_yn(getattr(u, 'is_fake', False))} · ⚠️ Scam: {_yn(getattr(u, 'is_scam', False))}\n"
        f"🖼 Photos: <code>{photo_n}</code>\n"
        f"🔗 <a href='tg://user?id={u.id}'>Open profile</a>\n"
        f"⏱ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
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
        short = header + "\n<i>✅ Full list → Log Group (chunks)</i>"
        await status.edit_text(short[:4000], disable_web_page_preview=True)
    except Exception:
        pass

    await _send_log_chunks(client, full)
    try:
        await notify_owner(
            client,
            f"✅ <b>.user report done</b>\nTarget: <code>{u.id}</code> {_esc(u.first_name or '')}",
        )
    except Exception:
        pass

    if first_photo:
        try:
            await notify_owner_photo(client, first_photo, caption=f"DP — {u.first_name or u.id}")
        except Exception:
            pass
        try:
            await client.send_photo(
                message.chat.id,
                first_photo,
                caption=f"🖼 DP — {_esc(u.first_name or u.id)}",
            )
        except Exception:
            pass

    try:
        await message.reply_text("✅ Full report <b>Log Group</b> me bhej diya (line-by-line links).")
    except Exception:
        pass
