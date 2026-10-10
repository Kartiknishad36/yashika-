"""
PM extras:
  .antispam on|off  — 5 msgs / 10s → auto block
  .pmlog on|off     — deleted DM → LOG_GROUP
"""
import time
from collections import defaultdict, deque

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID, LOG_GROUP_ID
from modules.owner.sudoers import SUDO_USERS, sudo_only, ub_cmd
from database.mongo import get_feature, set_feature, get_approved_pm

_SPAM: dict[int, deque] = defaultdict(lambda: deque(maxlen=20))
SPAM_WINDOW = 10.0
SPAM_LIMIT = 5

_PM_CACHE: dict[tuple[int, int], dict] = {}
_CACHE_MAX = 500


def _is_privileged(uid: int) -> bool:
    return uid == OWNER_ID or uid in SUDO_USERS


async def _notify_owner(client, text: str):
    if LOG_GROUP_ID:
        try:
            await client.send_message(LOG_GROUP_ID, text)
            return
        except Exception:
            pass
    try:
        me = await client.get_me()
        await client.send_message(me.id, text)
    except Exception:
        pass


@app.on_message(ub_cmd("antispam"))
@sudo_only
async def antispam_toggle(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("antispam", True)
        await message.reply_text(
            f"Anti-PM spam is <b>{'ON' if on else 'OFF'}</b>.\n"
            f"<code>.antispam on</code> | <code>.antispam off</code>"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_feature("antispam", True)
        await message.reply_text("✅ Anti-PM spam <b>ON</b> (5 msgs / 10s → block).")
    elif arg in ("off", "0", "disable"):
        await set_feature("antispam", False)
        await message.reply_text("❌ Anti-PM spam <b>OFF</b>.")
    else:
        await message.reply_text("Usage: <code>.antispam on|off</code>")


@app.on_message(ub_cmd("pmlog"))
@sudo_only
async def pmlog_toggle(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("pmlog", True)
        await message.reply_text(
            f"PM delete-logger is <b>{'ON' if on else 'OFF'}</b>.\n"
            f"<code>.pmlog on</code> | <code>.pmlog off</code>"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_feature("pmlog", True)
        await message.reply_text("✅ PM logger <b>ON</b> (deleted DMs → LOG).")
    elif arg in ("off", "0", "disable"):
        await set_feature("pmlog", False)
        await message.reply_text("❌ PM logger <b>OFF</b>.")
    else:
        await message.reply_text("Usage: <code>.pmlog on|off</code>")


@app.on_message(
    filters.private & filters.incoming & ~filters.bot & ~filters.service,
    group=5,
)
async def pm_cache_and_spam(client, message: Message):
    if not message.from_user:
        return
    uid = message.from_user.id
    if _is_privileged(uid):
        return

    if await get_feature("pmlog", True):
        body = message.text or message.caption or ""
        kind = "text"
        if message.photo:
            kind = "photo"
        elif message.video:
            kind = "video"
        elif message.voice:
            kind = "voice"
        elif message.video_note:
            kind = "video_note"
        elif message.sticker:
            kind = "sticker"
        elif message.document:
            kind = "document"
        elif message.animation:
            kind = "animation"

        key = (message.chat.id, message.id)
        _PM_CACHE[key] = {
            "user_id": uid,
            "name": message.from_user.first_name or "?",
            "username": message.from_user.username or "",
            "kind": kind,
            "body": (body or "")[:500],
            "time": time.time(),
        }
        if len(_PM_CACHE) > _CACHE_MAX:
            for k in list(_PM_CACHE.keys())[: len(_PM_CACHE) - _CACHE_MAX]:
                _PM_CACHE.pop(k, None)

    if not await get_feature("antispam", True):
        return

    approved = await get_approved_pm()
    if uid in approved:
        return

    now = time.time()
    q = _SPAM[uid]
    q.append(now)
    while q and now - q[0] > SPAM_WINDOW:
        q.popleft()

    if len(q) >= SPAM_LIMIT:
        _SPAM.pop(uid, None)
        try:
            await message.reply_text("🚫 Spam detected — blocked.")
        except Exception:
            pass
        try:
            await client.block_user(uid)
        except Exception:
            pass
        await _notify_owner(
            client,
            f"🚫 <b>Anti-PM spam block</b>\n"
            f"User: <code>{uid}</code> {message.from_user.mention}\n"
            f"{SPAM_LIMIT}+ msgs in {SPAM_WINDOW}s",
        )


@app.on_deleted_messages(filters.private)
async def pm_deleted(client, messages):
    if not await get_feature("pmlog", True):
        return
    for msg in messages:
        if not msg or not msg.chat:
            continue
        key = (msg.chat.id, msg.id)
        info = _PM_CACHE.pop(key, None)
        if not info:
            continue
        uname = f"@{info['username']}" if info["username"] else "—"
        text = (
            f"🗑 <b>PM DELETED</b>\n\n"
            f"From: <b>{info['name']}</b> ({uname})\n"
            f"ID: <code>{info['user_id']}</code>\n"
            f"Type: <code>{info['kind']}</code>\n"
            f"Text: <code>{info['body'] or '—'}</code>"
        )
        await _notify_owner(client, text)
