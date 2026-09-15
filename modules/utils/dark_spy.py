"""
Dark-themed intel (REAL Telegram data only).
  .whois .spy .profile .mutual .premiumspy .scamspy ...
  .darklist

Impossible claims (IP, last-seen bypass, device, name history)
→ short honest note, no fake numbers.
"""
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!", "/"]


async def _target_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        arg = message.command[1]
        try:
            if arg.lstrip("-").isdigit():
                return await client.get_users(int(arg))
            return await client.get_users(arg)
        except Exception:
            return None
    return message.from_user


async def _anim_then(message: Message, frames: list[str], final: str, delay: float = 0.45):
    msg = await message.reply_text(f"<code>{frames[0]}</code>")
    for f in frames[1:]:
        await asyncio.sleep(delay)
        try:
            await msg.edit_text(f"<code>{f}</code>")
        except Exception:
            return
    await asyncio.sleep(0.35)
    try:
        await msg.edit_text(final)
    except Exception:
        pass


def _card(title: str, body: str) -> str:
    return (
        f"╔══ ☠️ <b>{title}</b> ══╗\n"
        f"{body}\n"
        f"╚════════════════╝"
    )


@app.on_message(
    filters.command(
        [
            "whois",
            "spy",
            "darkinfo",
            "profile",
            "picspy",
            "botspy",
            "deletedspy",
            "fakespy",
            "premiumspy",
            "verifiedspy",
            "scamspy",
            "contactspy",
            "fulltrace",
        ],
        prefixes=PREFIXES,
    )
)
@sudo_only
async def dark_profile_cmd(client, message: Message):
    frames = [
        "☠️ INIT TRACE…",
        "📡 Linking MTProto…",
        "🔍 Pulling peer…",
        "📥 Parsing user object…",
    ]
    u = await _target_user(client, message)
    if not u:
        await _anim_then(
            message, frames, "❌ Target resolve fail. Reply / id / @username"
        )
        return

    try:
        chat = await client.get_chat(u.id)
    except Exception:
        chat = None

    bio = getattr(chat, "bio", None) or "—"
    un = f"@{u.username}" if u.username else "—"
    body = (
        f"<b>Name:</b> {u.first_name or ''} {u.last_name or ''}\n"
        f"<b>ID:</b> <code>{u.id}</code>\n"
        f"<b>Username:</b> {un}\n"
        f"<b>DC:</b> <code>{getattr(u, 'dc_id', '—')}</code>\n"
        f"<b>Bot:</b> {u.is_bot}\n"
        f"<b>Deleted:</b> {getattr(u, 'is_deleted', False)}\n"
        f"<b>Fake:</b> {getattr(u, 'is_fake', False)}\n"
        f"<b>Scam:</b> {getattr(u, 'is_scam', False)}\n"
        f"<b>Premium:</b> {getattr(u, 'is_premium', False)}\n"
        f"<b>Verified:</b> {getattr(u, 'is_verified', False)}\n"
        f"<b>Restricted:</b> {getattr(u, 'is_restricted', False)}\n"
        f"<b>Bio:</b> {bio}\n"
        f"tg://user?id={u.id}"
    )
    await _anim_then(message, frames, _card("WHOIS / PROFILE", body))

    # optional DP on picspy / fulltrace
    if message.command[0].lower() in ("picspy", "fulltrace", "profile"):
        try:
            async for photo in client.get_chat_photos(u.id, limit=1):
                await client.send_photo(
                    message.chat.id,
                    photo.file_id,
                    caption=f"🖼️ DP — {u.mention}",
                )
                break
        except Exception:
            pass


@app.on_message(filters.command(["mutual", "groupspy", "commonspy"], prefixes=PREFIXES))
@sudo_only
async def mutual_cmd(client, message: Message):
    frames = ["☠️ Mutual scan…", "📡 Common chats…", "📋 Building list…"]
    u = await _target_user(client, message)
    if not u:
        await message.reply_text("Reply / @user / id")
        return
    lines = []
    try:
        async for c in client.get_common_chats(u.id):
            lines.append(f"• {c.title or c.first_name} (<code>{c.id}</code>)")
            if len(lines) >= 25:
                break
    except Exception as e:
        await _anim_then(message, frames, f"❌ <code>{e}</code>")
        return
    body = f"<b>Target:</b> {u.mention}\n\n" + ("\n".join(lines) if lines else "None / hidden")
    await _anim_then(message, frames, _card("MUTUAL / GROUPS", body))


@app.on_message(filters.command(["msgspy", "forwardspy", "edits", "deletespy"], prefixes=PREFIXES))
@sudo_only
async def msgspy_cmd(client, message: Message):
    r = message.reply_to_message
    frames = ["☠️ Message probe…", "📥 Reading flags…"]
    if not r:
        await message.reply_text("Kisi <b>message</b> pe reply + command")
        return
    body = (
        f"<b>Msg ID:</b> <code>{r.id}</code>\n"
        f"<b>Date:</b> <code>{r.date}</code>\n"
        f"<b>Edited:</b> {bool(r.edit_date)} {f'(<code>{r.edit_date}</code>)' if r.edit_date else ''}\n"
        f"<b>Forward:</b> {bool(r.forward_date or r.forward_from or r.forward_from_chat)}\n"
        f"<b>Media:</b> <code>{r.media or '—'}</code>\n"
        f"<b>From:</b> {r.from_user.mention if r.from_user else '—'}"
    )
    if r.forward_from_chat:
        body += f"\n<b>Fwd chat:</b> {r.forward_from_chat.title}"
    await _anim_then(message, frames, _card("MSG SPY", body))


@app.on_message(
    filters.command(
        [
            "lastseen",
            "online",
            "offline",
            "iptrace",
            "location",
            "devicespy",
            "appspy",
            "onlinespy",
            "namespy",
            "usernamespy",
            "historyspy",
            "readspy",
            "typings",
        ],
        prefixes=PREFIXES,
    )
)
@sudo_only
async def dark_impossible_cmd(client, message: Message):
    """Honest dark UI — Telegram does not provide these."""
    cmd = message.command[0].lower()
    frames = ["☠️ Requesting…", "🔐 Server denied…"]
    body = (
        f"<b>Command:</b> <code>{cmd}</code>\n\n"
        "Telegram API <b>nahi deta</b>:\n"
        "• Real IP / GPS\n"
        "• Hidden last-seen bypass\n"
        "• Name/username history\n"
        "• Device / app version of others\n"
        "• Secret typing/read without access\n\n"
        "<i>Use .whois / .mutual / .msgspy for real data.</i>"
    )
    await _anim_then(message, frames, _card("DARK LIMIT", body), 0.4)


@app.on_message(filters.command(["stealth", "darkmode", "ghostspy", "invispy", "nightspy"], prefixes=PREFIXES))
@sudo_only
async def stealth_cmd(client, message: Message):
    frames = ["🌑 Lights off…", "🥷 Stealth…", "👻 Soft ghost…"]
    body = (
        "<b>Theme:</b> Dark / Stealth\n\n"
        "Real ghost read → <code>.ghost</code> / <code>.ghostview</code>\n"
        "Vanish own msgs → <code>.vanish</code>\n"
        "Profile track → <code>.profiletrack</code>"
    )
    await _anim_then(message, frames, _card("STEALTH", body))


@app.on_message(filters.command(["adminspy", "creator", "chattrace", "memberspy", "linkspy"], prefixes=PREFIXES))
@sudo_only
async def chat_dark_cmd(client, message: Message):
    frames = ["☠️ Chat probe…", "📡 getChat…"]
    try:
        chat = await client.get_chat(message.chat.id)
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return
    body = (
        f"<b>Title:</b> {chat.title or chat.first_name}\n"
        f"<b>ID:</b> <code>{chat.id}</code>\n"
        f"<b>Type:</b> <code>{chat.type}</code>\n"
        f"<b>Username:</b> @{chat.username or '—'}\n"
        f"<b>Members:</b> <code>{getattr(chat, 'members_count', '—')}</code>\n"
        f"<b>Verified:</b> {getattr(chat, 'is_verified', False)}\n"
        f"<b>Scam:</b> {getattr(chat, 'is_scam', False)}\n"
    )
    if getattr(chat, "description", None):
        body += f"<b>About:</b> {chat.description[:180]}\n"
    body += "\n<i>Invite link: .invitelink (admin)</i>"
    await _anim_then(message, frames, _card("CHAT TRACE", body))


@app.on_message(filters.command(["darklist", "spylist"], prefixes=PREFIXES))
@sudo_only
async def darklist_cmd(client, message: Message):
    await message.reply_text(
        "☠️ <b>DARK SPY PACK</b>\n"
        "━━━━━━━━━━━━━━\n"
        "<b>Real:</b>\n"
        "<code>.whois .spy .profile .picspy .fulltrace</code>\n"
        "<code>.mutual .groupspy</code>\n"
        "<code>.msgspy .forwardspy .edits</code>\n"
        "<code>.premiumspy .scamspy .botspy</code>\n"
        "<code>.adminspy .chattrace</code>\n\n"
        "<b>Honest limit cards:</b>\n"
        "<code>.iptrace .lastseen .devicespy .namespy</code>\n"
        "━━━━━━━━━━━━━━\n"
        "<i>Premium animation · no fake IP/GPS</i>"
  )
