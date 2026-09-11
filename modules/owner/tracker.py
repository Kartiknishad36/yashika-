"""
Online Tracker (userbot):
  .track on|off          — global tracker
  .trackadd <id|reply>   — user ko track list mein
  .trackdel <id|reply>
  .tracklist

Jab tracked user online/offline ho → Saved Messages (+ LOG_GROUP_ID).

Privacy-heavy: sirf apne account pe use karo.
"""
import time
from pyrogram import filters, raw
from pyrogram.types import Message, User
from pyrogram.handlers import RawUpdateHandler

from core.clients import app
from config import OWNER_ID, LOG_GROUP_ID
from modules.owner.sudoers import sudo_only, SUDO_USERS
from database.mongo import (
    get_feature,
    set_feature,
    _read,
    _write,
    _lock,
)

PREFIXES = [".", "!"]

# user_id -> "online" / "offline" / "recently" ...
_LAST_STATUS: dict[int, str] = {}


async def _track_list() -> list[int]:
    async with _lock:
        data = _read()
        data.setdefault("track_users", [])
        return list(data["track_users"])


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
        data["track_users"] = [x for x in data["track_users"] if x != uid]
        _write(data)


async def _notify(client, text: str):
    try:
        me = await client.get_me()
        await client.send_message(me.id, text)
    except Exception:
        pass
    if LOG_GROUP_ID:
        try:
            await client.send_message(LOG_GROUP_ID, text)
        except Exception:
            pass


def _target(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        return u.id, u.first_name
    if len(message.command) > 1:
        try:
            return int(message.command[1]), message.command[1]
        except ValueError:
            return None, None
    return None, None


@app.on_message(filters.command(["track"], prefixes=PREFIXES))
@sudo_only
async def track_toggle(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("tracker", False)
        await message.reply_text(
            f"Tracker **{'ON' if on else 'OFF'}**\n"
            f"`.track on|off` | `.trackadd` | `.trackdel` | `.tracklist`"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_feature("tracker", True)
        await message.reply_text("✅ Online tracker **ON**.")
    elif arg in ("off", "0", "disable"):
        await set_feature("tracker", False)
        await message.reply_text("❌ Tracker **OFF**.")
    else:
        await message.reply_text("Usage: `.track on|off`")


@app.on_message(filters.command(["trackadd"], prefixes=PREFIXES))
@sudo_only
async def track_add_cmd(client, message: Message):
    uid, name = _target(message)
    if not uid:
        await message.reply_text("Reply or `.trackadd <user_id>`")
        return
    await _track_add(uid)
    await message.reply_text(f"✅ Tracking <b>{name}</b> (`{uid}`)")


@app.on_message(filters.command(["trackdel"], prefixes=PREFIXES))
@sudo_only
async def track_del_cmd(client, message: Message):
    uid, name = _target(message)
    if not uid:
        await message.reply_text("Reply or `.trackdel <user_id>`")
        return
    await _track_del(uid)
    _LAST_STATUS.pop(uid, None)
    await message.reply_text(f"✅ Removed `{uid}` from track list.")


@app.on_message(filters.command(["tracklist"], prefixes=PREFIXES))
@sudo_only
async def track_list_cmd(client, message: Message):
    users = await _track_list()
    if not users:
        await message.reply_text("Track list empty.")
        return
    lines = []
    for uid in users:
        st = _LAST_STATUS.get(uid, "?")
        lines.append(f"• <code>{uid}</code> — {st}")
    await message.reply_text("👁 <b>Tracking</b>\n\n" + "\n".join(lines))


def _status_name(status) -> str:
    if status is None:
        return "unknown"
    # raw user status types
    n = type(status).__name__
    if "Empty" in n:
        return "long_ago"
    if "Online" in n:
        return "online"
    if "Offline" in n:
        return "offline"
    if "Recently" in n:
        return "recently"
    if "LastWeek" in n:
        return "last_week"
    if "LastMonth" in n:
        return "last_month"
    return n


async def _on_raw(client, update, users, chats):
    if not await get_feature("tracker", False):
        return
    # UpdateUserStatus
    if not isinstance(update, raw.types.UpdateUserStatus):
        return
    uid = update.user_id
    tracked = await _track_list()
    if uid not in tracked:
        return

    new_st = _status_name(update.status)
    old = _LAST_STATUS.get(uid)
    _LAST_STATUS[uid] = new_st
    if old == new_st:
        return

    name = str(uid)
    if uid in users and users[uid]:
        u = users[uid]
        name = getattr(u, "first_name", None) or name

    ts = time.strftime("%H:%M:%S")
    await _notify(
        client,
        f"👁 <b>Status</b> [{ts}]\n"
        f"User: <b>{name}</b> (<code>{uid}</code>)\n"
        f"{old or '—'} → <b>{new_st}</b>",
    )


# register raw handler once
app.add_handler(RawUpdateHandler(_on_raw), group=50)
