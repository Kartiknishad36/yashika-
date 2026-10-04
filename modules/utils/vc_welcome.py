"""
VC Welcome — per-group, new members only, shayari + TTS

  .vcwelcome on | off | test | (status)
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
NEW_WINDOW = 7 * 24 * 60 * 60

SHAYARI_WELCOME = [
    "{name}, dil se swagat hai is mehfil mein, yahan dosti aur khushiyan hain.",
    "{name}, aaye ho to dil khush ho gaya — welcome to the VC.",
    "{name}, naye mehmaan, nayi muskaan — is VC mein aapka swagat hai.",
    "{name}, group mein naya rang laaye ho — dil se welcome.",
]


def cmd(*names):
    return filters.command(list(names), prefixes=PREFIXES)


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
        now = int(datetime.now(timezone.utc).timestamp())
        data["vcwelcome_new"][key] = {
            u: ts for u, ts in entry.items() if now - int(ts) < NEW_WINDOW
        }
        _write(data)


async def _is_new_member(chat_id: int, user_id: int) -> bool:
    async with _lock:
        data = _read()
        entry = data.get("vcwelcome_new", {}).get(str(chat_id), {})
        ts = entry.get(str(user_id))
        if not ts:
            return False
        return (int(datetime.now(timezone.utc).timestamp()) - int(ts)) < NEW_WINDOW


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
        data["vcwelcome_done"][key] = done[-300:]
        _write(data)


async def _i_am_admin(client, chat_id: int) -> bool:
    try:
        me = await client.get_me()
        m = await client.get_chat_member(chat_id, me.id)
        return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


async def _make_tts(text: str):
    try:
        import edge_tts

        out = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        out.close()
        await edge_tts.Communicate(text, voice="hi-IN-SwaraNeural").save(out.name)
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
    shayari = random.choice(SHAYARI_WELCOME).format(name=name)
    try:
        await client.send_message(
            chat_id,
            f"**VC Welcome**\n\n{user.mention}\n\n_{shayari}_",
        )
    except Exception:
        pass
    path = await _make_tts(
        f"Namaste {name}. Voice chat mein aapka dil se swagat hai."
    )
    if path:
        try:
            await client.send_voice(chat_id, path, caption=f"Welcome · {name}")
        except Exception:
            pass
        try:
            os.unlink(path)
        except Exception:
            pass


@app.on_message(cmd("vcwelcome", "vcwel", "vwelcome"))
@sudo_only
async def vcwelcome_cmd(client, message: Message):
    if not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.reply_text("Sirf group me use karo.")
        return

    chat_id = message.chat.id
    args = message.command[1:] if len(message.command) > 1 else []
    action = (args[0].lower() if args else "status")

    if action in ("on", "enable", "1"):
        if not await _i_am_admin(client, chat_id):
            await message.reply_text("Pehle is group me **admin** banao.")
            return
        await _set_on(chat_id, True)
        await message.reply_text(
            f"**VC Welcome ON**\nGroup: **{message.chat.title}**\n"
            f"Sirf naye members · pehli VC join"
        )
        return

    if action in ("off", "disable", "0"):
        await _set_on(chat_id, False)
        await message.reply_text(f"**VC Welcome OFF** — {message.chat.title}")
        return

    if action == "test":
        if not await _is_on(chat_id):
            await message.reply_text("Pehle `.vcwelcome on`")
            return
        await _send_welcome(client, chat_id, message.from_user)
        return

    on = await _is_on(chat_id)
    await message.reply_text(
        f"**VC Welcome**\n"
        f"Status: **{'ON' if on else 'OFF'}**\n"
        f"`.vcwelcome on` / `off` / `test`"
    )


@app.on_chat_member_updated()
async def _on_member_join(client, update: ChatMemberUpdated):
    try:
        if not update.new_chat_member or not update.new_chat_member.user:
            return
        if update.new_chat_member.user.is_bot:
            return
        old = update.old_chat_member
        new = update.new_chat_member
        old_status = old.status if old else None
        was_out = old_status in (None, ChatMemberStatus.LEFT, ChatMemberStatus.BANNED)
        now_in = new.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
            ChatMemberStatus.RESTRICTED,
        )
        if was_out and now_in:
            chat_id = update.chat.id
            if await _is_on(chat_id):
                await _mark_new(chat_id, new.user.id)
    except Exception:
        pass


@app.on_raw_update()
async def _on_vc_participant(client, update, users, chats):
    try:
        if type(update).__name__ != "UpdateGroupCallParticipants":
            return
        participants = getattr(update, "participants", None) or []
        chat_id = None
        if chats:
            for cid, chat in chats.items():
                try:
                    chat_id = int(f"-100{cid}") if int(cid) > 0 else int(cid)
                except Exception:
                    chat_id = None
                break
        if chat_id is None or not await _is_on(chat_id):
            return
        if not await _i_am_admin(client, chat_id):
            return
        for p in participants:
            if getattr(p, "left", False):
                continue
            peer = getattr(p, "peer", None)
            user_id = getattr(peer, "user_id", None) if peer else None
            if not user_id:
                continue
            if not await _is_new_member(chat_id, user_id):
                continue
            if await _already_welcomed(chat_id, user_id):
                continue
            try:
                user = await client.get_users(user_id)
            except Exception:
                continue
            if getattr(user, "is_bot", False):
                continue
            await _mark_welcomed(chat_id, user_id)
            await _send_welcome(client, chat_id, user)
            await asyncio.sleep(0.3)
    except Exception:
        pass
