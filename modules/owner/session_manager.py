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
    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]ping(\s|$)"), group=-10)
    async def _ping(_, message: Message):
        await message.reply_text(f"<b>Pong!</b> session <code>{uid}</code>")

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]alive(\s|$)"), group=-10)
    async def _alive(_, message: Message):
        me = await client.get_me()
        await message.reply_text(f"<b>ALIVE</b> — {me.first_name}\nID: <code>{me.id}</code>")

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]id(\s|$)"), group=-10)
    async def _id(_, message: Message):
        chat = message.chat.id if message.chat else 0
        await message.reply_text(f"Chat: <code>{chat}</code>\nMe: <code>{uid}</code>")

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]help(\s|$)"), group=-10)
    async def _help(_, message: Message):
        await message.reply_text(
            f"<b>Session</b> <code>{uid}</code>\n<code>.ping</code> <code>.alive</code> <code>.id</code>"
        )


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

    @app.on_message(ub_cmd("sessioninfo", "sinfo"))
    @owner_only
    async def sessioninfo_cmd(client, message: Message):
        parts = (message.text or "").split()
        if len(parts) < 2:
            await message.reply_text("Usage: <code>.sessioninfo id</code>")
            return
        try:
            uid = int(parts[1])
        except ValueError:
            await message.reply_text("Invalid id")
            return
        c = EXTRA.get(uid)
        if not c:
            await message.reply_text("Not online")
            return
        counts = await count_dialogs(c)
        meta = META.get(uid) or {}
        await message.reply_text(
            f"<b>SESSION</b> <code>{uid}</code>\n"
            f"{meta.get('name')}\n"
            f"Groups: {counts.get('groups')} DMs: {counts.get('dms')}"
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
