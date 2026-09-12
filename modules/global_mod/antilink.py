"""
Anti-Link + Anti-Bot (per group)

  .antilink on|off|status
  .antibot on|off
  .antilinkstatus

Sudo only. Userbot needs delete (+ ban for antibot).
"""
import re

from pyrogram import filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus

from core.clients import app
from config import OWNER_ID
from modules.owner.sudoers import sudo_only, SUDO_USERS
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]

_LINK_RE = re.compile(
    r"(?i)(https?://|www\.|t\.me/|telegram\.me/|tg://)\S+"
)


def cmd(name):
    return filters.command(name, prefixes=PREFIXES) & filters.group


def _is_priv(uid: int) -> bool:
    return uid == OWNER_ID or uid in SUDO_USERS


@app.on_message(cmd("antilink"))
@sudo_only
async def antilink_toggle(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await get_chat_flag(chat_id, "antilink", False)
        await message.reply_text(
            f"🔗 AntiLink: <b>{'ON' if on else 'OFF'}</b>\n"
            f"`.antilink on` | `.antilink off`"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_chat_flag(chat_id, "antilink", True)
        await message.reply_text("✅ AntiLink **ON** — links delete honge.")
    elif arg in ("off", "0", "disable"):
        await set_chat_flag(chat_id, "antilink", False)
        await message.reply_text("❌ AntiLink **OFF**.")
    elif arg in ("status",):
        on = await get_chat_flag(chat_id, "antilink", False)
        await message.reply_text(f"AntiLink: <b>{'ON' if on else 'OFF'}</b>")
    else:
        await message.reply_text("Usage: `.antilink on|off|status`")


@app.on_message(cmd("antibot"))
@sudo_only
async def antibot_toggle(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await get_chat_flag(chat_id, "antibot", False)
        await message.reply_text(
            f"🤖 AntiBot: <b>{'ON' if on else 'OFF'}</b>\n"
            f"`.antibot on` | `.antibot off`"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_chat_flag(chat_id, "antibot", True)
        await message.reply_text("✅ AntiBot **ON**.")
    elif arg in ("off", "0", "disable"):
        await set_chat_flag(chat_id, "antibot", False)
        await message.reply_text("❌ AntiBot **OFF**.")
    else:
        await message.reply_text("Usage: `.antibot on|off`")


@app.on_message(cmd("antilinkstatus"))
@sudo_only
async def antilink_status(client, message: Message):
    cid = message.chat.id
    al = await get_chat_flag(cid, "antilink", False)
    ab = await get_chat_flag(cid, "antibot", False)
    await message.reply_text(
        f"🛡 <b>Status</b>\n"
        f"AntiLink: <b>{'ON' if al else 'OFF'}</b>\n"
        f"AntiBot: <b>{'ON' if ab else 'OFF'}</b>"
    )


@app.on_message(
    filters.group & filters.incoming & ~filters.service,
    group=5,
)
async def antilink_watch(client, message: Message):
    if not message.from_user:
        return
    if _is_priv(message.from_user.id):
        return
    if not await get_chat_flag(message.chat.id, "antilink", False):
        return

    text = message.text or message.caption or ""
    has_link = bool(_LINK_RE.search(text))

    ents = list(message.entities or []) + list(message.caption_entities or [])
    for e in ents:
        if e.type.name in ("URL", "TEXT_LINK"):
            has_link = True
            break

    if not has_link:
        return

    try:
        await message.delete()
    except Exception:
        return
    try:
        await client.send_message(
            message.chat.id,
            f"🔗 Link deleted — {message.from_user.mention}",
            protect_content=True,
        )
    except Exception:
        pass


@app.on_chat_member_updated()
async def antibot_join(client, update: ChatMemberUpdated):
    chat = update.chat
    if not chat:
        return
    if not await get_chat_flag(chat.id, "antibot", False):
        return

    new = update.new_chat_member
    old = update.old_chat_member
    if not new or not new.user or not new.user.is_bot:
        return

    was_out = (not old) or old.status in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED,
    )
    now_in = new.status not in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED,
    )
    if not (was_out and now_in):
        return

    try:
        me = await client.get_me()
        if new.user.id == me.id:
            return
    except Exception:
        pass

    try:
        await client.ban_chat_member(chat.id, new.user.id)
        await client.unban_chat_member(chat.id, new.user.id)
    except Exception:
        try:
            await client.ban_chat_member(chat.id, new.user.id)
        except Exception:
            return
    try:
        await client.send_message(
            chat.id,
            f"🤖 Bot {new.user.mention} removed (AntiBot).",
            protect_content=True,
        )
    except Exception:
        pass
