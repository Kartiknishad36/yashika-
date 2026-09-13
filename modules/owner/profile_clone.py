"""
Profile cloner (userbot):
  .clonemode on|off
  .clone              → reply to user
  .clone <user_id>
  .clone @username
  .back               → restore name/bio, remove extra DPs

Backup: my_backup.json
"""
import os
import json

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
BACKUP_FILE = "my_backup.json"
CLONE_ON = True


async def _resolve_user(client, message: Message):
    """Reply / id / @username → (user-ish, chat)."""
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        chat = await client.get_chat(u.id)
        return u, chat

    if len(message.command) < 2:
        return None, None

    arg = message.command[1].strip()
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


@app.on_message(filters.command("clonemode", prefixes=PREFIXES))
@sudo_only
async def clone_toggle(client, message: Message):
    global CLONE_ON
    if len(message.command) < 2:
        await message.reply_text(
            f"Cloner is <b>{'ON' if CLONE_ON else 'OFF'}</b>\n"
            f"<code>.clonemode on</code> | <code>.clonemode off</code>",
            protect_content=True,
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        CLONE_ON = True
        await message.reply_text("✅ Cloner <b>ON</b>", protect_content=True)
    elif arg in ("off", "0", "disable"):
        CLONE_ON = False
        await message.reply_text("❌ Cloner <b>OFF</b>", protect_content=True)
    else:
        await message.reply_text("Usage: <code>.clonemode on|off</code>", protect_content=True)


@app.on_message(filters.command("clone", prefixes=PREFIXES))
@sudo_only
async def clone_profile(client, message: Message):
    global CLONE_ON
    if not CLONE_ON:
        await message.reply_text(
            "Cloner OFF hai — <code>.clonemode on</code> karo",
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

    me_chat = await client.get_chat("me")
    backup = {
        "first_name": me_chat.first_name or "",
        "last_name": me_chat.last_name or "",
        "bio": getattr(me_chat, "bio", None) or "",
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

    try:
        photo = getattr(target_chat, "photo", None)
        if photo:
            try:
                file_id = getattr(photo, "big_file_id", None)
                path = await client.download_media(file_id or photo)
                if path:
                    await client.set_profile_photo(photo=path)
                    try:
                        os.remove(path)
                    except Exception:
                        pass
            except Exception as e:
                await m.edit_text(
                    f"⚠️ DP skip: <code>{e}</code>\nName/bio try…",
                    protect_content=True,
                )

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
            f"ID: <code>{uid}</code>\n"
            f"Username: @{uname}\n"
            f"Name: <b>{first_name} {last_name}</b>\n"
            f"Bio: <i>{bio or '—'}</i>\n\n"
            f"Restore: <code>.back</code>",
            protect_content=True,
        )
    except Exception as e:
        await m.edit_text(f"❌ Clone error: <code>{e}</code>", protect_content=True)


@app.on_message(filters.command("back", prefixes=PREFIXES))
@sudo_only
async def restore_profile(client, message: Message):
    if not os.path.exists(BACKUP_FILE):
        await message.reply_text(
            "Backup nahi mila — pehle <code>.clone</code> chalao.",
            protect_content=True,
        )
        return

    m = await message.reply_text("♻️ Restoring…", protect_content=True)
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            async for photo in client.get_chat_photos("me"):
                try:
                    await client.delete_profile_photos(photo.file_id)
                except Exception:
                    pass
        except Exception:
            pass

        await client.update_profile(
            first_name=(data.get("first_name") or " ")[:64],
            last_name=(data.get("last_name") or "")[:64],
            bio=(data.get("bio") or "")[:70],
        )
        await m.edit_text(
            "✅ <b>Back done</b> — name/bio restore.\n"
            "Note: purani DP manual set karni pad sakti hai.",
            protect_content=True,
        )
    except Exception as e:
        await m.edit_text(f"❌ Back error: <code>{e}</code>", protect_content=True)
