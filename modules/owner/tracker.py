"""
Online Tracker — detailed status + profile changes

  .track on|off
  .trackadd <id|@user|reply>
  .trackdel <id|@user|reply>
  .tracklist
  .trackinfo <id|reply>   ← full detail

Alerts → LOG_GROUP only
"""
import time
from datetime import datetime, timezone

from pyrogram import raw
from pyrogram.types import Message
from pyrogram.handlers import RawUpdateHandler

from core.clients import app
from core.notify import notify_owner
from modules.owner.sudoers import sudo_only, ub_cmd
from database.mongo import get_feature, set_feature, _read, _write, _lock

_LAST_STATUS: dict[int, str] = {}
_USER_CACHE: dict[int, dict] = {}
_HISTORY: dict[int, list] = {}

DC_MAP = {1: "Miami US", 2: "Amsterdam NL", 3: "Miami US", 4: "Amsterdam NL", 5: "Singapore"}


def _fmt_ts(ts) -> str:
    if not ts:
        return "—"
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return str(ts)


def _status_detail(status) -> tuple:
    if status is None:
        return "unknown", "status=None"
    n = type(status).__name__
    if "UserStatusOnline" in n or n == "UserStatusOnline":
        exp = getattr(status, "expires", None)
        return "online", f"expires={_fmt_ts(exp)}"
    if "UserStatusOffline" in n or n == "UserStatusOffline":
        was = getattr(status, "was_online", None)
        return "offline", f"last_seen={_fmt_ts(was)}"
    if "Recently" in n:
        return "recently", "last seen: recently"
    if "LastWeek" in n:
        return "last_week", "last seen: within a week"
    if "LastMonth" in n:
        return "last_month", "last seen: within a month"
    if "Empty" in n:
        return "long_ago", "last seen: long ago / hidden"
    return n, n


def _push_hist(uid: int, event: str):
    _HISTORY.setdefault(uid, [])
    _HISTORY[uid].append(f"{time.strftime('%H:%M:%S')} {event}")
    _HISTORY[uid] = _HISTORY[uid][-30:]


async def _track_list() -> list:
    async with _lock:
        data = _read()
        data.setdefault("track_users", [])
        return [int(x) for x in data["track_users"]]


async def _track_add(uid: int):
    async with _lock:
        data = _read()
        data.setdefault("track_users", [])
        if uid not in data["track_users"]:
            data["track_users"].append(uid)
            _write(data)


async def _track_del(uid: int):
    async with _lock:
        data = _read()
        data.setdefault("track_users", [])
        data["track_users"] = [x for x in data["track_users"] if int(x) != int(uid)]
        _write(data)


async def _notify(client, text: str):
    await notify_owner(client, text)


def _target(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        return u.id, u.first_name or str(u.id)
    parts = (message.text or "").split()
    if len(parts) > 1:
        arg = parts[1].strip()
        if arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit()):
            return int(arg), arg
        return arg, arg
    return None, None


async def _resolve_uid(client, raw_target):
    if raw_target is None:
        return None, None
    if isinstance(raw_target, int):
        try:
            u = await client.get_users(raw_target)
            return u.id, u.first_name or str(u.id)
        except Exception:
            return raw_target, str(raw_target)
    try:
        chat = await client.get_chat(raw_target)
        uid = chat.id
        name = getattr(chat, "first_name", None) or getattr(chat, "title", None) or str(uid)
        return uid, name
    except Exception:
        return None, None


async def _cache_user(client, uid: int):
    try:
        u = await client.get_users(uid)
        _USER_CACHE[uid] = {
            "name": u.first_name or "",
            "last_name": u.last_name or "",
            "username": u.username or "",
            "premium": bool(getattr(u, "is_premium", False)),
            "dc": getattr(u, "dc_id", None),
        }
        return _USER_CACHE[uid]
    except Exception:
        return _USER_CACHE.get(uid) or {}


@app.on_message(ub_cmd("track"))
@sudo_only
async def track_toggle(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        on = await get_feature("tracker", False)
        n = len(await _track_list())
        await message.reply_text(
            f"╔══ 👁 <b>TRACKER</b> ══╗\n"
            f"Status: <b>{'ON' if on else 'OFF'}</b>\n"
            f"Users: <code>{n}</code>\n\n"
            f"<code>.track on|off</code>\n"
            f"<code>.trackadd</code> reply/id/@user\n"
            f"<code>.trackdel</code>\n"
            f"<code>.tracklist</code>\n"
            f"<code>.trackinfo</code> full detail\n"
            f"╚══════════════╝"
        )
        return
    arg = parts[1].lower()
    if arg in ("on", "1", "enable"):
        await set_feature("tracker", True)
        await message.reply_text("✅ Tracker <b>ON</b> — alerts Log Group")
    elif arg in ("off", "0", "disable"):
        await set_feature("tracker", False)
        await message.reply_text("❌ Tracker <b>OFF</b>")
    else:
        await message.reply_text("Usage: <code>.track on|off</code>")


@app.on_message(ub_cmd("trackadd"))
@sudo_only
async def track_add_cmd(client, message: Message):
    raw_t, _ = _target(message)
    uid, name = await _resolve_uid(client, raw_t)
    if not uid:
        await message.reply_text("Reply / <code>.trackadd id</code>")
        return
    await _track_add(uid)
    info = await _cache_user(client, uid)
    uname = f"@{info.get('username')}" if info.get("username") else "—"
    try:
        u = await client.get_users(uid)
        st, detail = _status_detail(getattr(u, "status", None))
        _LAST_STATUS[uid] = st
        _push_hist(uid, f"ADD status={st}")
    except Exception:
        st, detail = "?", ""
    await message.reply_text(
        f"✅ Tracking <b>{name}</b>\n"
        f"ID: <code>{uid}</code>\nUser: {uname}\n"
        f"Now: <b>{st}</b>\nDetail: <code>{detail}</code>"
    )
    await _notify(client, f"👁 <b>TRACK ADD</b>\n<code>{uid}</code> {name} {uname}")


@app.on_message(ub_cmd("trackdel"))
@sudo_only
async def track_del_cmd(client, message: Message):
    raw_t, _ = _target(message)
    uid, name = await _resolve_uid(client, raw_t)
    if not uid:
        await message.reply_text("Reply / <code>.trackdel id</code>")
        return
    await _track_del(uid)
    _LAST_STATUS.pop(uid, None)
    _USER_CACHE.pop(uid, None)
    _HISTORY.pop(uid, None)
    await message.reply_text(f"✅ Removed <code>{uid}</code>")


@app.on_message(ub_cmd("tracklist"))
@sudo_only
async def track_list_cmd(client, message: Message):
    users = await _track_list()
    if not users:
        await message.reply_text("Track list empty.")
        return
    lines = []
    for uid in users:
        st = _LAST_STATUS.get(uid, "?")
        c = _USER_CACHE.get(uid) or {}
        nm = c.get("name") or str(uid)
        un = f"@{c['username']}" if c.get("username") else ""
        prem = "⭐" if c.get("premium") else ""
        lines.append(f"• <code>{uid}</code> {nm} {un} {prem} — <b>{st}</b>")
    on = await get_feature("tracker", False)
    await message.reply_text(
        f"╔══ 👁 <b>TRACKING LIST</b> ══╗\n"
        f"[{'ON' if on else 'OFF'}] · {len(users)} users\n\n"
        + "\n".join(lines)
        + "\n╚══════════════╝"
    )


@app.on_message(ub_cmd("trackinfo"))
@sudo_only
async def track_info_cmd(client, message: Message):
    raw_t, _ = _target(message)
    uid, name = await _resolve_uid(client, raw_t)
    if not uid:
        await message.reply_text("Reply / <code>.trackinfo id</code>")
        return
    try:
        u = await client.get_users(uid)
        st, detail = _status_detail(getattr(u, "status", None))
        _LAST_STATUS[uid] = st
        await _cache_user(client, uid)

        try:
            common = len(await client.get_common_chats(uid))
        except Exception:
            common = "?"

        photo_n = 0
        try:
            async for _ in client.get_chat_photos(uid, limit=30):
                photo_n += 1
        except Exception:
            pass

        try:
            chat = await client.get_chat(uid)
            bio = getattr(chat, "bio", None) or "—"
        except Exception:
            bio = "—"

        dc = getattr(u, "dc_id", None)
        hist = _HISTORY.get(uid) or []
        tracked = uid in set(await _track_list())

        text = (
            f"╔══ 👁 <b>TRACK INFO FULL</b> ══╗\n\n"
            f"👤 Name: <b>{u.first_name or '—'} {u.last_name or ''}</b>\n"
            f"🔖 Username: @{u.username or '—'}\n"
            f"🆔 ID: <code>{u.id}</code>\n"
            f"🏛 DC: <code>{dc or '—'}</code> ({DC_MAP.get(dc, '?')})\n"
            f"📡 Status: <b>{st}</b>\n"
            f"📋 Detail: <code>{detail}</code>\n"
            f"📝 Bio: {str(bio)[:200]}\n\n"
            f"⭐ Premium: {'✅' if getattr(u, 'is_premium', False) else '❌'}\n"
            f"✅ Verified: {'✅' if getattr(u, 'is_verified', False) else '❌'}\n"
            f"🤖 Bot: {'✅' if u.is_bot else '❌'}\n"
            f"⚠️ Scam: {'✅' if getattr(u, 'is_scam', False) else '❌'}\n"
            f"🎭 Fake: {'✅' if getattr(u, 'is_fake', False) else '❌'}\n"
            f"🖼 Photos: <code>{photo_n}</code>\n"
            f"👀 Common chats: <code>{common}</code>\n"
            f"👁 In track list: {'✅ Yes' if tracked else '❌ No'}\n"
            f"\n<b>── Recent events ──</b>\n"
            + ("\n".join(f"• <code>{h}</code>" for h in hist[-15:]) if hist else "— none yet")
            + f"\n\n⏱ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
            + "\n╚════════════════════════╝"
        )
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"❌ <code>{type(e).__name__}: {e}</code>")


async def _on_raw(client, update, users, chats):
    try:
        if not await get_feature("tracker", False):
            return
        tracked = await _track_list()
        if not tracked:
            return
        tracked_set = set(int(x) for x in tracked)

        if isinstance(update, raw.types.UpdateUserStatus):
            uid = int(update.user_id)
            if uid not in tracked_set:
                return
            new_st, detail = _status_detail(update.status)
            old = _LAST_STATUS.get(uid)
            _LAST_STATUS[uid] = new_st
            if old == new_st:
                return
            _push_hist(uid, f"{old or '—'} → {new_st}")
            name = str(uid)
            uname = ""
            if uid in users and users[uid]:
                u = users[uid]
                name = getattr(u, "first_name", None) or name
                uname = getattr(u, "username", None) or ""
            elif uid in _USER_CACHE:
                name = _USER_CACHE[uid].get("name") or name
                uname = _USER_CACHE[uid].get("username") or ""
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            await _notify(
                client,
                f"👁 <b>STATUS CHANGE</b>\nTime: <code>{ts}</code>\n"
                f"User: <b>{name}</b>" + (f" (@{uname})" if uname else "")
                + f"\nID: <code>{uid}</code>\n"
                f"{old or '—'} → <b>{new_st}</b>\n<code>{detail}</code>",
            )
            return

        if isinstance(update, raw.types.UpdateUser):
            u = getattr(update, "user", None)
            if not u:
                return
            uid = int(getattr(u, "id", 0) or 0)
            if uid not in tracked_set:
                return
            new_name = getattr(u, "first_name", None) or ""
            new_last = getattr(u, "last_name", None) or ""
            new_user = getattr(u, "username", None) or ""
            old = _USER_CACHE.get(uid) or {}
            changes = []
            if old.get("name") and old["name"] != new_name:
                changes.append(f"Name: <code>{old['name']}</code> → <b>{new_name}</b>")
            if old.get("last_name", "") != new_last and (old.get("last_name") or new_last):
                changes.append(
                    f"Last: <code>{old.get('last_name') or '—'}</code> → <b>{new_last or '—'}</b>"
                )
            if old.get("username", "") != new_user and (old.get("username") or new_user):
                changes.append(
                    f"User: @{old.get('username') or '—'} → <b>@{new_user or '—'}</b>"
                )
            _USER_CACHE[uid] = {
                "name": new_name,
                "last_name": new_last,
                "username": new_user,
                "premium": old.get("premium", False),
                "dc": old.get("dc"),
            }
            if not changes:
                return
            for ch in changes:
                _push_hist(uid, ch.replace("<code>", "").replace("</code>", "").replace("<b>", "").replace("</b>", ""))
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            await _notify(
                client,
                f"👁 <b>PROFILE CHANGE</b>\nTime: <code>{ts}</code>\nID: <code>{uid}</code>\n"
                + "\n".join(changes),
            )
    except Exception as e:
        print(f"[tracker] raw: {e}")


app.add_handler(RawUpdateHandler(_on_raw), group=50)
print("[tracker] raw handler registered")
