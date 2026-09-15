"""
SPY 50+ PACK — REAL TELEGRAM API ONLY
Decorator order: @app.on_message → @sudo_only
"""
import asyncio

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from core.clients import app
from modules.owner.sudoers import sudo_only

P = [".", "!", "/"]


async def get_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        arg = message.command[1].lstrip("@")
        try:
            return await client.get_users(
                int(arg) if arg.lstrip("-").isdigit() else arg
            )
        except Exception:
            return None
    return message.from_user


async def anim(message: Message, frames: list, final: str):
    try:
        m = await message.reply_text(
            f"<code>{frames[0]}</code>", parse_mode=ParseMode.HTML
        )
    except Exception:
        m = await message.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(0.35)
        try:
            await m.edit_text(f"<code>{f}</code>", parse_mode=ParseMode.HTML)
        except Exception:
            break
    await asyncio.sleep(0.3)
    try:
        await m.edit_text(
            final, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    except Exception:
        pass


def box(t: str, b: str) -> str:
    return f"╔══ 🕵️ <b>{t}</b> ══╗\n{b}\n╚═══════════╝"


# ---------- 1. WHOIS ----------
@app.on_message(
    filters.command(
        [
            "whois",
            "spy",
            "profile",
            "who",
            "whois2",
            "idinfo",
            "details",
            "trace",
            "intel",
            "whoami",
            "stalk",
            "lookup",
            "whoisinfo",
        ],
        prefixes=P,
    )
)
@sudo_only
async def whois_c(client, message: Message):
    u = await get_user(client, message)
    if not u:
        await message.reply_text("Reply / @username / id do")
        return
    try:
        chat = await client.get_chat(u.id)
    except Exception:
        chat = None
    bio = getattr(chat, "bio", None) if chat else None
    bio = bio or "—"
    b = (
        f"<b>Name:</b> {u.first_name or ''} {u.last_name or ''}\n"
        f"<b>ID:</b> <code>{u.id}</code>\n"
        f"<b>Username:</b> @{u.username or '—'}\n"
        f"<b>DC:</b> <code>{getattr(u, 'dc_id', '—')}</code>\n"
        f"<b>Bot:</b> {u.is_bot}\n"
        f"<b>Premium:</b> {getattr(u, 'is_premium', False)} | "
        f"<b>Verified:</b> {getattr(u, 'is_verified', False)}\n"
        f"<b>Scam:</b> {getattr(u, 'is_scam', False)} | "
        f"<b>Fake:</b> {getattr(u, 'is_fake', False)}\n"
        f"<b>Deleted:</b> {getattr(u, 'is_deleted', False)}\n"
        f"<b>Bio:</b> {str(bio)[:150]}\n"
        f"<a href='tg://user?id={u.id}'>Link</a>"
    )
    await anim(
        message,
        ["🕵️ Scanning…", "📡 Fetching…", "🔍 Parsing…"],
        box("WHOIS", b),
    )


# ---------- 2. DP ----------
@app.on_message(
    filters.command(["picspy", "dp", "getdp", "avatar", "pfp"], prefixes=P)
)
@sudo_only
async def dp_c(client, message: Message):
    u = await get_user(client, message)
    if not u:
        await message.reply_text("Reply / @user / id")
        return
    status = await message.reply_text(
        f"<code>🖼️ DP fetch — {u.first_name or u.id}…</code>",
        parse_mode=ParseMode.HTML,
    )
    c = 0
    try:
        async for p in client.get_chat_photos(u.id, limit=5):
            await client.send_photo(
                message.chat.id,
                p.file_id,
                caption=f"DP {c + 1} — {u.mention}",
            )
            c += 1
        try:
            await status.delete()
        except Exception:
            pass
        if c == 0:
            await message.reply_text("❌ No DP")
    except Exception as e:
        await status.edit_text(f"❌ <code>{e}</code>")


# ---------- 3. FLAGS ----------
@app.on_message(
    filters.command(
        [
            "premiumspy",
            "scamspy",
            "botspy",
            "verifiedspy",
            "fakespy",
            "deletedspy",
            "contactspy",
            "scamcheck",
            "botcheck",
            "flagspy",
        ],
        prefixes=P,
    )
)
@sudo_only
async def flag_c(client, message: Message):
    u = await get_user(client, message)
    if not u:
        await message.reply_text("Reply / @user / id")
        return
    b = (
        f"<b>Target:</b> {u.mention}\n"
        f"<b>Premium:</b> {getattr(u, 'is_premium', False)}\n"
        f"<b>Scam:</b> {getattr(u, 'is_scam', False)}\n"
        f"<b>Fake:</b> {getattr(u, 'is_fake', False)}\n"
        f"<b>Verified:</b> {getattr(u, 'is_verified', False)}\n"
        f"<b>Bot:</b> {u.is_bot}\n"
        f"<b>Deleted:</b> {getattr(u, 'is_deleted', False)}\n"
        f"<b>Contact:</b> {getattr(u, 'is_contact', False)}\n"
        f"<b>Mutual contact:</b> {getattr(u, 'is_mutual_contact', False)}"
    )
    await anim(message, ["🕵️ Flag check…", "📡 Done…"], box("FLAG SPY", b))


# ---------- 4. MUTUAL ----------
@app.on_message(
    filters.command(
        ["mutual", "groupspy", "commonspy", "common", "mutualgroups"],
        prefixes=P,
    )
)
@sudo_only
async def mutual_c(client, message: Message):
    u = await get_user(client, message)
    if not u:
        await message.reply_text("Reply / @user / id")
        return
    lines = []
    try:
        async for ch in client.get_common_chats(u.id):
            lines.append(f"• {ch.title or ch.first_name} (<code>{ch.id}</code>)")
            if len(lines) >= 20:
                break
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return
    b = "\n".join(lines) if lines else "No mutual / hidden"
    await anim(
        message,
        ["🕵️ Mutual scan…", "📡 Common chats…"],
        box(f"MUTUAL — {u.first_name or u.id}", b),
    )


# ---------- 5. MSG ----------
@app.on_message(
    filters.command(
        ["msgspy", "forwardspy", "edits", "fwdspy", "msgs", "mediaspy"],
        prefixes=P,
    )
)
@sudo_only
async def msg_c(client, message: Message):
    r = message.reply_to_message
    if not r:
        await message.reply_text("Message pe **reply** karo")
        return
    b = (
        f"<b>ID:</b> <code>{r.id}</code>\n"
        f"<b>Date:</b> <code>{r.date}</code>\n"
        f"<b>Edited:</b> {bool(r.edit_date)}\n"
        f"<b>Forward:</b> {bool(r.forward_date or r.forward_from or r.forward_from_chat)}\n"
        f"<b>Media:</b> <code>{r.media or 'text'}</code>\n"
        f"<b>From:</b> {r.from_user.mention if r.from_user else '—'}"
    )
    await anim(message, ["🕵️ Msg scan…"], box("MSG SPY", b))


# ---------- 6. CHAT ----------
@app.on_message(
    filters.command(
        [
            "adminspy",
            "chattrace",
            "memberspy",
            "chatspy",
            "darkchat",
        ],
        prefixes=P,
    )
)
@sudo_only
async def chat_c(client, message: Message):
    try:
        ch = await client.get_chat(message.chat.id)
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return
    b = (
        f"<b>Title:</b> {ch.title or ch.first_name}\n"
        f"<b>ID:</b> <code>{ch.id}</code>\n"
        f"<b>Type:</b> <code>{ch.type}</code>\n"
        f"<b>User:</b> @{ch.username or '—'}\n"
        f"<b>Members:</b> <code>{getattr(ch, 'members_count', '—')}</code>"
    )
    await anim(message, ["🕵️ Chat scan…"], box("CHAT TRACE", b))


# ---------- 7. LIMIT + LIST ----------
@app.on_message(
    filters.command(
        [
            "iptrace",
            "lastseen",
            "devicespy",
            "namespy",
            "readspy",
            "stealth",
            "darkmode",
            "ghostspy",
            "darklist",
            "spylist",
        ],
        prefixes=P,
    )
)
@sudo_only
async def limit_c(client, message: Message):
    cmd = message.command[0].lower()
    if cmd in ("darklist", "spylist"):
        await message.reply_text(
            "🕵️ <b>SPY 50+ PACK</b>\n"
            "━━━━━━━━━━\n"
            "<code>.whois .spy .profile .trace .intel .stalk</code>\n"
            "<code>.picspy .dp .getdp .avatar .pfp</code>\n"
            "<code>.premiumspy .scamspy .botspy .flagspy</code>\n"
            "<code>.mutual .groupspy .common</code>\n"
            "<code>.msgspy .forwardspy .edits</code>\n"
            "<code>.adminspy .chattrace .chatspy</code>\n"
            "<code>.iptrace .lastseen .devicespy (limit cards)</code>\n"
            "<code>.stealth .darkmode .ghostspy</code>\n"
            "━━━━━━━━━━\n"
            "<i>Real API only · sudo_only</i>",
            parse_mode=ParseMode.HTML,
        )
        return

    if cmd in ("stealth", "darkmode", "ghostspy"):
        b = (
            "<b>Stealth tips</b>\n"
            "• <code>.ghost</code> / <code>.ghostview</code>\n"
            "• <code>.vanish</code>\n"
            "• <code>.whois</code> · <code>.picspy</code>"
        )
        await anim(
            message,
            ["🌑 Stealth…", "🥷 Ready…"],
            box("STEALTH", b),
        )
        return

    b = (
        f"<b>{cmd}</b> — Telegram API ye data nahi deta.\n"
        "Real: <code>.whois</code> · <code>.mutual</code> · <code>.msgspy</code>"
    )
    await anim(
        message,
        ["🔐 Checking…", "❌ Not available…"],
        box("LIMIT", b),
  )
