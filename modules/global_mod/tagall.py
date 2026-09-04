import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
DELAY_BETWEEN_TAGS = 2.5   # seconds between each user (Telegram flood se bachne ke liye)

# chat_id -> asyncio.Task
TAGALL_TASKS: dict[int, asyncio.Task] = {}


def cmd(name):
    return filters.command(name, prefixes=PREFIXES) & filters.group


async def _tagall_worker(client, chat_id: int, custom_text: str):
    members = []
    try:
        async for member in client.get_chat_members(chat_id):
            if member.user.is_bot or member.user.is_deleted:
                continue
            members.append(member.user)
    except RPCError as e:
        await client.send_message(chat_id, f"❌ Couldn't fetch member list: `{e}`")
        return

    if not members:
        await client.send_message(chat_id, "No taggable members found.")
        return

    total = len(members)
    try:
        for i, user in enumerate(members, 1):
            mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
            text = f"{mention} {custom_text}" if custom_text else mention

            try:
                await client.send_message(chat_id, text)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await client.send_message(chat_id, text)
                except RPCError:
                    pass
            except RPCError:
                pass

            await asyncio.sleep(DELAY_BETWEEN_TAGS)

        await client.send_message(chat_id, f"✅ Tagall complete — {total} members tagged.")
    except asyncio.CancelledError:
        await client.send_message(chat_id, "🛑 Tagall stopped.")
        raise
    finally:
        TAGALL_TASKS.pop(chat_id, None)


@app.on_message(cmd("tagall"))
@sudo_only
async def tagall_cmd(client, message: Message):
    """
    .tagall [message] — tags every non-bot member ONE BY ONE.
    Each message = 1 user mention + your text.
    Use `.tagallstop` to cancel.
    """
    chat_id = message.chat.id
    if chat_id in TAGALL_TASKS:
        await message.reply_text("A tagall is already running here. Use `.tagallstop` to stop it.")
        return

    custom_text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    await message.reply_text(
        "🏷 Tagging everyone **user-by-user**...\n"
        "Use `.tagallstop` to cancel."
    )

    task = asyncio.create_task(_tagall_worker(client, chat_id, custom_text))
    TAGALL_TASKS[chat_id] = task


@app.on_message(cmd("tagallstop"))
@sudo_only
async def tagallstop_cmd(client, message: Message):
    task = TAGALL_TASKS.get(message.chat.id)
    if not task:
        await message.reply_text("No tagall running here.")
        return
    task.cancel()


@app.on_message(cmd("tagme"))
@sudo_only
async def tagme_cmd(client, message: Message):
    """Mentions just the person who ran the command."""
    user = message.from_user
    await message.reply_text(f'<a href="tg://user?id={user.id}">{user.first_name}</a>')
