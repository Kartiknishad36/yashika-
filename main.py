import asyncio
import importlib

from core.clients import app, bot, assistant
from core.call_manager import ensure_started
from core.autodelete import register_trigger_autodelete
from database.mongo import add_chat
from modules.owner.sudoers import load_sudoers

MODULES = [
    # Owner / security
    "modules.owner.sudoers",
    "modules.owner.pmguard",
    "modules.owner.pm_extra",
    "modules.owner.clone",
    "modules.owner.tracker",
    # VC
    "modules.vc.play",
    "modules.vc.controls",
    # Global mod
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
    # Public
    "modules.public.login",
    # Bot UI / music / AI
    "modules.bot.start",
    "modules.bot.ai_chat",
    "modules.bot.stickers",
    "modules.bot.music",
    "modules.bot.logger",
    # Economy / games / fun
    "modules.economy.basic",
    "modules.games.couple",
    "modules.games.dice",
    "modules.games.truth_dare",
    "modules.games.bomb",
    "modules.games.chase",
    "modules.games.ludo",
    "modules.fun_family.actions",
    # Utils
    "modules.utils.basics",
    "modules.utils.info",
    "modules.utils.fun",
    "modules.utils.afk",
    "modules.utils.protect",
    "modules.utils.notes",
    "modules.utils.voice",
    # Media
    "modules.media.kang",
    "modules.media.download",
    "modules.media.social",
]

for m in MODULES:
    try:
        importlib.import_module(m)
    except Exception as e:
        print(f"[Bot] WARNING: could not load module '{m}': {type(e).__name__}: {e}")


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

    # ---- Userbot ----
    try:
        await app.start()
        print("[Bot] Userbot client started.")
    except Exception as e:
        print(f"[Bot] FATAL: userbot start failed: {e}")
        raise

    await asyncio.sleep(2)

    # ---- Bot token ----
    if bot:
        try:
            await bot.start()
            print("[Bot] Bot client started.")
            try:
                from modules.bot.bot_commands import setup_bot_commands
                await setup_bot_commands()
                print("[Bot] Bot commands registered.")
            except Exception as e:
                print(f"[Bot] WARNING: set_bot_commands failed: {e}")
            try:
                from modules.bot.logger import send_startup_logs
                await send_startup_logs()
                print("[Bot] Startup logs sent.")
            except Exception as e:
                print(f"[Bot] WARNING: startup logs failed: {e}")
        except Exception as e:
            print(f"[Bot] WARNING: bot start failed: {e}")

    await asyncio.sleep(2)

    # ---- Assistant ----
    if assistant:
        try:
            await assistant.start()
            print("[Bot] Assistant client started.")
        except Exception as e:
            print(f"[Bot] WARNING: assistant start failed: {e}")

    try:
        await ensure_started(app)
        print("[Bot] PyTgCalls started.")
    except Exception as e:
        print(f"[Bot] WARNING: PyTgCalls failed: {e}")

    print("[Bot] Bot is ready.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
