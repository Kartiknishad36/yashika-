"""
Extra userbot sessions (from .login / .addsession)

Each logged account runs as its own Client — own control on that ID.
Owner can inspect: .sessions / .sessioninfo / .sessionstop
"""
import asyncio
from typing import Dict, Optional

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ParseMode

from config import API_ID, API_HASH, OWNER_ID
from modules.owner.sudoers import ub_cmd, sudo_only, owner_only
from database.mongo import _read, _write, _lock

# uid -> Client
EXTRA: Dict[int, Client] = {}
# uid -> meta
META: Dict[int, dict] = {}


async def _save_session(uid: int, session: str, name: str = "", username: str = ""):
    async with _lock:
        data = _read()
        data.setdefault("sessions", {})
        data["sessions"][str(uid)] = {
            "session": session,
            "name": name,
            "username": username,
        }
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
    """Minimal independent control for this account."""

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]ping(\s|$)"), group=-10)
    async def _ping(_, message: Message):
        await message.reply_text(f"<b>Pong!</b> session <code>{uid}</code>")

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]alive(\s|$)"), group=-10)
    async def _alive(_, message: Message):
        me = await client.get_me()
        await message.reply_text(
            f"<b>ALIVE</b> — {me.first_name}\n"
            f"ID: <code>{me.id}</code>\n"
            f"Extra session bot"
        )

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]id(\s|$)"), group=-10)
    async def _id(_, message: Message):
        chat = message.chat.id if message.chat else 0
        await message.reply_text(f"Chat: <code>{chat}</code>\nMe: <code>{uid}</code>")

    @client.on_message(filters.me & filters.text & filters.regex(r"^[.!]help(\s|$)"), group=-10)
    async def _help(_, message: Message):
        await message.reply_text(
            f"<b>Session bot</b> <code>{uid}</code>\n"
            f"<code>.ping</code> <code>.alive</code> <code>.id</code>\n"
            f"Owner: .sessions .sessioninfo"
        )


async def start_extra_session(session: str, notify_client: Optional[Client] = None) -> tuple:
    """Start client from session string. Returns (ok, uid_or_err)."""
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
        # stop old if same uid
        if uid in EXTRA:
            try:
                await EXTRA[uid].stop()
            except Exception:
                pass
        _register_basic_handlers(client, uid)
        EXTRA[uid] = client
        META[uid] = {
            "name": me.first_name or "",
            "username": me.username or "",
            "session": session,
        }
        await _save_session(uid, session, META[uid]["name"], META[uid]["username"])
        print(f"[session] started extra uid={uid} @{me.username}")
        if notify_client:
            try:
                await notify_client.send_message(
                    "me",
                    f"<b>EXTRA SESSION ONLINE</b>\n"
                    f"{me.first_name} | @{me.username or '—'}\n"
                    f"ID: <code>{uid}</code>\n"
                    f"Own control: .ping .alive .help on that account",
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
        "groups": groups,
        "channels": channels,
        "dms": dms,
        "bots": bots,
        "other": other,
        "total": groups + channels + dms + bots + other,
    }


async def boot_saved_sessions():
    """Called from main after app.start — restore saved sessions."""
    saved = await _load_all_sessions()
    for uid_s, meta in saved.items():
        sess = (meta or {}).get("session") or ""
        if not sess:
            continue
        ok, res = await start_extra_session(sess)
        print(f"[session] restore {uid_s}: {ok} {res}")


# ── owner commands on MAIN app ──────────────────────────────────────────────
from core.clients import app


@app.on_message(ub_cmd("sessions", "sessionlist"))
@owner_only
async def sessions_cmd(client, message: Message):
    if not EXTRA and not await _load_all_sessions():
        await message.reply_text("Koi extra session nahi.")
        return
    lines = []
    for uid, meta in META.items():
        online = "🟢" if uid in EXTRA else "🔴"
        un = f"@{meta.get('username')}" if meta.get("username") else "—"
        lines.append(f"{online} <code>{uid}</code> {meta.get('name') or ''} {un}")
    saved = await _load_all_sessions()
    for uid_s, meta in saved.items():
        if int(uid_s) not in META:
            lines.append(f"💾 <code>{uid_s}</code> {meta.get('name') or ''} (saved, offline)")
    await message.reply_text(
        f"<b>Extra sessions</b> ({len(EXTRA)} online)\n\n"
        + ("\n".join(lines) if lines else "empty")
        + "\n\n<code>.sessioninfo id</code> <code>.sessionstop id</code>"
    )


@app.on_message(ub_cmd("sessioninfo", "sinfo"))
@owner_only
async def sessioninfo_cmd(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.reply_text("Usage: <code>.sessioninfo user_id</code>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.reply_text("Invalid id")
        return

    c = EXTRA.get(uid)
    if not c:
        # try start from saved
        saved = await _load_all_sessions()
        meta = saved.get(str(uid))
        if not meta or not meta.get("session"):
            await message.reply_text("Session online nahi / saved nahi.")
            return
        ok, res = await start_extra_session(meta["session"], notify_client=client)
        if not ok:
            await message.reply_text(f"Start fail: <code>{res}</code>")
            return
        c = EXTRA.get(uid)

    status = await message.reply_text("Dialogs count…")
    counts = await count_dialogs(c)
    meta = META.get(uid) or {}
    if counts.get("error"):
        await status.edit_text(f"Error: <code>{counts['error']}</code>")
        return
    await status.edit_text(
        f"<b>SESSION INFO</b>\n"
        f"Name: <b>{meta.get('name') or '—'}</b>\n"
        f"User: @{meta.get('username') or '—'}\n"
        f"ID: <code>{uid}</code>\n\n"
        f"👥 Groups: <code>{counts['groups']}</code>\n"
        f"📢 Channels: <code>{counts['channels']}</code>\n"
        f"💬 DMs: <code>{counts['dms']}</code>\n"
        f"🤖 Bots: <code>{counts['bots']}</code>\n"
        f"📦 Total: <code>{counts['total']}</code>"
    )


@app.on_message(ub_cmd("sessionstop", "stopsession"))
@owner_only
async def sessionstop_cmd(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.reply_text("Usage: <code>.sessionstop user_id</code>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.reply_text("Invalid id")
        return
    ok = await stop_extra_session(uid)
    await message.reply_text("Stopped + removed." if ok else "Not running (saved cleared if any).")


@app.on_message(ub_cmd("sessionstart"))
@owner_only
async def sessionstart_cmd(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.reply_text("Usage: <code>.sessionstart user_id</code>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.reply_text("Invalid id")
        return
    saved = await _load_all_sessions()
    meta = saved.get(str(uid))
    if not meta or not meta.get("session"):
        await message.reply_text("Saved session nahi mili.")
        return
    ok, res = await start_extra_session(meta["session"], notify_client=client)
    await message.reply_text(f"{'OK' if ok else 'FAIL'}: <code>{res}</code>")
