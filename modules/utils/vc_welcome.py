"""
🎙️ VC WELCOME — per-group, NEW members only, shayari + TTS

  .vcwelcome on     → is group me ON (default sab OFF)
  .vcwelcome off    → is group me OFF
  .vcwelcome        → status
  .vcwelcome test   → test welcome (apne pe)

Rules:
  • Sirf us group me jahan command se ON kiya
  • Account admin hona chahiye
  • Sirf NAYA group member → pehli baar VC join pe welcome
  • Purane members / baar-baar VC join → IGNORE
  • Premium shayari style + TTS voice
"""
import asyncio
import os
import random
import tempfile
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus, ChatType

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import get_chat_flag, set_chat_flag, _read, _write, _lock

PREFIXES = [".", "!"]

# Naya member kitne time tak "new" maana jaye (seconds) — 7 days
NEW_WINDOW = 7 * 24 * 60 * 60

SHAYARI_WELCOME = [
    "{name}, dil se swagat hai is mehfil mein,
Yahan dosti hai, yahan khushiyan hain,
Voice chat ki is shaan mein,
Aapka aana hai ek naya samaa.",
    "{name}, aaye ho to dil khush ho gaya,
VC ki mehfil mein rang aa gaya,
Shayari ke andaaz mein kehna hai yeh,
Welcome, yahan tumhara intezaar tha.",
    "{name}, naye mehmaan, nayi muskaan,
Is group ki VC mein aapka swagat hai,
Hasi khushi ke saath milo sabse,
Yahan dil se pyar banta hai.",
    "{name}, chand si muskaan leke aaye ho,
Voice chat mein roshan kar diya mahol,
Shukriya is pyaare saath ke liye,
Welcome to the vibe, dil se.",
    "{name}, ek naya sitara chamka hai,
Is VC ke aasmaan mein,
Dil se kehte hain — swagat hai,
Baithe raho, maza lena yaar.",
    "{name}, group mein naya rang laaye ho,
VC join karke mehfil sajaayi,
Shayari ke alfaaz se welcome,
Khush raho, yahan ghar sa mehsoos karo.",
    "{name}, aawaaz se pehchaan hoti hai,
Welcome to this voice mehfil,
Dosti, hasi, aur acchi baatein,
Yahan sab milke banate hain yaadein.",
    "{name}, nayi shuruaat, naya josh,
VC mein aana — dil jeet liya,
Premium style mein swagat hai aapka,
Enjoy the call, dil se welcome.",
]


def cmd(*names):
    return filters.command(list(names), prefixes=PREFIXES)


# ───────────── storage helpers ─────────────
async def _is_on(chat_id: int) -> bool:
    return bool(await get_chat_flag(chat_id, "vcwelcome", False))


async def _set_on(chat_id: int, value: bool):
    await set_chat_flag(chat_id, "vcwelcome", bool(value))


async def _mark_new(chat_id: int, user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("vcwelcome_new", {})
        key = str(chat_id)
        entry = data["vcwelcome_new"].setdefault(key, {})
        entry[str(user_id)] = int(datetime.now(timezone.utc).timestamp())
        # prune old
        now = int(datetime.now(timezone.utc).timestamp())
        data["vcwelcome_new"][key] = {
            u: ts
            for u, ts in entry.items()
            if now - int(ts) < NEW_WINDOW
        }
        _write(data)


async def _is_new_member(chat_id: int, user_id: int) -> bool:
    async with _lock:
        data = _read()
        entry = data.get("vcwelcome_new", {}).get(str(chat_id), {})
        ts = entry.get(str(user_id))
        if not ts:
            return False
        now = int(datetime.now(timezone.utc).timestamp())
        return (now - int(ts)) < NEW_WINDOW


async def _already_welcomed(chat_id: int, user_id: int) -> bool:
    async with _lock:
        data = _read()
        done = data.get("vcwelcome_done", {}).get(str(chat_id), [])
        return user_id in done or str(user_id) in [str(x) for x in done]


async def _mark_welcomed(chat_id: int, user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("vcwelcome_done", {})
        key = str(chat_id)
        done = data["vcwelcome_done"].setdefault(key, [])
        if user_id not in done:
            done.append(user_id)
        data["vcwelcome_done"][key] = done[-500:]
        _write(data)


async def _i_am_admin(client, chat_id: int) -> bool:
    try:
        me = await client.get_me()
        m = await client.get_chat_member(chat_id, me.id)
        return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


def _pick_shayari(name: str) -> str:
    return random.choice(SHAYARI_WELCOME).format(name=name)


async def _make_tts(text: str) -> str | None:
    """edge-tts → mp3 path, ya None."""
    try:
        import edge_tts

        out = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        out.close()
        # Hindi neural voice
        communicate = edge_tts.Communicate(text, voice="hi-IN-SwaraNeural")
        await communicate.save(out.name)
        return out.name
    except Exception:
        try:
            from gtts import gTTS

            out = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            out.close()
            gTTS(text=text, lang="hi").save(out.name)
            return out.name
        except Exception:
            return None


async def _send_welcome(client, chat_id: int, user):
    name = (user.first_name or "Dost").strip()
    mention = user.mention
    shayari = _pick_shayari(name)

    # Premium text
    caption = (
        "✨━━━━━━━━━━━━━━━━━━✨\n"
        f"🎙️ <b>VC WELCOME</b> 🎙️\n"
        "✨━━━━━━━━━━━━━━━━━━✨\n\n"
        f"👋 {mention}\n\n"
        f"<i>{shayari}</i>\n\n"
        "💜 <b>Premium Shayari Welcome</b>\n"
        "✨━━━━━━━━━━━━━━━━━━✨"
    )

    try:
        await client.send_message(chat_id, caption)
    except Exception:
        pass

    # TTS voice
    tts_text = (
        f"Namaste {name}. "
        f"Voice chat mein aapka dil se swagat hai. "
        f"Khush raho, maze lo, dosti nibhao."
    )
    path = await _make_tts(tts_text)
    if path:
        try:
            await client.send_voice(
                chat_id,
                path,
                caption=f"🔊 TTS Welcome · {mention}",
            )
        except Exception:
            pass
        try:
            os.unlink(path)
        except Exception:
            pass


# ───────────── commands ─────────────
@app.on_message(cmd("vcwelcome", "vcwel", "vwelcome"))
@sudo_only
async def vcwelcome_cmd(client, message: Message):
    if not message.chat or message.chat.type not in (
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    ):
        await message.reply_text("❌ Sirf group me use karo.")
        return

    chat_id = message.chat.id
    args = message.command[1:] if len(message.command) > 1 else []
    action = (args[0].lower() if args else "status")

    if action in ("on", "enable", "start", "1", "true"):
        if not await _i_am_admin(client, chat_id):
            await message.reply_text(
                "❌ Pehle is group me <b>admin</b> banao userbot account ko."
            )
            return
        await _set_on(chat_id, True)
        await message.reply_text(
            "🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢\n"
            "✅ <b>VC WELCOME · ON</b>\n"
            "🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢\n\n"
            f"📍 Group: <b>{message.chat.title}</b>\n"
            "✨ Sirf <b>naye members</b> ka\n"
            "🎙️ Pehli baar VC join pe\n"
            "📜 Shayari + 🔊 TTS welcome\n"
            "🚫 Purane members ignore\n\n"
            "💜 Premium mode active"
        )
        return

    if action in ("off", "disable", "stop", "0", "false"):
        await _set_on(chat_id, False)
        await message.reply_text(
            "🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴\n"
            "⏹ <b>VC WELCOME · OFF</b>\n"
            "🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴\n\n"
            f"📍 Group: <b>{message.chat.title}</b>\n"
            "Is group me ab welcome nahi hoga."
        )
        return

    if action in ("test", "demo"):
        if not await _is_on(chat_id):
            await message.reply_text("Pehle <code>.vcwelcome on</code> karo.")
            return
        u = message.from_user
        await message.reply_text("🧪 Test welcome bhej raha hoon…")
        await _send_welcome(client, chat_id, u)
        return

    # status
    on = await _is_on(chat_id)
    admin = await _i_am_admin(client, chat_id)
    await message.reply_text(
        "🎙️━━━━━━━━━━━━━━━━━━🎙️\n"
        "💜 <b>VC WELCOME STATUS</b>\n"
        "🎙️━━━━━━━━━━━━━━━━━━🎙️\n\n"
        f"📍 Group: <b>{message.chat.title}</b>\n"
        f"🔘 Status: <b>{'🟢 ON' if on else '🔴 OFF'}</b>\n"
        f"👑 Admin: <b>{'Yes' if admin else 'No'}</b>\n\n"
        "📌 Commands:\n"
        "🟢 <code>.vcwelcome on</code>\n"
        "🔴 <code>.vcwelcome off</code>\n"
        "🧪 <code>.vcwelcome test</code>\n\n"
        "✨ Naya member + pehli VC join = Shayari + TTS\n"
        "🚫 Default: sab groups OFF"
    )


# ───────────── track NEW group members ─────────────
@app.on_chat_member_updated()
async def _on_member_join(client, update: ChatMemberUpdated):
    try:
        if not update.new_chat_member or not update.new_chat_member.user:
            return
        if update.new_chat_member.user.is_bot:
            return

        old = update.old_chat_member
        new = update.new_chat_member
        # joined: was not member → now member/admin
        old_status = old.status if old else None
        new_status = new.status

        was_out = old_status in (
            None,
            ChatMemberStatus.LEFT,
            ChatMemberStatus.BANNED,
        ) or (
            old_status == ChatMemberStatus.RESTRICTED
            and not getattr(old, "is_member", True)
        )
        now_in = new_status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
            ChatMemberStatus.RESTRICTED,
        )

        if was_out and now_in:
            chat_id = update.chat.id
            if not await _is_on(chat_id):
                return
            await _mark_new(chat_id, new.user.id)
    except Exception:
        pass


# ───────────── VC participant join (raw) ─────────────
@app.on_raw_update()
async def _on_vc_participant(client, update, users, chats):
    """UpdateGroupCallParticipants → naya VC join detect."""
    try:
        name = type(update).__name__
        if name != "UpdateGroupCallParticipants":
            return

        participants = getattr(update, "participants", None) or []
        # find chat_id from chats dict / peer
        chat_id = None
        call = getattr(update, "call", None)
        # try resolve chat from chats
        if chats:
            for cid, chat in chats.items():
                # group call updates often key by channel id
                try:
                    chat_id = int(f"-100{cid}") if cid > 0 else int(cid)
                except Exception:
                    chat_id = cid
                break

        if chat_id is None:
            # fallback: cannot resolve
            return

        if not await _is_on(chat_id):
            return
        if not await _i_am_admin(client, chat_id):
            return

        for p in participants:
            # left?
            if getattr(p, "left", False):
                continue
            peer = getattr(p, "peer", None)
            user_id = None
            if peer is not None:
                user_id = getattr(peer, "user_id", None)
            if not user_id and users:
                # first user in map
                pass
            if not user_id:
                continue

            # only NEW members, not already welcomed
            if not await _is_new_member(chat_id, user_id):
                continue
            if await _already_welcomed(chat_id, user_id):
                continue

            try:
                user = await client.get_users(user_id)
            except Exception:
                continue
            if user.is_bot:
                continue

            await _mark_welcomed(chat_id, user_id)
            await _send_welcome(client, chat_id, user)
            await asyncio.sleep(0.5)
    except Exception:
        pass


# ───────────── fallback: new member pehli message + VC context ─────────────
# Agar raw VC update miss ho jaye, pehli baar naya member message kare
# aur chat me video_chat active ho to bhi ek baar welcome (optional soft)
@app.on_message(
    filters.group & filters.incoming & ~filters.bot & ~filters.service,
    group=40,
)
async def _soft_fallback_welcome(client, message: Message):
    try:
        if not message.from_user or not message.chat:
            return
        chat_id = message.chat.id
        uid = message.from_user.id

        if not await _is_on(chat_id):
            return
        if not await _is_new_member(chat_id, uid):
            return
        if await _already_welcomed(chat_id, uid):
            return

        # sirf tab jab group me video chat active ho
        chat = message.chat
        vc_active = bool(
            getattr(chat, "video_chat", None)
            or getattr(chat, "voice_chat", None)
        )
        # Pyrogram may not always fill this; try get_chat
        if not vc_active:
            try:
                full = await client.get_chat(chat_id)
                vc_active = bool(
                    getattr(full, "video_chat", None)
                    or getattr(getattr(full, "raw", None), "call", None)
                )
            except Exception:
                vc_active = False

        if not vc_active:
            return

        await _mark_welcomed(chat_id, uid)
        await _send_welcome(client, chat_id, message.from_user)
    except Exception:
        pass
