"""
Ultra extra pack — real actions only.
Already in other modules (don't duplicate load):
  .id .purge .spam .raid .ban .kick .mute .pin .afk .tagall
  .hack .type .stats .uptime .weather .calc .tr (tools/anims)

Yahan:
  .userinfo .groupinfo .getpic .copycap .ghostview
  .vanishmode .vanish 5s
  .alive2 .speed .repo .owner
  .hack2 .type2 .fakechat (fun)
  .ultralist
"""
import asyncio
import time

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import sudo_only
from config import BOT_NAME, OWNER_ID
from database.mongo import set_feature, get_feature

PREFIXES = [".", "!", "/"]
_START = time.time()


def _who(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return message.from_user


# ---------- INFO ----------

@app.on_message(filters.command(["userinfo", "whois2"], prefixes=PREFIXES))
@sudo_only
async def userinfo_cmd(client, message: Message):
    u = _who(message)
    if not u:
        await message.reply_text("User nahi mila.")
        return
    dc = getattr(u, "dc_id", None) or "—"
    un = f"@{u.username}" if u.username else "—"
    text = (
        "╔══════════════╗\n"
        "║ 👤 <b>USER INFO</b> ║\n"
        "╚══════════════╝\n"
        f"<b>Name:</b> {u.first_name or ''} {u.last_name or ''}\n"
        f"<b>ID:</b> <code>{u.id}</code>\n"
        f"<b>Username:</b> {un}\n"
        f"<b>DC:</b> <code>{dc}</code>\n"
        f"<b>Bot:</b> {'Yes' if u.is_bot else 'No'}\n"
        f"<b>Premium:</b> {'Yes' if getattr(u, 'is_premium', False) else 'No'}\n"
        f"<b>Scam:</b> {'Yes' if getattr(u, 'is_scam', False) else 'No'}\n"
        f"<b>Verified:</b> {'Yes' if getattr(u, 'is_verified', False) else 'No'}\n"
        f"tg://user?id={u.id}"
    )
    await message.reply_text(text)


@app.on_message(filters.command(["groupinfo", "chatinfo2"], prefixes=PREFIXES))
@sudo_only
async def groupinfo_cmd(client, message: Message):
    target = message.chat.id
    if len(message.command) > 1:
        a = message.command[1]
        target = int(a) if a.lstrip("-").isdigit() else a
    try:
        chat = await client.get_chat(target)
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")
        return
    text = (
        "╔══════════════╗\n"
        "║ 👥 <b>CHAT INFO</b> ║\n"
        "╚══════════════╝\n"
        f"<b>Name:</b> {chat.title or chat.first_name}\n"
        f"<b>ID:</b> <code>{chat.id}</code>\n"
        f"<b>Type:</b> <code>{chat.type}</code>\n"
        f"<b>Username:</b> @{chat.username or '—'}\n"
        f"<b>Members:</b> <code>{getattr(chat, 'members_count', '—')}</code>\n"
        f"<b>Verified:</b> {getattr(chat, 'is_verified', False)}\n"
    )
    if getattr(chat, "description", None):
        text += f"\n<b>About:</b> {chat.description[:200]}"
    await message.reply_text(text)


@app.on_message(filters.command("getpic", prefixes=PREFIXES))
@sudo_only
async def getpic_cmd(client, message: Message):
    u = _who(message)
    if not u:
        await message.reply_text("Reply user / khud.")
        return
    try:
        async for photo in client.get_chat_photos(u.id, limit=1):
            await client.send_photo(
                message.chat.id,
                photo.file_id,
                caption=f"🖼 DP — {u.mention}\n<code>{u.id}</code>",
            )
            return
        await message.reply_text("❌ No DP")
    except Exception as e:
        await message.reply_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command("copycap", prefixes=PREFIXES))
@sudo_only
async def copycap_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        await message.reply_text("Media/text pe reply + <code>.copycap</code>")
        return
    try:
        await r.copy(message.chat.id)
    except Exception as e:
        if r.caption:
            await message.reply_text(r.caption)
        else:
            await message.reply_text(f"❌ <code>{e}</code>")


# ---------- GHOST / VANISH ----------

@app.on_message(filters.command(["ghostview", "ghostmode"], prefixes=PREFIXES))
@sudo_only
async def ghostview_cmd(client, message: Message):
    if len(message.command) > 1 and message.command[1].lower() in ("off", "0"):
        await set_feature("ghost_read", False)
        await message.reply_text("❌ GhostView OFF")
        return
    await set_feature("ghost_read", True)
    await message.reply_text(
        "👻 <b>Ghost View ON</b>\n"
        "Is client se read/seen avoid (jab tak modules read na bhejein).\n"
        "Phone app alag device hai — wahan open mat karna.\n"
        "<code>.ghostview off</code>"
    )


@app.on_message(filters.command(["vanishmode", "vanish"], prefixes=PREFIXES))
@sudo_only
async def vanish_cmd(client, message: Message):
    # .vanishmode on/off | .vanish 5s text
    if len(message.command) >= 2 and message.command[1].lower() in ("on", "off"):
        on = message.command[1].lower() == "on"
        await set_feature("vanish_mode", on)
        await message.reply_text(f"💨 Vanish auto-delete: <b>{'ON' if on else 'OFF'}</b>")
        return

    if len(message.command) >= 2 and message.command[1].endswith("s"):
        try:
            sec = max(1, min(int(message.command[1][:-1]), 30))
        except ValueError:
            sec = 5
        text = message.text.split(None, 2)[2] if len(message.command) > 2 else "•"
        msg = await message.reply_text(text)
        await asyncio.sleep(sec)
        try:
            await msg.delete()
            await message.delete()
        except Exception:
            pass
        return

    msg = await message.reply_text("💨 <b>Vanish</b> — 5s me gayab…")
    await asyncio.sleep(5)
    try:
        await msg.delete()
        await message.delete()
    except Exception:
        pass


# ---------- STATUS / BRANDING ----------

@app.on_message(filters.command(["alive2", "aliveu"], prefixes=PREFIXES))
@sudo_only
async def alive2_cmd(client, message: Message):
    me = await client.get_me()
    up = int(time.time() - _START)
    await message.reply_text(
        f"🔥 <b>{BOT_NAME}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Status: <b>ONLINE</b>\n"
        f"User: <code>{me.id}</code>\n"
        f"Uptime: <code>{up}s</code>\n"
        f"Mode: Premium Hybrid\n"
        f"━━━━━━━━━━━━━━\n"
        f"✨ Features loaded"
    )


@app.on_message(filters.command("speed", prefixes=PREFIXES))
@sudo_only
async def speed_cmd(client, message: Message):
    t1 = time.time()
    m = await message.reply_text("⚡ Measuring…")
    ms = (time.time() - t1) * 1000
    await m.edit_text(f"⚡ <b>Response</b>\n<code>{ms:.1f} ms</code>")


@app.on_message(filters.command("repo", prefixes=PREFIXES))
@sudo_only
async def repo_cmd(client, message: Message):
    await message.reply_text(
        "📦 <b>Repo</b>\n"
        "https://github.com/Kartiknishad36/yashika-\n"
        f"Bot: <b>{BOT_NAME}</b>"
    )


@app.on_message(filters.command("owner", prefixes=PREFIXES))
@sudo_only
async def owner_cmd(client, message: Message):
    await message.reply_text(
        f"👑 <b>Owner</b>\n<code>{OWNER_ID}</code>\n"
        f"tg://user?id={OWNER_ID}"
    )


# ---------- FUN ANIM ----------

@app.on_message(filters.command("hack2", prefixes=PREFIXES))
@sudo_only
async def hack2_cmd(client, message: Message):
    frames = [
        "Hacking database…",
        "Accessing nodes…",
        "Bypass security…",
        "✅ Hacked! (Fake) 😂",
    ]
    msg = await message.reply_text(f"<code>{frames[0]}</code>")
    for f in frames[1:]:
        await asyncio.sleep(0.55)
        try:
            await msg.edit_text(f"<code>{f}</code>")
        except Exception:
            break


@app.on_message(filters.command("type2", prefixes=PREFIXES))
@sudo_only
async def type2_cmd(client, message: Message):
    try:
        await client.send_chat_action(message.chat.id, "typing")
    except Exception:
        pass
    await asyncio.sleep(2)
    await message.reply_text("✅ <b>Typing simulation done</b>")


@app.on_message(filters.command("fakechat", prefixes=PREFIXES))
@sudo_only
async def fakechat_cmd(client, message: Message):
    name = "Jaan"
    if message.reply_to_message and message.reply_to_message.from_user:
        name = message.reply_to_message.from_user.first_name or name
    await message.reply_text(
        "💬 <b>Fake Chat</b> (fun)\n"
        "━━━━━━━━━━━━━━\n"
        f"<b>{name}:</b> I love you\n"
        f"<b>You:</b> I love you too {name} ❤️\n"
        "━━━━━━━━━━━━━━"
    )


@app.on_message(filters.command("ultralist", prefixes=PREFIXES))
@sudo_only
async def ultralist_cmd(client, message: Message):
    await message.reply_text(
        "🧿 <b>ULTRA EXTRA</b>\n"
        "━━━━━━━━━━━━━━\n"
        "Info: <code>.userinfo .groupinfo .getpic .copycap</code>\n"
        "Ghost: <code>.ghostview .vanish .vanish 5s hi</code>\n"
        "Status: <code>.alive2 .speed .repo .owner</code>\n"
        "Fun: <code>.hack2 .type2 .fakechat</code>\n"
        "━━━━━━━━━━━━━━\n"
        "<i>Real ban/kick/mute → existing mod modules use karo</i>"
  )
