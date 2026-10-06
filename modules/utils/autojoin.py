import re, asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserAlreadyParticipant, InviteHashExpired, InviteHashInvalid, ChannelPrivate
from core.clients import app
from core.notify import notify_owner
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
AUTOJOIN_ON = False
_LINK_RE = re.compile(
    r"(?:https?://)?(?:www\.)?t\.me/(?:joinchat/|\+|)([a-zA-Z0-9_-]{5,}|[a-zA-Z][a-zA-Z0-9_]{3,})"
)

@app.on_message(filters.command("autojoin", prefixes=PREFIXES))
@sudo_only
async def autojoin_cmd(client, message: Message):
    global AUTOJOIN_ON
    if len(message.command) < 2:
        return await message.reply_text(
            f"AutoJoin: <b>{'ON' if AUTOJOIN_ON else 'OFF'}</b>\n"
            f"<code>.autojoin on|off</code>\n<code>.join link</code>"
        )
    AUTOJOIN_ON = message.command[1].lower() in ("on", "1")
    await message.reply_text(f"AutoJoin {'ON' if AUTOJOIN_ON else 'OFF'}")

@app.on_message(filters.command("join", prefixes=PREFIXES))
@sudo_only
async def join_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<code>.join https://t.me/+xxx</code>")
    target = message.text.split(None, 1)[1].strip()
    m = _LINK_RE.search(target)
    join_arg = m.group(1) if m else target
    try:
        chat = await client.join_chat(join_arg)
        await message.reply_text(f"✅ Joined <b>{getattr(chat, 'title', join_arg)}</b>")
    except UserAlreadyParticipant:
        await message.reply_text("Already member")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")

@app.on_message(filters.command("leave", prefixes=PREFIXES))
@sudo_only
async def leave_cmd(client, message: Message):
    if len(message.command) < 2:
        try:
            await message.reply_text("👋 Leaving…")
            await client.leave_chat(message.chat.id)
        except Exception as e:
            await message.reply_text(f"❌ <code>{e}</code>")
        return
    target = message.text.split(None, 1)[1].strip()
    try:
        arg = int(target) if target.lstrip("-").isdigit() else target
        await client.leave_chat(arg)
        await message.reply_text(f"✅ Left <code>{arg}</code>")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")

@app.on_message(filters.incoming & filters.text & ~filters.me & ~filters.bot, group=15)
async def join_watcher(client, message: Message):
    if not AUTOJOIN_ON or not message.text:
        return
    found = _LINK_RE.findall(message.text)
    for token in found[:3]:
        try:
            chat = await client.join_chat(token)
            await notify_owner(client, f"✅ AutoJoin: <b>{getattr(chat, 'title', token)}</b>")
        except (UserAlreadyParticipant, InviteHashExpired, InviteHashInvalid, ChannelPrivate):
            pass
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
        await asyncio.sleep(1.5)
