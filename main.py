import asyncio
import importlib
import time
from datetime import datetime, timezone

from core.clients import app
from core.call_manager import ensure_started
from core.autodelete import register_trigger_autodelete
from database.mongo import add_chat
from modules.owner.sudoers import load_sudoers, SUDO_USERS, set_me_id
from config import LOG_GROUP_ID, BOT_NAME, OWNER_ID

MODULES = [
    "modules.owner.sudoers",
    "modules.owner.login",
    "modules.owner.session_manager",
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
    "modules.utils.dark_spy",
    "modules.utils.spy_pack",
    "modules.utils.voice",

    "modules.media.kang",
    "modules.media.download",
    "modules.media.social",
]

loaded = 0
for m in MODULES:
    try:
        importlib.import_module(m)
        loaded += 1
    except Exception as e:
        print(f"[Userbot] WARN load {m}: {type(e).__name__}: {e}")
print(f"[Userbot] Modules loaded: {loaded}/{len(MODULES)}")

_TRACKED_AT: dict = {}
_TRACK_INTERVAL = 3600


async def track_chats():
    from pyrogram import filters

    @app.on_message(filters.group | filters.private, group=50)
    async def _track(client, message):
        try:
            chat = message.chat
            if not chat:
                return
            now = time.time()
            if now - _TRACKED_AT.get(chat.id, 0) < _TRACK_INTERVAL:
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
        print(f"[Userbot] LOG fail: {e}")


async def main():
    await load_sudoers()
    await track_chats()
    register_trigger_autodelete(app, enabled=True)

    try:
        await app.start()
        me = await app.get_me()
        set_me_id(me.id)
        if OWNER_ID:
            SUDO_USERS.add(OWNER_ID)
        SUDO_USERS.add(me.id)
        print(f"[Userbot] Started as {me.first_name} (@{me.username or me.id})")
        print(f"[Userbot] ME_ID={me.id} OWNER={OWNER_ID}")
    except Exception as e:
        print(f"[Userbot] FATAL: {e}")
        raise

    try:
        from modules.owner.session_manager import boot_saved_sessions

        await boot_saved_sessions()
    except Exception as e:
        print(f"[Userbot] extra sessions: {e}")

    try:
        from modules.utils.autoreply import boot_style_scan

        asyncio.create_task(boot_style_scan())
    except Exception as e:
        print(f"[Userbot] style scan: {e}")

    await asyncio.sleep(1)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    uname = f"@{me.username}" if me.username else "—"
    await _notify_log(
        f"<b>USERBOT STARTED</b>\n"
        f"Name: <b>{me.first_name}</b>\n"
        f"User: {uname}\n"
        f"ID: <code>{me.id}</code>\n"
        f"Time: <code>{now}</code>"
    )

    await asyncio.sleep(2)
    try:
        await ensure_started(app)
        print("[Userbot] PyTgCalls ready")
    except Exception as e:
        print(f"[Userbot] PyTgCalls: {e}")

    print("[Userbot] READY")
    await _notify_log(f"<b>{BOT_NAME or 'Yashika'} READY</b>")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
