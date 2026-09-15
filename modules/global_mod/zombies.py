import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import FloodWait, UserAdminInvalid, ChatAdminRequired
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

@app.on_message(filters.command(["zombies", "cleanzombies", "zombie"], prefixes=PREFIXES) & filters.group)
@sudo_only
async def zombies_cmd(client, message: Message):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return await message.reply_text("Sirf groups mein.")
    arg = message.command[1].lower() if len(message.command) > 1 else "count"
    do_clean = arg in ("clean", "clear", "kick", "ban", "remove")
    permanent_ban = arg == "ban" or (len(message.command) > 2 and message.command[2].lower() == "ban")
    status = await message.reply_text("👻 Zombie scan…")
    zombies, scanned = [], 0
    try:
        async for member in client.get_chat_members(message.chat.id):
            scanned += 1
            u = member.user
            if not u or not u.is_deleted:
                continue
            if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                continue
            zombies.append(u.id)
    except ChatAdminRequired:
        return await status.edit_text("❌ Admin rights chahiye.")
    except Exception as e:
        return await status.edit_text(f"❌ `{e}`")
    if not zombies:
        return await status.edit_text(f"✅ Clean — scanned `{scanned}`, zombies `0`")
    if not do_clean:
        return await status.edit_text(
            f"👻 Zombies: `{len(zombies)}` / scanned `{scanned}`\n"
            f"`·zombies clean` | `·zombies ban`"
        )
    removed = failed = 0
    await status.edit_text(f"🧹 Cleaning `{len(zombies)}`…")
    for uid in zombies:
        try:
            await client.ban_chat_member(message.chat.id, uid)
            if not permanent_ban:
                try:
                    await client.unban_chat_member(message.chat.id, uid)
                except Exception:
                    pass
            removed += 1
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            try:
                await client.ban_chat_member(message.chat.id, uid)
                if not permanent_ban:
                    await client.unban_chat_member(message.chat.id, uid)
                removed += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.15)
    await status.edit_text(f"✅ Removed `{removed}` | Failed `{failed}`")
