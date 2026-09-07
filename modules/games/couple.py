""" /couple — random cute couple in the group """
import random
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter

from core.clients import bot
from config import BOT_NAME

if bot is None:
    raise RuntimeError("modules.games.couple needs BOT_TOKEN")

PREFIXES = ["/", ".", "!"]


@bot.on_message(filters.command("couple", prefixes=PREFIXES) & filters.group)
async def couple_cmd(client, message: Message):
    members = []
    try:
        async for m in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.SEARCH):
            u = m.user
            if u and not u.is_bot and not u.is_deleted:
                members.append(u)
            if len(members) >= 80:
                break
    except Exception as e:
        await message.reply_text(f"❌ Members nahi mil sake: `{e}`")
        return

    if len(members) < 2:
        await message.reply_text("Couple ke liye kam se kam 2 members chahiye.")
        return

    a, b = random.sample(members, 2)
    text = (
        f"❤️ <b>Tᴏᴅᴀʏꜱ Cᴜᴛᴇ Cᴏᴜᴘʟᴇ</b> ❤️\n\n"
        f"{a.mention} 🩵 💞 {b.mention}\n\n"
        f"Lᴏᴠᴇ Iꜱ Iɴ Tʜᴇ Aɪʀ ❤️\n"
        f"\~ Fʀᴏᴍ {BOT_NAME.upper()} Wɪᴛʜ Lᴏᴠᴇ 💋"
    )
    await message.reply_text(text)
