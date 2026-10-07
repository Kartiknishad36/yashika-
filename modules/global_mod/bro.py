"""
.bro — reply spam / auto roast
  .bro [count]     reply target pe count messages
  .broall [count]  group me random
  .unbro           stop
  .brolist         status
"""
import asyncio
import random

from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only

ACTIVE: dict[int, bool] = {}

LINES = [
    "{t} sun be — baat seedhi rakh",
    "{t} zyada mat uchal",
    "{t} aukat me reh",
    "{t} chill kar bhai",
    "{t} time waste mat kar",
    "{t} scene clear kar",
    "{t} bakchodi band",
    "{t} seedha reply de",
    "{t} drama mat kar",
    "{t} bas kar ab",
    "{t} dimag mat kha",
    "{t} focus rakh",
    "{t} bakwas band",
    "{t} calm down",
    "{t} over mat soch",
    "{t} real me aa",
    "{t} talk sense",
    "{t} enough now",
    "{t} move on",
    "{t} stop spam",
]


def _mention(u) -> str:
    if not u:
        return "User"
    name = u.first_name or "User"
    return f'<a href="tg://user?id={u.id}">{name}</a>'


async def _run_spam(client, chat_id: int, mention: str, count: int):
    ACTIVE[chat_id] = True
    for _ in range(count):
        if not ACTIVE.get(chat_id):
            break
        try:
            msg = random.choice(LINES).format(t=mention)
            await client.send_message(chat_id, msg)
            await asyncio.sleep(0.8)
        except Exception:
            break
    ACTIVE[chat_id] = False


@app.on_message(ub_cmd("bro"))
@sudo_only
async def bro_cmd(client, message: Message):
    parts = (message.text or "").split()
    count = 5
    if len(parts) > 1 and parts[1].isdigit():
        count = min(int(parts[1]), 30)

    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(parts) > 1 and not parts[1].isdigit():
        try:
            target = await client.get_users(parts[1].lstrip("@"))
        except Exception:
            await message.reply_text("❌ User nahi mila. Reply karo ya @user do.")
            return
    else:
        await message.reply_text(
            "Usage:\n"
            "• Reply + <code>.bro 10</code>\n"
            "• <code>.bro @user 5</code>\n"
            "Stop: <code>.unbro</code>"
        )
        return

    mention = _mention(target)
    chat_id = message.chat.id
    if ACTIVE.get(chat_id):
        await message.reply_text("Already running — <code>.unbro</code>")
        return

    await message.reply_text(f"🔥 .bro start ×{count} on {mention}")
    asyncio.create_task(_run_spam(client, chat_id, mention, count))


@app.on_message(ub_cmd("broall"))
@sudo_only
async def broall_cmd(client, message: Message):
    parts = (message.text or "").split()
    count = 5
    if len(parts) > 1 and parts[1].isdigit():
        count = min(int(parts[1]), 20)
    chat_id = message.chat.id
    if ACTIVE.get(chat_id):
        await message.reply_text("Already running — <code>.unbro</code>")
        return
    await message.reply_text(f"🔥 .broall ×{count}")
    asyncio.create_task(_run_spam(client, chat_id, "sab", count))


@app.on_message(ub_cmd("unbro", "brostop"))
@sudo_only
async def unbro_cmd(client, message: Message):
    ACTIVE[message.chat.id] = False
    await message.reply_text("🛑 .bro stopped")


@app.on_message(ub_cmd("brolist"))
@sudo_only
async def brolist_cmd(client, message: Message):
    on = ACTIVE.get(message.chat.id, False)
    await message.reply_text(
        f"<b>.bro status</b>\n"
        f"This chat: <b>{'RUNNING' if on else 'IDLE'}</b>\n"
        f"Cmds: <code>.bro</code> <code>.broall</code> <code>.unbro</code>"
    )
