from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

@app.on_message(filters.command("msginfo", prefixes=PREFIXES))
@sudo_only
async def msginfo_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        return await message.reply_text("Reply + `·msginfo`")
    lines = [
        "📋 **MSG INFO**",
        f"ID: `{r.id}`",
        f"Date: `{r.date}`",
        f"Edit: **{'Yes' if r.edit_date else 'No'}**",
        f"Forward: **{'Yes' if r.forward_date or r.forward_from or r.forward_from_chat else 'No'}**",
    ]
    if r.from_user:
        lines.append(f"Sender: {r.from_user.mention} (`{r.from_user.id}`)")
    await message.reply_text("\n".join(lines))

@app.on_message(filters.command(["chatinfo2", "groupinfo2"], prefixes=PREFIXES))
@sudo_only
async def chatinfo2_cmd(client, message: Message):
    target = message.chat.id
    if len(message.command) > 1:
        a = message.command[1]
        target = int(a) if a.lstrip("-").isdigit() else a
    try:
        chat = await client.get_chat(target)
    except Exception as e:
        return await message.reply_text(f"❌ `{e}`")
    await message.reply_text(
        f"📊 **{chat.title or chat.first_name}**\n"
        f"ID: `{chat.id}`\nType: `{chat.type}`\n"
        f"Username: @{chat.username or '—'}\n"
        f"Members: `{getattr(chat, 'members_count', '—')}`"
    )

@app.on_message(filters.command("common2", prefixes=PREFIXES))
@sudo_only
async def common2_cmd(client, message: Message):
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        arg = message.command[1]
        try:
            u = await client.get_users(int(arg) if arg.isdigit() else arg)
            uid = u.id
        except Exception as e:
            return await message.reply_text(f"❌ `{e}`")
    if not uid:
        return await message.reply_text("Reply / `·common2 @user`")
    lines = []
    try:
        async for c in client.get_common_chats(uid):
            lines.append(f"• {c.title or c.first_name} (`{c.id}`)")
            if len(lines) >= 25:
                break
    except Exception as e:
        return await message.reply_text(f"❌ `{e}`")
    await message.reply_text("👥 **Common**\n" + ("\n".join(lines) or "None"))

@app.on_message(filters.command(["idtouser", "id2user"], prefixes=PREFIXES))
@sudo_only
async def idtouser_cmd(client, message: Message):
    if len(message.command) < 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text("`·idtouser 123456`")
    try:
        u = await client.get_users(int(message.command[1]))
        await message.reply_text(f"{u.mention}\n`{u.id}`\n@{u.username or '—'}")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")

@app.on_message(filters.command(["usertoid", "user2id"], prefixes=PREFIXES))
@sudo_only
async def usertoid_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("`·usertoid @username`")
    try:
        u = await client.get_users(message.command[1])
        await message.reply_text(f"`{u.id}`\n{u.mention}")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")
