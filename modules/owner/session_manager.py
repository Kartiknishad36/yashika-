"""Extra userbot sessions from bot /login or .addsession"""
from typing import Dict, Optional

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ParseMode

from config import API_ID, API_HASH
from core.notify import notify_owner
from modules.owner.sudoers import ub_cmd, owner_only
from database.mongo import _read, _write, _lock

EXTRA: Dict[int, Client] = {}
META: Dict[int, dict] = {}


async def _save_session(uid: int, session: str, name: str = "", username: str = ""):
    async with _lock:
        data = _read()
        data.setdefault("sessions", {})
        data["sessions"][str(uid)] = {"session": session, "name": name, "username": username}
        _write(data)


async def _load_all_sessions() -> dict:
    async with _lock:
        data = _read()
        return dict(data.get("sessions") or {})


async def _delete_session(uid: int):
    async with _lock:
        data = _read()
        data.setdefault("sessions", {})
        data["sessions"].pop(str(uid), None)
        _write(data)


def _register_basic_handlers(client: Client, uid: int):
    """Logged-in secondary ID — own outgoing commands."""

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]ping(\s|$)"), group=-10)
    async def _ping(_, message: Message):
        await message.reply_text(f"<b>Pong!</b> session <code>{uid}</code>")

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]alive(\s|$)"), group=-10)
    async def _alive(_, message: Message):
        me = await client.get_me()
        prem = "Yes" if getattr(me, "is_premium", False) else "No"
        await message.reply_text(
            f"<b>ALIVE</b> — {me.first_name}\n"
            f"ID: <code>{me.id}</code>\nPremium: <b>{prem}</b>"
        )

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]id(\s|$)"), group=-10)
    async def _id(_, message: Message):
        chat = message.chat.id if message.chat else 0
        await message.reply_text(f"Chat: <code>{chat}</code>\nMe: <code>{uid}</code>")

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]help(\s|$)"), group=-10)
    async def _help(_, message: Message):
        await message.reply_text(
            f"<b>Session</b> <code>{uid}</code>\n"
            f"<code>.ping</code> <code>.alive</code> <code>.id</code>\n"
            f"<code>.ok</code> <code>.vip</code> <code>.king</code> <code>.yashika</code>\n"
            f"<code>.tagall</code> <code>.info</code>"
        )

    arts = {
        "ok": "OK",
        "vip": "VIP",
        "boss": "BOSS",
        "pro": "PRO",
        "king": "KING",
        "yashika": "YASHIKA",
        "win": "WIN",
        "gg": "GG",
        "hi": "HI",
        "bye": "BYE",
    }
    for name, label in arts.items():
        def _make(n=name, lab=label):
            @client.on_message(
                filters.me & filters.text & filters.regex(rf"^[.!]{n}(\s|$)"),
                group=-9,
            )
            async def _art(_, message: Message, __n=n, __lab=lab):
                await message.reply_text(f"<b>{__lab}</b>\nSession <code>{uid}</code>")
            return _art
        _make()

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]tagall(\s|$)"), group=-9)
    async def _tagall(_, message: Message):
        import asyncio
        import html
        if message.chat.type.name not in ("GROUP", "SUPERGROUP"):
            await message.reply_text("Group only")
            return
        n = 0
        async for m in client.get_chat_members(message.chat.id):
            u = m.user
            if not u or u.is_bot:
                continue
            name = html.escape(u.first_name or "U")
            try:
                await client.send_message(
                    message.chat.id,
                    f'<a href="tg://user?id={u.id}">{name}</a>',
                )
                n += 1
                await asyncio.sleep(1.5)
                if n >= 50:
                    break
            except Exception:
                continue
        await message.reply_text(f"Tagged {n}")

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]info(\s|$)"), group=-9)
    async def _info(_, message: Message):
        target = "me"
        if message.reply_to_message and message.reply_to_message.from_user:
            target = message.reply_to_message.from_user.id
        else:
            parts = (message.text or "").split()
            if len(parts) > 1:
                target = parts[1].lstrip("@")
        try:
            user = await client.get_users(target)
            text = (
                f"<b>INFO</b> (session {uid})\n"
                f"Name: {user.first_name}\n"
                f"ID: <code>{user.id}</code>\n"
                f"User: @{user.username or '—'}\n"
                f"Premium: {bool(getattr(user, 'is_premium', False))}"
            )
            await message.reply_text(text)
        except Exception as e:
            await message.reply_text(f"❌ {e}")


async def start_extra_session(session: str, notify_client: Optional[Client] = None) -> tuple:
    if not session or len(session) < 20:
        return False, "session short"
    client = Client(
        name=f"extra_{abs(hash(session)) % 10**8}",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session,
        in_memory=True,
        parse_mode=ParseMode.HTML,
        workers=2,
        sleep_threshold=120,
    )
    try:
        await client.start()
        me = await client.get_me()
        uid = me.id
        if uid in EXTRA:
            try:
                await EXTRA[uid].stop()
            except Exception:
                pass
        _register_basic_handlers(client, uid)
        EXTRA[uid] = client
        META[uid] = {"name": me.first_name or "", "username": me.username or "", "session": session}
        await _save_session(uid, session, META[uid]["name"], META[uid]["username"])
        print(f"[session] started extra uid={uid}")
        if notify_client:
            try:
                await notify_owner(
                    notify_client,
                    f"<b>EXTRA SESSION ONLINE</b>\n"
                    f"{me.first_name} | @{me.username or '—'}\n"
                    f"ID: <code>{uid}</code>",
                )
            except Exception:
                pass
        return True, uid
    except Exception as e:
        try:
            await client.stop()
        except Exception:
            pass
        return False, f"{type(e).__name__}: {e}"


async def stop_extra_session(uid: int) -> bool:
    c = EXTRA.pop(uid, None)
    META.pop(uid, None)
    if c:
        try:
            await c.stop()
        except Exception:
            pass
    await _delete_session(uid)
    return c is not None


async def count_dialogs(client: Client) -> dict:
    groups = channels = dms = bots = other = 0
    try:
        async for d in client.get_dialogs():
            t = d.chat.type
            if t in (ChatType.GROUP, ChatType.SUPERGROUP):
                groups += 1
            elif t == ChatType.CHANNEL:
                channels += 1
            elif t == ChatType.PRIVATE:
                if getattr(d.chat, "is_bot", False):
                    bots += 1
                else:
                    dms += 1
            else:
                other += 1
    except Exception as e:
        return {"error": str(e)}
    return {
        "groups": groups, "channels": channels, "dms": dms,
        "bots": bots, "other": other,
        "total": groups + channels + dms + bots + other,
    }


async def boot_saved_sessions():
    saved = await _load_all_sessions()
    for uid_s, meta in saved.items():
        sess = (meta or {}).get("session") or ""
        if not sess:
            continue
        ok, res = await start_extra_session(sess)
        print(f"[session] restore {uid_s}: {ok} {res}")


from core.clients import app

if app is not None:

    @app.on_message(ub_cmd("sessions", "sessionlist"))
    @owner_only
    async def sessions_cmd(client, message: Message):
        lines = []
        for uid, meta in META.items():
            online = "🟢" if uid in EXTRA else "🔴"
            un = f"@{meta.get('username')}" if meta.get("username") else "—"
            lines.append(f"{online} <code>{uid}</code> {meta.get('name') or ''} {un}")
        await message.reply_text(
            f"<b>Extra sessions</b> ({len(EXTRA)} online)\n\n"
            + ("\n".join(lines) if lines else "empty")
        )

    @app.on_message(ub_cmd("sessioninfo", "sinfo", "sessionstats"))
    @owner_only
    async def sessioninfo_cmd(client, message: Message):
        parts = (message.text or "").split()
        if len(parts) < 2:
            await message.reply_text(
                "Usage: <code>.sessioninfo id</code>\n"
                f"Online: {', '.join(str(x) for x in EXTRA) or 'none'}"
            )
            return
        try:
            uid = int(parts[1])
        except ValueError:
            await message.reply_text("Invalid id")
            return
        extra = EXTRA.get(uid)
        if not extra:
            await message.reply_text("Session offline.")
            return
        status = await message.reply_text("📊 Scanning…")
        groups, channels, dms = [], [], []
        try:
            async for d in extra.get_dialogs(limit=200):
                c = d.chat
                if not c:
                    continue
                title = getattr(c, "title", None) or (
                    (getattr(c, "first_name", None) or "")
                    + (" " + c.last_name if getattr(c, "last_name", None) else "")
                ) or str(c.id)
                uname = f"@{c.username}" if getattr(c, "username", None) else "—"
                link = f"https://t.me/{c.username}" if getattr(c, "username", None) else f"id:{c.id}"
                line = f"• {title} | {uname} | <code>{c.id}</code> | {link}"
                tname = getattr(c.type, "name", str(c.type)).upper()
                if tname in ("GROUP", "SUPERGROUP"):
                    groups.append(line)
                elif tname == "CHANNEL":
                    channels.append(line)
                elif tname == "PRIVATE":
                    dms.append(line)
        except Exception as e:
            await status.edit_text(f"❌ {type(e).__name__}: {e}")
            return
        meta = META.get(uid) or {}
        header = (
            f"<b>SESSION STATS</b> <code>{uid}</code>\n"
            f"{meta.get('name') or ''} @{meta.get('username') or '—'}\n"
            f"Groups: <code>{len(groups)}</code> · "
            f"Channels: <code>{len(channels)}</code> · "
            f"DMs: <code>{len(dms)}</code>"
        )
        text = "\n".join(
            [header, "\n<b>GROUPS</b>"] + groups[:80]
            + ["\n<b>CHANNELS</b>"] + channels[:40]
            + ["\n<b>DMs</b>"] + dms[:60]
        )
        for i in range(0, len(text), 3500):
            try:
                await notify_owner(client, text[i : i + 3500])
            except Exception:
                await message.reply_text(text[i : i + 4000])
        await status.edit_text(
            f"✅ Log group me bhej diya\n"
            f"G={len(groups)} C={len(channels)} DM={len(dms)}"
        )

    @app.on_message(ub_cmd("sessionstop", "stopsession"))
    @owner_only
    async def sessionstop_cmd(client, message: Message):
        parts = (message.text or "").split()
        if len(parts) < 2:
            await message.reply_text("Usage: <code>.sessionstop id</code>")
            return
        try:
            uid = int(parts[1])
        except ValueError:
            await message.reply_text("Invalid id")
            return
        ok = await stop_extra_session(uid)
        await message.reply_text("Stopped." if ok else "Not running.")
