"""Mongo DP — .dp .dpsave .dplog .dpclear"""
import asyncio
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd
from database.mongo import _read, _write, _lock


async def _resolve_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    parts = (message.text or "").split()
    if len(parts) > 1:
        arg = parts[1].lstrip("@")
        try:
            return await client.get_users(
                int(arg) if arg.lstrip("-").isdigit() else arg
            )
        except Exception:
            return None
    return message.from_user


async def _collect_photos(client, user_id: int, limit: int = 50):
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
        data["mongo_dp"][key] = existing[-100:]
        _write(data)


async def _dp_store_clear(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("mongo_dp", {})
        data["mongo_dp"][str(user_id)] = []
        _write(data)


def _photo_entry(photo) -> dict:
    file_id = getattr(photo, "file_id", None)
    unique = getattr(photo, "file_unique_id", None)
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


@app.on_message(ub_cmd("dp", "mongodp", "getdp", "mdp") & filters.me)
async def mongo_dp_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Usage: reply ya <code>.dp @user</code>")
        return
    status = await message.reply_text(f"Mongo DP fetch… <code>{user.first_name}</code>")
    photos = await _collect_photos(client, user.id, limit=50)
    if not photos:
        await status.edit_text(f"<b>{user.first_name}</b> ki DP nahi / private.")
        return
    entries = [_photo_entry(p) for p in photos]
    await _dp_store_add(user.id, entries)
    await status.edit_text(f"Mongo DP · {user.mention}\nPhotos: <code>{len(photos)}</code>")
    sent = 0
    for i, p in enumerate(photos, 1):
        try:
            await client.send_photo(
                message.chat.id, p.file_id,
                caption=f"DP {i}/{len(photos)} · {user.mention}",
                reply_to_message_id=message.id,
            )
            sent += 1
            await asyncio.sleep(0.4)
        except Exception:
            pass
    await status.edit_text(f"Done · Sent <code>{sent}/{len(photos)}</code>")


@app.on_message(ub_cmd("dpsave", "savedp", "mongosave") & filters.me)
async def dp_save_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Usage: reply / <code>.dpsave @user</code>")
        return
    photos = await _collect_photos(client, user.id, limit=50)
    if not photos:
        await message.reply_text("Koi DP nahi.")
        return
    entries = [_photo_entry(p) for p in photos]
    await _dp_store_add(user.id, entries)
    total = len(await _dp_store_get(user.id))
    await message.reply_text(
        f"Saved · {user.mention}\nBatch: <code>{len(entries)}</code> · Total: <code>{total}</code>"
    )


@app.on_message(ub_cmd("dplog", "dphistory", "mongolog") & filters.me)
async def dp_log_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Usage: reply / <code>.dplog @user</code>")
        return
    stored = await _dp_store_get(user.id)
    live = await _collect_photos(client, user.id, limit=100)
    await message.reply_text(
        f"<b>Mongo DP Log</b>\n{user.mention}\n"
        f"Live: <code>{len(live)}</code> · Stored: <code>{len(stored)}</code>"
    )


@app.on_message(ub_cmd("dpclear", "cleardp") & filters.me)
async def dp_clear_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await message.reply_text("Usage: reply / <code>.dpclear @user</code>")
        return
    await _dp_store_clear(user.id)
    await message.reply_text(f"Cleared for {user.mention}")
