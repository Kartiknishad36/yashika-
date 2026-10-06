"""
PM Guard — no group link / no verify.
Incoming DM → stylish warning (max 5) → REPORT + BLOCK.
Owner / sudo free. Commands: .approve .unapprove .approved .pmwarns
"""
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID, LOG_GROUP_ID
from modules.owner.sudoers import SUDO_USERS, sudo_only, ub_cmd
from database.mongo import approve_pm, unapprove_pm, get_approved_pm

PM_WARNS: dict[int, int] = {}
MAX_WARNS = 5

WARN_TEXT = (
    "<b>╔══════════════════════╗</b>\n"
    "<b>║   ⚠️  PM SECURITY  ⚠️   ║</b>\n"
    "<b>╚══════════════════════╝</b>\n\n"
    "<b>Bina permission DM mat karo.</b>\n"
    "Owner busy hai — spam mat bhejo.\n\n"
    "⚠️ Warning: <b>{warns}/{max_warns}</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "{bar}\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "<i>{max_warns} warning ke baad</i>\n"
    "🚫 <b>REPORT + BLOCK</b> automatic.\n\n"
    "Zaroori baat hai to wait —\n"
    "owner khud reply karega."
)

BLOCK_TEXT = (
    "<b>╔══════════════════════╗</b>\n"
    "<b>║   🚫  BLOCKED  🚫   ║</b>\n"
    "<b>╚══════════════════════╝</b>\n\n"
    "{max_warns} warnings complete.\n"
    "Spam <b>REPORT</b> + <b>BLOCK</b>.\n\n"
    "<i>Ab message nahi bhej sakte.</i>"
)


def _bar(warns: int, max_w: int = MAX_WARNS) -> str:
    filled = "█" * min(warns, max_w)
    empty = "░" * max(0, max_w - warns)
    return f"{filled}{empty}  {warns}/{max_w}"


async def _notify_owner(client, user, warns: int, blocked: bool = False):
    name = getattr(user, "first_name", "?") or "?"
    uname = f"@{user.username}" if getattr(user, "username", None) else "—"
    uid = user.id
    if blocked:
        text = (
            f"<b>PM GUARD — BLOCKED</b>\n"
            f"User: <b>{name}</b> ({uname})\n"
            f"ID: <code>{uid}</code>\n"
            f"Warns: {MAX_WARNS}/{MAX_WARNS}\n"
            f"Action: report + block"
        )
    else:
        text = (
            f"<b>PM GUARD — WARN</b>\n"
            f"User: <b>{name}</b> ({uname})\n"
            f"ID: <code>{uid}</code>\n"
            f"Warns: {warns}/{MAX_WARNS}"
        )
    targets = []
    if LOG_GROUP_ID:
        targets.append(LOG_GROUP_ID)
    targets.append("me")
    for t in targets:
        try:
            await client.send_message(t, text)
        except Exception:
            pass


async def _report_spam(client, user_id: int, message: Message):
    """Best-effort spam report."""
    try:
        await client.report(chat_id=user_id, message_ids=message.id)
        return
    except Exception:
        pass
    try:
        from pyrogram.raw.functions.messages import Report
        from pyrogram.raw.types import InputReportReasonSpam

        await client.invoke(
            Report(
                peer=await client.resolve_peer(user_id),
                id=[message.id],
                reason=InputReportReasonSpam(),
                message="PM spam after 5 warnings",
            )
        )
    except Exception as e:
        print(f"[pmguard] report fail: {e}")


@app.on_message(
    filters.private & filters.incoming & ~filters.bot & ~filters.service,
    group=10,
)
async def pmguard(client, message: Message):
    user = message.from_user
    if not user:
        return
    user_id = user.id

    if user_id == OWNER_ID or user_id in SUDO_USERS:
        return

    try:
        approved = await get_approved_pm()
        if user_id in approved:
            return
    except Exception:
        pass

    PM_WARNS[user_id] = PM_WARNS.get(user_id, 0) + 1
    warns = PM_WARNS[user_id]

    # 5th warn → report + block
    if warns >= MAX_WARNS:
        try:
            await message.reply_text(BLOCK_TEXT.format(max_warns=MAX_WARNS))
        except Exception:
            pass
        await _report_spam(client, user_id, message)
        try:
            await client.block_user(user_id)
        except Exception as e:
            print(f"[pmguard] block fail: {e}")
        await _notify_owner(client, user, warns, blocked=True)
        PM_WARNS.pop(user_id, None)
        return

    text = WARN_TEXT.format(
        warns=warns,
        max_warns=MAX_WARNS,
        bar=_bar(warns),
    )
    try:
        await message.reply_text(text)
    except Exception as e:
        print(f"[pmguard] reply fail: {e}")
    await _notify_owner(client, user, warns, blocked=False)


def _target_from(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        return u.id, u.first_name or str(u.id)
    parts = (message.text or "").split()
    if len(parts) > 1:
        try:
            return int(parts[1]), parts[1]
        except ValueError:
            return None, None
    return None, None


@app.on_message(ub_cmd("approve"))
@sudo_only
async def approve_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply ya <code>.approve id</code>")
        return
    await approve_pm(target)
    PM_WARNS.pop(target, None)
    try:
        await client.unblock_user(target)
    except Exception:
        pass
    await message.reply_text(f"✅ <b>{name}</b> PM approved.")


@app.on_message(ub_cmd("unapprove"))
@sudo_only
async def unapprove_cmd(client, message: Message):
    target, name = _target_from(message)
    if not target:
        await message.reply_text("Reply ya <code>.unapprove id</code>")
        return
    await unapprove_pm(target)
    await message.reply_text(f"✅ <b>{name}</b> unapproved.")


@app.on_message(ub_cmd("approved"))
@sudo_only
async def approved_cmd(client, message: Message):
    approved = await get_approved_pm()
    if not approved:
        await message.reply_text("Koi approved PM user nahi.")
        return
    lines = "\n".join(f"• <code>{uid}</code>" for uid in approved)
    await message.reply_text(f"✅ <b>PM Approved</b>\n\n{lines}")


@app.on_message(ub_cmd("pmwarns", "warns_pm"))
@sudo_only
async def pmwarns_cmd(client, message: Message):
    if not PM_WARNS:
        await message.reply_text("Koi active PM warn nahi.")
        return
    lines = "\n".join(
        f"• <code>{uid}</code> — {w}/{MAX_WARNS}" for uid, w in PM_WARNS.items()
    )
    await message.reply_text(f"⚠️ <b>PM Warns</b>\n\n{lines}")
