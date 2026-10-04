"""
Lightweight user info — NO background trackers (fixes 10–20 min lag / FloodWait).

  .uinfo / .scan  — basic profile report
  .id             — also in basics
"""
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


async def _target_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        q = message.command[1]
        try:
            if q.isdigit() or (q.startswith("-") and q[1:].isdigit()):
                return await client.get_users(int(q))
            return await client.get_users(q)
        except Exception:
            return None
    return message.from_user


@app.on_message(filters.command(["uinfo", "scan", "whois"], prefixes=PREFIXES))
@sudo_only
async def uinfo_cmd(client, message: Message):
    user = await _target_user(client, message)
    if not user:
        await message.reply_text("User nahi mila. Reply / id / @username")
        return

    uname = f"@{user.username}" if user.username else "—"
    name = user.first_name or ""
    if user.last_name:
        name = f"{name} {user.last_name}".strip()

    lines = [
        "**User Info**",
        "━━━━━━━━━━━━",
        f"**Name:** {name}",
        f"**Username:** {uname}",
        f"**ID:** `{user.id}`",
        f"**Bot:** {'Yes' if user.is_bot else 'No'}",
        f"**Premium:** {'Yes' if getattr(user, 'is_premium', False) else 'No'}",
        f"**Scam:** {'Yes' if getattr(user, 'is_scam', False) else 'No'}",
        f"**Fake:** {'Yes' if getattr(user, 'is_fake', False) else 'No'}",
    ]
    if user.dc_id:
        lines.append(f"**DC:** `{user.dc_id}`")

    # Optional: member status in current group (single call, not flood)
    if message.chat and message.chat.type.name in ("GROUP", "SUPERGROUP"):
        try:
            m = await client.get_chat_member(message.chat.id, user.id)
            lines.append(f"**In this chat:** `{m.status}`")
        except Exception:
            lines.append("**In this chat:** not a member / hidden")

    await message.reply_text("\n".join(lines))


@app.on_message(filters.command(["fwdinfo"], prefixes=PREFIXES))
@sudo_only
async def fwdinfo_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        await message.reply_text("Reply to a forwarded message.")
        return
    origin = getattr(r, "forward_origin", None)
    if not origin:
        await message.reply_text("Ye forward nahi hai (ya origin hidden).")
        return
    await message.reply_text(
        f"**Forward origin**\n<code>{type(origin).__name__}</code>\n{origin}"
    )
