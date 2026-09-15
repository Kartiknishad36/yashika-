from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import set_feature, get_feature, get_all_chats

PREFIXES = [".", "!"]

@app.on_message(filters.command("autoleave", prefixes=PREFIXES))
@sudo_only
async def autoleave_cmd(client, message: Message):
    if len(message.command) < 2:
        on = await get_feature("autoleave", False)
        return await message.reply_text(
            f"🚪 AutoLeave: **{'ON' if on else 'OFF'}**\n"
            f"`·autoleave on|off`\n`·autoleave now` (careful)"
        )
    arg = message.command[1].lower()
    if arg in ("on", "off"):
        await set_feature("autoleave", arg == "on")
        return await message.reply_text(f"AutoLeave {arg.upper()}")
    if arg == "now":
        status = await message.reply_text("Leaving non-admin tracked groups…")
        left = 0
        try:
            chats = await get_all_chats() or []
        except Exception:
            chats = []
        for cid in list(chats)[:40]:
            try:
                chat = await client.get_chat(cid)
                if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
                    continue
                member = await client.get_chat_member(cid, "me")
                if str(member.status) in ("administrator", "owner", "creator", "ChatMemberStatus.ADMINISTRATOR", "ChatMemberStatus.OWNER"):
                    continue
                await client.leave_chat(cid)
                left += 1
            except Exception:
                continue
        return await status.edit_text(f"✅ Left \~`{left}` groups")
