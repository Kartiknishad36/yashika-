import asyncio
import importlib
import time
from datetime import datetime, timezone

from core.clients import app
from core.call_manager import ensure_started
from core.autodelete import register_trigger_autodelete
from database.mongo import add_chat
from modules.owner.sudoers import load_sudoers, SUDO_USERS
from config import LOG_GROUP_ID, BOT_NAME, OWNER_ID

MODULES = [
    "modules.owner.sudoers",
    "modules.owner.login",
    "modules.owner.pmguard",
    "modules.owner.clone",
    "modules.owner.tracker",
    "modules.owner.raid_spam",
    "modules.owner.ghostmod",
    "modules.owner.secretlog",

    "modules.vc.play",
    "modules.vc.controls",
    "modules.utils.vc_welcome",

    "modules.global_mod.gban",
    "modules.global_mod.gmute",
    "modules.global_mod.gdel",
    "modules.global_mod.warn",
    "modules.global_mod.broadcast",
    "modules.global_mod.chatmod",
    "modules.global_mod.tagall",
    "modules.global_mod.shayari",
    "modules.global_mod.bro",
    "modules.global_mod.welcome",
    "modules.global_mod.antilink",
    "modules.global_mod.antidelete",
    "modules.global_mod.antiflood",
    "modules.global_mod.locks",
    "modules.global_mod.rules",
    "modules.global_mod.nightmode",
    "modules.global_mod.slowmode",
    "modules.global_mod.zombies",
    "modules.global_mod.autokick",
    "modules.global_mod.admin_extra",

    "modules.economy.basic",

    "modules.utils.basics",
    "modules.utils.info",
    "modules.utils.user_scan",
    "modules.utils.mongo_dp",
    "modules.utils.fun",
    "modules.utils.afk",
    "modules.utils.protect",
    "modules.utils.notes",
    "modules.utils.system_cmds",
    "modules.utils.tools",
    "modules.utils.profile_set",
    "modules.utils.fun_text",
    "modules.utils.copy_tools",
    "modules.utils.hashtag",
    "modules.utils.vanish",
    "modules.utils.paste_cmd",
    "modules.utils.reminder",
    "modules.utils.filters_words",
    "modules.utils.qrcode_cmd",
    "modules.utils.stats_cmd",
    "modules.utils.setgroup",
    "modules.utils.telegraph",
    "modules.utils.autojoin",
    "modules.utils.autoreply",

    "modules.media.kang",
    "modules.media.download",
    "modules.media.social",
]

for m in MODULES:
    try:
        importlib.import_module(m)
    except Exception as e:
        print(f"[Userbot] WARNING: could not load '{m}': {type(e).__name__}: {e}")

# chat_id -> last track timestamp (avoid write on every message)
_TRACKED_AT: dict[int, float] = {}
_TRACK_INTERVAL = 3600  # 1 hour


async def track_chats():
    from pyrogram import filters

    @app.on_message(filters.group | filters.private, group=50)
    async def _track(client, message):
        try:
            chat = message.chat
            if not chat:
                return
            now = time.time()
            last = _TRACKED_AT.get(chat.id, 0)
            if now - last < _TRACK_INTERVAL:
                return
            _TRACKED_AT[chat.id] = now
            title = getattr(chat, "title", None) or getattr(chat, "first_name", None) or ""
            await add_chat(chat.id, title)
        except Exception:
            pass


async def _notify_log(text: str):
    if not LOG_GROUP_ID:
        return
    try:
        await app.send_message(LOG_GROUP_ID, text)
    except Exception as e:
        print(f"[Userbot] LOG notify failed: {e}")


async def main():
    await load_sudoers()
    await track_chats()
    register_trigger_autodelete(app)

    try:
        await app.start()
        me = await app.get_me()
        SUDO_USERS.add(me.id)
        if OWNER_ID:
            SUDO_USERS.add(OWNER_ID)
        print(f"[Userbot] Started as {me.first_name} (@{me.username or me.id})")
        print(f"[Userbot] SUDO={sorted(SUDO_USERS)}")
    except Exception as e:
        print(f"[Userbot] FATAL: {e}")
        raise

    # Telegram naye/restart session pe GetMessages flood karta hai — thoda wait
    await asyncio.sleep(3)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    uname = f"@{me.username}" if me.username else "—"
    await _notify_log(
        f"**USERBOT STARTED**\n"
        f"Name: **{me.first_name}**\n"
        f"User: {uname}\n"
        f"ID: `{me.id}`\n"
        f"Bot: **{BOT_NAME or 'Yashika'}**\n"
        f"Time: `{now}`\n\n"
        f"`.help` `.ping` `.login` `.play`"
    )

    # PyTgCalls thoda baad — startup flood se clash kam
    await asyncio.sleep(5)
    try:
        await ensure_started(app)
        print("[Userbot] PyTgCalls ready")
        await _notify_log("VC engine ready")
    except Exception as e:
        print(f"[Userbot] PyTgCalls: {e}")

    print("[Userbot] Ready.")
    await _notify_log(f"**{BOT_NAME or 'Yashika'} READY**")
    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
