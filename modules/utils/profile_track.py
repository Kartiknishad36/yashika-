from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!"]
_SNAP = {}

@app.on_message(filters.command("profiletrack", prefixes=PREFIXES))
@sudo_only
async def profiletrack_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "`·profiletrack on` (reply)\n`·profiletrack off`\n`·profiletrack list`"
        )
    arg = message.command[1].lower()
    tracked = await get_feature("profile_track", {}) or {}
    if not isinstance(tracked, dict):
        tracked = {}
    if arg == "list":
        if not tracked:
            return await message.reply_text("Empty")
        return await message.reply_text("👁\n" + "\n".join(f"• `{k}`" for k in tracked))
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 2 and message.command[2].lstrip("-").isdigit():
        uid = int(message.command[2])
    if arg in ("on", "add"):
        if not uid:
            return await message.reply_text("Reply + on")
        u = await client.get_users(uid)
        chat = await client.get_chat(uid)
        tracked[str(uid)] = {
            "name": f"{u.first_name or ''} {u.last_name or ''}".strip(),
            "bio": getattr(chat, "bio", "") or "",
            "username": u.username or "",
        }
        await set_feature("profile_track", tracked)
        return await message.reply_text(f"✅ Tracking {u.mention}")
    if arg in ("off", "del"):
        if not uid:
            return await message.reply_text("Reply/id + off")
        tracked.pop(str(uid), None)
        await set_feature("profile_track", tracked)
        return await message.reply_text(f"✅ Stopped `{uid}`")

@app.on_message(filters.incoming & \~filters.me & \~filters.bot, group=14)
async def profiletrack_watch(client, message: Message):
    if not message.from_user:
        return
    uid = message.from_user.id
    tracked = await get_feature("profile_track", {}) or {}
    if str(uid) not in tracked:
        return
    try:
        u = message.from_user
        chat = await client.get_chat(uid)
        cur = {
            "name": f"{u.first_name or ''} {u.last_name or ''}".strip(),
            "bio": getattr(chat, "bio", "") or "",
            "username": u.username or "",
        }
        old = tracked.get(str(uid)) or {}
        changes = []
        if old.get("name") != cur["name"]:
            changes.append(f"Name: `{old.get('name')}` → `{cur['name']}`")
        if old.get("bio") != cur["bio"]:
            changes.append("Bio changed")
        if old.get("username") != cur["username"]:
            changes.append(f"@{old.get('username') or '—'} → @{cur['username'] or '—'}")
        if changes:
            tracked[str(uid)] = cur
            await set_feature("profile_track", tracked)
            await client.send_message(
                "me",
                f"👁 **Profile change**\n{u.mention} (`{uid}`)\n" + "\n".join(changes),
            )
    except Exception:
        pass
