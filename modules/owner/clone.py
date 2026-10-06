"""
Profile cloner (userbot)
  .clonemode on|off
  .clone              reply / id / @username
  .back               restore name/bio + delete ONLY cloned DP(s)

Note: Telegram user ID / @username clone nahi ho sakte (platform limit).
Name, bio, DP same dikhte hain.
"""
import os
import json

from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only, ub_cmd

BACKUP_FILE = "my_backup.json"
CLONE_ON = True


async def _photo_ids(client) -> list:
    """Current profile photo file_ids (newest first)."""
    ids = []
    try:
        async for photo in client.get_chat_photos("me", limit=20):
            fid = getattr(photo, "file_id", None)
            if fid:
                ids.append(fid)
    except Exception as e:
        print(f"[clone] photo list: {e}")
    return ids


async def _resolve_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        chat = await client.get_chat(u.id)
        return u, chat

    parts = (message.text or "").split()
    if len(parts) < 2:
        return None, None
    arg = parts[1].strip()
    try:
        if arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit()):
            chat = await client.get_chat(int(arg))
        else:
            chat = await client.get_chat(arg)
        try:
            u = await client.get_users(chat.id)
        except Exception:
            u = chat
        return u, chat
    except Exception:
        return None, None


@app.on_message(ub_cmd("clonemode"))
@sudo_only
async def clone_toggle(client, message: Message):
    global CLONE_ON
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.reply_text(
            f"Cloner: <b>{'ON' if CLONE_ON else 'OFF'}</b>\n"
            f"<code>.clonemode on</code> | <code>.clonemode off</code>",
            protect_content=True,
        )
        return
    arg = parts[1].lower()
    if arg in ("on", "1", "enable"):
        CLONE_ON = True
        await message.reply_text("✅ Cloner <b>ON</b>", protect_content=True)
    elif arg in ("off", "0", "disable"):
        CLONE_ON = False
        await message.reply_text("❌ Cloner <b>OFF</b>", protect_content=True)
    else:
        await message.reply_text("Usage: <code>.clonemode on|off</code>", protect_content=True)


@app.on_message(ub_cmd("clone"))
@sudo_only
async def clone_profile(client, message: Message):
    global CLONE_ON
    if not CLONE_ON:
        await message.reply_text(
            "Cloner OFF — <code>.clonemode on</code>",
            protect_content=True,
        )
        return

    target_user, target_chat = await _resolve_user(client, message)
    if not target_chat:
        await message.reply_text(
            "Usage:\n"
            "• Reply + <code>.clone</code>\n"
            "• <code>.clone 123456789</code>\n"
            "• <code>.clone @username</code>",
            protect_content=True,
        )
        return

    # ── backup BEFORE any change ────────────────────────────────────────────
    me_chat = await client.get_chat("me")
    old_photo_ids = await _photo_ids(client)
    backup = {
        "first_name": me_chat.first_name or "",
        "last_name": me_chat.last_name or "",
        "bio": getattr(me_chat, "bio", None) or "",
        "photo_ids_before": old_photo_ids,
        "added_photo_ids": [],
    }
    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(backup, f, ensure_ascii=False, indent=2)
    except Exception as e:
        await message.reply_text(f"❌ Backup fail: <code>{e}</code>", protect_content=True)
        return

    name = (
        getattr(target_user, "first_name", None)
        or getattr(target_chat, "first_name", None)
        or "User"
    )
    mention = (
        target_user.mention
        if hasattr(target_user, "mention")
        else f"<code>{target_chat.id}</code>"
    )
    uid = target_chat.id
    uname = (
        getattr(target_chat, "username", None)
        or getattr(target_user, "username", None)
        or "—"
    )

    m = await message.reply_text(
        f"🔄 Cloning {mention}…\nID: <code>{uid}</code>",
        protect_content=True,
    )

    added_ids = []
    try:
        # ── DP from target ──────────────────────────────────────────────────
        dp_ok = False
        try:
            # Prefer full-res via get_chat_photos
            target_photos = []
            async for ph in client.get_chat_photos(uid, limit=1):
                target_photos.append(ph)
            if target_photos:
                path = await client.download_media(target_photos[0].file_id)
                if path:
                    await client.set_profile_photo(photo=path)
                    try:
                        os.remove(path)
                    except Exception:
                        pass
                    dp_ok = True
            else:
                photo = getattr(target_chat, "photo", None)
                if photo:
                    file_id = getattr(photo, "big_file_id", None)
                    path = await client.download_media(file_id or photo)
                    if path:
                        await client.set_profile_photo(photo=path)
                        try:
                            os.remove(path)
                        except Exception:
                            pass
                        dp_ok = True
        except Exception as e:
            await m.edit_text(
                f"⚠️ DP skip: <code>{e}</code>\nName/bio continue…",
                protect_content=True,
            )

        # Track which photos are NEW (cloned)
        if dp_ok:
            new_ids = await _photo_ids(client)
            old_set = set(old_photo_ids)
            for fid in new_ids:
                if fid not in old_set:
                    added_ids.append(fid)
            backup["added_photo_ids"] = added_ids
            try:
                with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                    json.dump(backup, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        # ── name + bio (same look as target) ────────────────────────────────
        first_name = (getattr(target_chat, "first_name", None) or name or " ")[:64]
        last_name = (getattr(target_chat, "last_name", None) or "")[:64]
        bio = (getattr(target_chat, "bio", None) or "")[:70]

        await client.update_profile(
            first_name=first_name or " ",
            last_name=last_name,
            bio=bio,
        )

        await m.edit_text(
            f"✅ <b>Cloned</b>\n\n"
            f"From: {mention}\n"
            f"Target ID: <code>{uid}</code>\n"
            f"Username: @{uname}\n"
            f"Name: <b>{first_name} {last_name}</b>\n"
            f"Bio: <i>{bio or '—'}</i>\n"
            f"DP: {'✅' if dp_ok else '❌'}\n"
            f"Added photos: <code>{len(added_ids)}</code>\n\n"
            f"<i>Note: Telegram ID / @username change nahi hote.</i>\n"
            f"Restore: <code>.back</code>",
            protect_content=True,
        )
    except Exception as e:
        await m.edit_text(f"❌ Clone error: <code>{e}</code>", protect_content=True)


@app.on_message(ub_cmd("back"))
@sudo_only
async def restore_profile(client, message: Message):
    if not os.path.exists(BACKUP_FILE):
        await message.reply_text(
            "Backup nahi — pehle <code>.clone</code> chalao.",
            protect_content=True,
        )
        return

    m = await message.reply_text("♻️ Restoring…", protect_content=True)
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ONLY delete photos that were added during .clone
        added = data.get("added_photo_ids") or []
        deleted = 0
        if added:
            for fid in added:
                try:
                    await client.delete_profile_photos(fid)
                    deleted += 1
                except Exception as e:
                    print(f"[clone] delete photo: {e}")
        else:
            # Fallback: delete photos not in before-list (still keep old ones)
            before = set(data.get("photo_ids_before") or [])
            if before:
                current = await _photo_ids(client)
                for fid in current:
                    if fid not in before:
                        try:
                            await client.delete_profile_photos(fid)
                            deleted += 1
                        except Exception:
                            pass

        await client.update_profile(
            first_name=(data.get("first_name") or " ")[:64],
            last_name=(data.get("last_name") or "")[:64],
            bio=(data.get("bio") or "")[:70],
        )

        await m.edit_text(
            f"✅ <b>Back done</b>\n\n"
            f"Name/bio restore ✅\n"
            f"Cloned DP deleted: <code>{deleted}</code>\n"
            f"Purani DPs safe ✅",
            protect_content=True,
        )
    except Exception as e:
        await m.edit_text(f"❌ Back error: <code>{e}</code>", protect_content=True)
