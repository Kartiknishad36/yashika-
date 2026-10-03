"""
🥭 MONGO DP SYSTEM

  .dp / .mongodp / .getdp     → reply/user → saari profile DPs bhejo
  .dpsave                    → reply/user → current DPs file_id save (local DB)
  .dplog / .dphistory        → reply/user → saved DP history + count
  .dpclear                   → reply/user → us user ki saved DP list clear

Storage: database/mongo.py (storage.json) → key "mongo_dp"
Telegram API se live photos + local tracked file_ids.
"""
import asyncio
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import MessageMediaType

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import _read, _write, _lock

PREFIXES = [".", "!"]


def cmd(*names):
    return filters.command(list(names), prefixes=PREFIXES)


async def _resolve_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        arg = message.command[1].lstrip("@")
        try:
            return await client.get_users(
                int(arg) if arg.lstrip("-").isdigit() else arg
            )
        except Exception:
            return None
    return message.from_user


async def _collect_photos(client, user_id: int, limit: int = 50):
    """Live Telegram profile photos (newest first)."""
    photos = []
    try:
        async for p in client.get_chat_photos(user_id, limit=limit):
            photos.append(p)
    except Exception:
        pass
    return photos


async def _dp_store_get(user_id: int) -> list:
    async with _lock:
        data = _read()
        data.setdefault("mongo_dp", {})
        return list(data["mongo_dp"].get(str(user_id), []))


async def _dp_store_add(user_id: int, entries: list):
    """entries: list of {file_id, unique_id, date, w, h}"""
    async with _lock:
        data = _read()
        data.setdefault("mongo_dp", {})
        key = str(user_id)
        existing = data["mongo_dp"].setdefault(key, [])
        seen = {e.get("unique_id") or e.get("file_id") for e in existing}
        for e in entries:
            uid = e.get("unique_id") or e.get("file_id")
            if uid and uid not in seen:
                existing.append(e)
                seen.add(uid)
        data["mongo_dp"][key] = existing[-100:]  # keep last 100
        _write(data)


async def _dp_store_clear(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("mongo_dp", {})
        data["mongo_dp"][str(user_id)] = []
        _write(data)


def _photo_entry(photo) -> dict:
    """Pyrogram ChatPhoto / Photo → dict."""
    file_id = getattr(photo, "file_id", None)
    unique = getattr(photo, "file_unique_id", None)
    # sizes list on Photo
    w = h = None
    if getattr(photo, "sizes", None):
        best = photo.sizes[-1]
        w = getattr(best, "width", None)
        h = getattr(best, "height", None)
        if not file_id:
            file_id = getattr(best, "file_id", None)
        if not unique:
            unique = getattr(best, "file_unique_id", None)
    return {
        "file_id": file_id,
        "unique_id": unique,
        "date": int(datetime.now(timezone.utc).timestamp()),
        "w": w,
        "h": h,
    }


# ───────────────────── .dp / .mongodp ─────────────────────
@app.on_message(cmd("dp", "mongodp", "getdp", "mdp"))
@sudo_only
async def mongo_dp_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text(
            "🥭 <b>Mongo DP</b>\n"
            "Usage: <b>reply</b> ya <code>.dp @user</code> / <code>.dp id</code>"
        )
        return

    status = await message.reply_text(
        f"🥭 Mongo DP fetch… <code>{user.first_name}</code>"
    )

    photos = await _collect_photos(client, user.id, limit=50)
    if not photos:
        await status.edit_text(
            f"❌ <b>{user.first_name}</b> ki koi profile photo nahi / private."
        )
        return

    # save to local mongo_dp store
    entries = [_photo_entry(p) for p in photos]
    await _dp_store_add(user.id, entries)

    await status.edit_text(
        f"🥭 <b>Mongo DP</b> · {user.mention}\n"
        f"🖼 Photos: <code>{len(photos)}</code>\n"
        f"Sending…"
    )

    sent = 0
    for i, p in enumerate(photos, 1):
        try:
            await client.send_photo(
                message.chat.id,
                p.file_id,
                caption=(
                    f"🥭 <b>Mongo DP</b> {i}/{len(photos)}\n"
                    f"User: {user.mention}\n"
                    f"ID: <code>{user.id}</code>"
                ),
                reply_to_message_id=message.id,
            )
            sent += 1
            await asyncio.sleep(0.35)
        except Exception:
            try:
                # fallback: download-less send via file_id on sizes
                if getattr(p, "sizes", None):
                    await client.send_photo(
                        message.chat.id,
                        p.sizes[-1].file_id,
                        caption=f"🥭 DP {i}/{len(photos)} · {user.id}",
                        reply_to_message_id=message.id,
                    )
                    sent += 1
            except Exception:
                pass

    await status.edit_text(
        f"✅ <b>Mongo DP done</b>\n"
        f"User: {user.mention}\n"
        f"Sent: <code>{sent}/{len(photos)}</code>\n"
        f"Saved in DB: <code>yes</code>"
    )


# ───────────────────── .dpsave ─────────────────────
@app.on_message(cmd("dpsave", "savedp", "mongosave"))
@sudo_only
async def dp_save_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Usage: reply / <code>.dpsave @user</code>")
        return

    photos = await _collect_photos(client, user.id, limit=50)
    if not photos:
        await message.reply_text("❌ Koi DP nahi mili.")
        return

    entries = [_photo_entry(p) for p in photos]
    await _dp_store_add(user.id, entries)
    total = len(await _dp_store_get(user.id))

    await message.reply_text(
        f"✅ <b>Mongo DP saved</b>\n"
        f"User: {user.mention}\n"
        f"New batch: <code>{len(entries)}</code>\n"
        f"Total stored: <code>{total}</code>"
    )


# ───────────────────── .dplog ─────────────────────
@app.on_message(cmd("dplog", "dphistory", "mongolog"))
@sudo_only
async def dp_log_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Usage: reply / <code>.dplog @user</code>")
        return

    stored = await _dp_store_get(user.id)
    live = await _collect_photos(client, user.id, limit=100)

    lines = [
        "🥭 <b>MONGO DP LOG</b>",
        f"User: {user.mention}",
        f"ID: <code>{user.id}</code>",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🖼 Live Telegram DPs: <code>{len(live)}</code>",
        f"💾 Stored in DB: <code>{len(stored)}</code>",
    ]

    if stored:
        lines.append("")
        lines.append("<b>Last saved entries:</b>")
        for i, e in enumerate(stored[-10:], 1):
            ts = e.get("date") or 0
            try:
                dt = datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime(
                    "%Y-%m-%d %H:%M"
                )
            except Exception:
                dt = "—"
            wh = ""
            if e.get("w") and e.get("h"):
                wh = f" {e['w']}x{e['h']}"
            lines.append(
                f"{i}. <code>{(e.get('unique_id') or '—')[:16]}</code>{wh} · {dt}"
            )

    lines.append("")
    lines.append(
        "Commands: <code>.dp</code> <code>.dpsave</code> <code>.dpclear</code>"
    )
    await message.reply_text("\n".join(lines))


# ───────────────────── .dpclear ─────────────────────
@app.on_message(cmd("dpclear", "cleardp"))
@sudo_only
async def dp_clear_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Usage: reply / <code>.dpclear @user</code>")
        return
    await _dp_store_clear(user.id)
    await message.reply_text(
        f"🗑 Mongo DP store cleared for {user.mention}"
    )


# ───────────────────── auto-track on new photo (optional light) ─────────────────────
@app.on_message(
    filters.incoming & ~filters.me & ~filters.bot & ~filters.service,
    group=13,
)
async def _dp_auto_hint(client, message: Message):
    """
    Jab user message kare to current DP unique_id track karo
    (photo change detect ke liye).
    """
    if not message.from_user:
        return
    try:
        uid = message.from_user.id
        photos = []
        async for p in client.get_chat_photos(uid, limit=1):
            photos.append(p)
            break
        if not photos:
            return
        entry = _photo_entry(photos[0])
        if not entry.get("unique_id"):
            return
        stored = await _dp_store_get(uid)
        ids = {e.get("unique_id") for e in stored}
        if entry["unique_id"] not in ids:
            await _dp_store_add(uid, [entry])
    except Exception:
        pass
