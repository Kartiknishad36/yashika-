"""
☠️ DARK SPY 50+ — REAL DATA ONLY
"""
import asyncio

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from core.clients import app
from modules.owner.sudoers import sudo_only

P = [".", "!", "/"]


async def get_target(client, message: Message):
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


async def dark_anim(message: Message, frames, final):
    try:
        m = await message.reply_text(
            f"<code>{frames[0]}</code>", parse_mode=ParseMode.HTML
        )
    except Exception:
        m = await message.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(0.4)
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
    return m


def box(title, body):
    return f"╔══ ☠️ <b>{title}</b> ══╗\n{body}\n╚════════════════╝"


# ================= REAL INTEL =================

@app.on_message(
    filters.command(
        [
            "whois",
            "spy",
            "darkinfo",
            "profile",
            "who",
            "details",
            "fulltrace",
            "trace",
            "stalk",
            "intel",
            "userinfo2",
            "realinfo",
            "deepinfo",
        ],
        prefixes=P,
    )
)
@sudo_only
async def whois_cmd(client, message: Message):
    u = await get_target(client, message)
    if not u:
        await message.reply_text("❌ Reply / @username / id")
        return

    try:
        chat = await client.get_chat(u.id)
    except Exception:
        chat = None

    bio = getattr(chat, "bio", None) or "—"
    body = (
        f"<b>Name:</b> {u.first_name or ''} {u.last_name or ''}\n"
        f"<b>ID:</b> <code>{u.id}</code>\n"
        f"<b>User:</b> @{u.username or '—'}\n"
        f"<b>DC:</b> <code>{getattr(u, 'dc_id', '—')}</code>\n"
        f"<b>Bot:</b> {u.is_bot} | <b>Deleted:</b> {getattr(u, 'is_deleted', False)}\n"
        f"<b>Fake:</b> {getattr(u, 'is_fake', False)} | "
        f"<b>Scam:</b> {getattr(u, 'is_scam', False)}\n"
        f"<b>Premium:</b> {getattr(u, 'is_premium', False)} | "
        f"<b>Verified:</b> {getattr(u, 'is_verified', False)}\n"
        f"<b>Bio:</b> {str(bio)[:180]}\n"
        f"<a href='tg://user?id={u.id}'>Profile Link</a>"
    )
    await dark_anim(
        message,
        ["☠️ TRACE START…", "📡 MTProto Connect…", "🔍 Fetching Peer…"],
        box(f"WHOIS · {message.command[0].upper()}", body),
    )

    if message.command[0].lower() in ("profile", "fulltrace", "whois", "deepinfo"):
        try:
            async for p in client.get_chat_photos(u.id, limit=1):
                await client.send_photo(
                    message.chat.id,
                    p.file_id,
                    caption=f"🖼️ DP — {u.first_name or u.id}",
                )
                break
        except Exception:
            pass


@app.on_message(
    filters.command(["picspy", "dp", "getdp", "avatar", "pfp"], prefixes=P)
)
@sudo_only
async def picspy_cmd(client, message: Message):
    u = await get_target(client, message)
    if not u:
        await message.reply_text("Reply / @user / id")
        return
    status = await message.reply_text(
        f"🖼️ <code>Fetching DP — {u.first_name or u.id}…</code>",
        parse_mode=ParseMode.HTML,
    )
    try:
        count = 0
        async for p in client.get_chat_photos(u.id, limit=5):
            await client.send_photo(
                message.chat.id,
                p.file_id,
                caption=f"DP {count + 1} — {u.mention}",
            )
            count += 1
        try:
            await status.delete()
        except Exception:
            pass
        if count == 0:
            await message.reply_text("❌ No DP found")
    except Exception as e:
        await status.edit_text(f"❌ <code>{e}</code>")


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
            "flagspy",
        ],
        prefixes=P,
    )
)
@sudo_only
async def flagspy_cmd(client, message: Message):
    u = await get_target(client, message)
    if not u:
        await message.reply_text("Reply / @user / id")
        return
    body = (
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
    await dark_anim(
        message,
        ["☠️ Flag scan…", "📡 Checking flags…"],
        box("FLAG SPY", body),
    )


@app.on_message(
    filters.command(
        ["mutual", "groupspy", "commonspy", "common", "mutualgroups"],
        prefixes=P,
    )
)
@sudo_only
async def mutual_cmd(client, message: Message):
    u = await get_target(client, message)
    if not u:
        await message.reply_text("Reply / @user / id")
        return
    lines = []
    try:
        async for c in client.get_common_chats(u.id):
            lines.append(f"• {c.title or c.first_name} — <code>{c.id}</code>")
            if len(lines) >= 20:
                break
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return
    body = f"<b>Target:</b> {u.mention}\n\n" + (
        "\n".join(lines) if lines else "No mutual / Hidden"
    )
    await dark_anim(
        message,
        ["☠️ Mutual scan…", "📡 Common chats…"],
        box("MUTUAL SPY", body),
    )


@app.on_message(
    filters.command(
        ["msgspy", "forwardspy", "edits", "deletespy", "msgs", "fwdspy"],
        prefixes=P,
    )
)
@sudo_only
async def msgspy_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        await message.reply_text("Message pe **reply** karo")
        return
    fwd = "—"
    if r.forward_from_chat:
        fwd = r.forward_from_chat.title or str(r.forward_from_chat.id)
    elif r.forward_from:
        fwd = r.forward_from.first_name or str(r.forward_from.id)
    body = (
        f"<b>Msg ID:</b> <code>{r.id}</code>\n"
        f"<b>Date:</b> <code>{r.date}</code>\n"
        f"<b>Edited:</b> {bool(r.edit_date)}"
        f"{f' (<code>{r.edit_date}</code>)' if r.edit_date else ''}\n"
        f"<b>Forwarded:</b> {bool(r.forward_date or r.forward_from or r.forward_from_chat)}\n"
        f"<b>Media:</b> <code>{r.media or 'text'}</code>\n"
        f"<b>From:</b> {r.from_user.mention if r.from_user else '—'}\n"
        f"<b>Fwd From:</b> {fwd}"
    )
    await dark_anim(
        message,
        ["☠️ Msg probe…", "📥 Flags…"],
        box("MSG SPY", body),
    )


@app.on_message(
    filters.command(
        [
            "adminspy",
            "creator",
            "chattrace",
            "memberspy",
            "linkspy",
            "darkchat",
        ],
        prefixes=P,
    )
)
@sudo_only
async def chatspy_cmd(client, message: Message):
    try:
        chat = await client.get_chat(message.chat.id)
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return
    desc = getattr(chat, "description", None) or "—"
    body = (
        f"<b>Title:</b> {chat.title or chat.first_name}\n"
        f"<b>ID:</b> <code>{chat.id}</code>\n"
        f"<b>Type:</b> <code>{chat.type}</code>\n"
        f"<b>Username:</b> @{chat.username or '—'}\n"
        f"<b>Members:</b> <code>{getattr(chat, 'members_count', '—')}</code>\n"
        f"<b>About:</b> {str(desc)[:150]}"
    )
    await dark_anim(
        message,
        ["☠️ Chat trace…", "📡 getChat…"],
        box("CHAT TRACE", body),
    )


# ================= LIMIT CARDS =================

@app.on_message(
    filters.command(
        [
            "iptrace",
            "lastseen",
            "online",
            "offline",
            "devicespy",
            "appspy",
            "onlinespy",
            "namespy",
            "usernamespy",
            "historyspy",
            "readspy",
            "typings",
            "location",
            "ip",
            "gps",
            "device",
            "os",
            "appver",
            "seen",
        ],
        prefixes=P,
    )
)
@sudo_only
async def impossible_cmd(client, message: Message):
    cmd = message.command[0]
    body = (
        f"<b>Cmd:</b> <code>{cmd}</code>\n\n"
        "❌ Telegram API <b>ye nahi deta:</b>\n"
        "• Real IP / GPS\n"
        "• Hidden Last Seen bypass\n"
        "• Name history\n"
        "• Others ka Device/OS\n"
        "• Secret read/typing hack\n\n"
        "<i>Real: .whois · .mutual · .msgspy</i>"
    )
    await dark_anim(
        message,
        ["☠️ Requesting…", "🔐 Denied by Server…"],
        box("DARK LIMIT", body),
    )


@app.on_message(
    filters.command(
        ["stealth", "darkmode", "ghostspy", "invispy", "nightspy", "dark"],
        prefixes=P,
    )
)
@sudo_only
async def stealth_cmd(client, message: Message):
    body = (
        "<b>Dark Theme</b>\n\n"
        "• Ghost → <code>.ghostview</code> / <code>.ghost</code>\n"
        "• Vanish → <code>.vanish</code>\n"
        "• Profile → <code>.whois</code>\n"
        "• DP → <code>.picspy</code>"
    )
    await dark_anim(
        message,
        ["🌑 Lights Off…", "🥷 Stealth Mode…"],
        box("STEALTH", body),
    )


@app.on_message(
    filters.command(["darklist", "spylist", "darkhelp", "spyhelp"], prefixes=P)
)
@sudo_only
async def darklist_cmd(client, message: Message):
    await message.reply_text(
        "☠️ <b>DARK SPY 50+ PACK</b>\n"
        "━━━━━━━━━━━━━━━\n"
        "<b>REAL:</b>\n"
        "<code>.whois .spy .profile .fulltrace .trace</code>\n"
        "<code>.picspy .dp .getdp</code>\n"
        "<code>.premiumspy .scamspy .botspy .flagspy</code>\n"
        "<code>.mutual .groupspy .common</code>\n"
        "<code>.msgspy .forwardspy .edits</code>\n"
        "<code>.adminspy .chattrace .darkchat</code>\n\n"
        "<b>LIMIT CARDS:</b>\n"
        "<code>.iptrace .lastseen .devicespy .namespy</code>\n"
        "<code>.stealth .darkmode .ghostspy</code>\n\n"
        "<code>.darklist</code>\n"
        "━━━━━━━━━━━━━━━\n"
        "<i>No fake IP — pure API + premium anim</i>",
        parse_mode=ParseMode.HTML,
       )
