import asyncio
import importlib

from core.clients import app, assistant
from core.call_manager import ensure_started
from core.autodelete import register_trigger_autodelete
from database.mongo import add_chat
from modules.owner.sudoers import load_sudoers

# Pure USERBOT — no bot, no games, no animations
MODULES = [
    # ========== Owner / security ==========
    "modules.owner.sudoers",
    "modules.owner.pmguard",
    "modules.owner.pm_extra",
    "modules.owner.clone",
    "modules.owner.tracker",
    "modules.owner.raid_spam",
    "modules.owner.ghostmod",
    "modules.owner.secretlog",

    # ========== VC / Music ==========
    "modules.vc.play",
    "modules.vc.controls",

    # ========== Global mod ==========
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

    # ========== Economy ==========
    "modules.economy.basic",

    # ========== Utils (core) ==========
    "modules.utils.basics",
    "modules.utils.info",
    "modules.utils.fun",
    "modules.utils.afk",
    "modules.utils.protect",
    "modules.utils.notes",
    "modules.utils.voice",
    "modules.utils.nuinfo",

    # ========== Utils (extra) ==========
    "modules.utils.system_cmds",
    "modules.utils.tools",
    "modules.utils.profile_set",
    "modules.utils.fun_text",
    "modules.utils.spy_pack",
    "modules.utils.ultra_extra",
    "modules.utils.intel",
    "modules.utils.copy_tools",
    "modules.utils.hashtag",
    "modules.utils.profile_track",
    "modules.utils.vanish",
    "modules.utils.creator_tools",
    "modules.utils.autoleave_inactive",
    "modules.utils.fun_location",
    "modules.utils.leadsaver",
    "modules.utils.followup",
    "modules.utils.idbackup",
    "modules.utils.paste_cmd",
    "modules.utils.reminder",
    "modules.utils.filters_words",
    "modules.utils.shayari_extra",
    "modules.utils.qrcode_cmd",
    "modules.utils.stats_cmd",
    "modules.utils.setgroup",
    "modules.utils.autobio",
    "modules.utils.telegraph",
    "modules.utils.autojoin",
    "modules.utils.autoreply",
    "modules.utils.gclone",

    # ========== Media ==========
    "modules.media.kang",
    "modules.media.download",
    "modules.media.social",
]

for m in MODULES:
    try:
        importlib.import_module(m)
    except Exception as e:
        print(f"[Userbot] WARNING: could not load '{m}': {type(e).__name__}: {e}")


async def track_new_chats():
    from pyrogram import filters

    @app.on_message(filters.group, group=-1)
    async def _track(client, message):
        try:
            await add_chat(message.chat.id, message.chat.title or "")
        except Exception:
            pass


async def main():
    await load_sudoers()
    await track_new_chats()
    register_trigger_autodelete(app)

    try:
        await app.start()
        me = await app.get_me()
        print(f"[Userbot] Started as {me.first_name} (@{me.username or me.id})")
    except Exception as e:
        print(f"[Userbot] FATAL: start failed: {e}")
        raise

    await asyncio.sleep(1)

    if assistant:
        try:
            await assistant.start()
            a_me = await assistant.get_me()
            print(f"[Userbot] Assistant started as {a_me.first_name} (@{a_me.username or a_me.id})")
        except Exception as e:
            print(f"[Userbot] WARNING: assistant start failed: {e}")

    try:
        await ensure_started(app)
        print("[Userbot] PyTgCalls started.")
    except Exception as e:
        print(f"[Userbot] WARNING: PyTgCalls failed: {e}")

    print("[Userbot] Ready. All commands run on user account.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
