"""
Anti-Link + Anti-Bot (per group, userbot `app`).

Commands (sudo / admin-style via sudo_only):
  .antilink on|off     — links auto-delete (+ optional warn)
  .antibot on|off      — new bots kicked / service bot-add deleted
  .antilinkstatus      — current flags for this chat

Needs: delete messages right (and ban/kick for antibot).
"""
import re

from pyrogram import filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus

from core.clients import app
from modules.owner.sudoers import sudo_only, SUDO_USERS
from config import OWNER_ID
from database.mongo import set_chat_flag, get_chat_flag

PREFIXES = [".", "!"]

# t.me / http / www / telegram.me
_LINK_RE = re.compile(
    r"(?i)(https?://|www\.|t\.me/|telegram\.me/|tg://)\S+"
)


def cmd(name):
    return filters.command(name, prefixes=PREFIXES) & filters.group


def _is_priv(uid: int) -> bool:
    return uid == OWNER_ID or uid in SUDO_USERS


# ---------- toggles ----------
@app.on_message(cmd("antilink"))
@sudo_only
async def antilink_toggle(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await get_chat_flag(chat_id, "antilink", False)
        await message.reply_text(
            f"Anti-Link is **{'ON' if on else 'OFF'}** here.\n"
            f"`.antilink on` | `.antilink off`"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_chat_flag(chat_id, "antilink", True)
        await message.reply_text("✅ Anti-Link **ON** — links delete honge.")
    elif arg in ("off", "0", "disable"):
        await set_chat_flag(chat_id, "antilink", False)
        await message.reply_text("❌ Anti-Link **OFF**.")
    else:
        await message.reply_text("Usage: `.antilink on|off`")


@app.on_message(cmd("antibot"))
@sudo_only
async def antibot_toggle(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await get_chat_flag(chat_id, "antibot", False)
        await message.reply_text(
            f"Anti-Bot is **{'ON' if on else 'OFF'}** here.\n"
            f"`.antibot on` | `.antibot off`"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await set_chat_flag(chat_id, "antibot", True)
        await message.reply_text("✅ Anti-Bot **ON** — bots kick / remove.")
    elif arg in ("off", "0", "disable"):
        await set_chat_flag(chat_id, "antibot", False)
        await message.reply_text("❌ Anti-Bot **OFF**.")
    else:
        await message.reply_text("Usage: `.antibot on|off`")


@app.on_message(cmd("antilinkstatus"))
@sudo_only
async def antilink_status(client, message: Message):
    cid = message.chat.id
    al = await get_chat_flag(cid, "antilink", False)
    ab = await get_chat_flag(cid, "antibot", False)
    await message.reply_text(
        f"🛡 <b>Status</b> for this chat\n\n"
        f"Anti-Link: <b>{'ON' if al else 'OFF'}</b>\n"
        f"Anti-Bot: <b>{'ON' if ab else 'OFF'}</b>"
    )


# ---------- delete links ----------
@app.on_message(
    filters.group & filters.incoming & \~filters.service,
    group=8,
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
    if not has_link and message.entities:
        for e in message.entities:
            if e.type.name in ("URL", "TEXT_LINK"):
                has_link = True
                break
    if not has_link and message.caption_entities:
        for e in message.caption_entities:
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
        warn = await message.reply_text(
            f"🔗 Link not allowed, {message.from_user.mention}."
        )
        # optional: auto-delete warn after few sec — skip to keep simple
    except Exception:
        pass


# ---------- kick bots on join ----------
@app.on_chat_member_updated()
async def antibot_join(client, update: ChatMemberUpdated):
    chat = update.chat
    if not chat or not getattr(chat, "id", None):
        return
    if not await get_chat_flag(chat.id, "antibot", False):
        return

    new = update.new_chat_member
    old = update.old_chat_member
    if not new or not new.user:
        return
    if not new.user.is_bot:
        return

    # joined / added
    was_in = old and old.status not in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED,
    )
    now_in = new.status not in (
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED,
    )
    if not (now_in and not was_in):
        return

    # don't kick ourselves
    try:
        me = await client.get_me()
        if new.user.id == me.id:
            return
    except Exception:
        pass

    try:
        await client.ban_chat_member(chat.id, new.user.id)
        await client.unban_chat_member(chat.id, new.user.id)  # kick style
    except Exception:
        try:
            await client.ban_chat_member(chat.id, new.user.id)
        except Exception:
            return
    try:
        await client.send_message(
            chat.id,
            f"🤖 Bot {new.user.mention} removed (Anti-Bot ON).",
        )
    except Exception:
        pass
