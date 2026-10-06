"""
Yashika — Bot + optional Userbot (Railway ready)

Required: API_ID, API_HASH, BOT_TOKEN, OWNER_ID
Optional: STRING_SESSION, MONGO_URI, LOG_GROUP_ID
"""
import asyncio
import importlib
from datetime import datetime, timezone

from config import (
    API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID,
    LOG_GROUP_ID, BOT_NAME, MONGO_URI,
)
from core.clients import bot, app
from core.autodelete import register_trigger_autodelete, register_bot_autodelete
from core.notify import notify_owner

BOT_MODULES = [
    "modules.bot.start",
    "modules.bot.login_bot",
]

UB_MODULES = [
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
    "modules.utils.intel",
    "modules.utils.nuinfo",
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


def _load(mods, label):
    ok = 0
    failed = []
    for m in mods:
        try:
            importlib.import_module(m)
            ok += 1
        except Exception as e:
            failed.append(m)
            print(f"[{label}] WARN {m}: {type(e).__name__}: {e}")
    print(f"[{label}] loaded {ok}/{len(mods)}")
    if failed:
        print(f"[{label}] FAILED: {', '.join(failed)}")
    return ok


async def main():
    if not API_ID or not API_HASH:
        raise SystemExit("API_ID / API_HASH required")
    if not BOT_TOKEN and not STRING_SESSION:
        raise SystemExit("Set BOT_TOKEN and/or STRING_SESSION")

    try:
        importlib.import_module("modules.owner.sudoers")
        importlib.import_module("modules.owner.session_manager")
    except Exception as e:
        print(f"[boot] core: {e}")

    if bot is not None:
        _load(BOT_MODULES, "bot")
        register_bot_autodelete(bot)
    else:
        print("[boot] BOT_TOKEN missing — bot off")

    if app is not None:
        _load(UB_MODULES, "userbot")
        register_trigger_autodelete(app, enabled=True)
        try:
            from modules.owner.sudoers import load_sudoers
            await load_sudoers()
        except Exception as e:
            print(f"[boot] sudoers: {e}")
    else:
        print("[boot] STRING_SESSION missing — userbot off")

    if MONGO_URI:
        try:
            from database.mongo_async import get_db
            await get_db()
        except Exception as e:
            print(f"[boot] mongo: {e}")

    if bot is not None:
        await bot.start()
        bme = await bot.get_me()
        print(f"[bot] @{bme.username} id={bme.id}")
        try:
            from modules.owner.sudoers import SUDO_USERS
            if OWNER_ID:
                SUDO_USERS.add(OWNER_ID)
        except Exception:
            pass

    if app is not None:
        await app.start()
        ume = await app.get_me()
        print(f"[userbot] {ume.first_name} id={ume.id}")
        try:
            from modules.owner.sudoers import set_me_id, SUDO_USERS
            set_me_id(ume.id)
            if OWNER_ID:
                SUDO_USERS.add(OWNER_ID)
            SUDO_USERS.add(ume.id)
        except Exception as e:
            print(f"[userbot] me: {e}")
        try:
            from modules.owner.session_manager import boot_saved_sessions
            await boot_saved_sessions()
        except Exception as e:
            print(f"[userbot] sessions: {e}")
        try:
            from core.call_manager import ensure_started
            await ensure_started(app)
            print("[userbot] PyTgCalls ready")
        except Exception as e:
            print(f"[userbot] PyTgCalls: {e}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    client = bot or app
    if client:
        await notify_owner(
            client,
            f"<b>{BOT_NAME} STARTED</b>\n"
            f"Mode: {'BOT' if bot else ''}{' + UB' if app else ''}\n"
            f"Time: <code>{now}</code>\n"
            f"Owner: <code>{OWNER_ID}</code>",
        )

    print("[READY] Railway worker running")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
