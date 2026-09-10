import asyncio
import importlib

from core.clients import app, bot, assistant
from core.call_manager import ensure_started
from core.autodelete import register_trigger_autodelete
from database.mongo import add_chat
from modules.owner.sudoers import load_sudoers

MODULES = [
    "modules.owner.sudoers",
    "modules.owner.pmguard",
    "modules.vc.play",
    "modules.vc.controls",
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
    "modules.owner.clone",
    "modules.public.login",
    "modules.bot.start",
    "modules.economy.basic",
    "modules.games.couple",
    "modules.games.dice",
    "modules.games.truth_dare",
    "modules.games.bomb",
    "modules.fun_family.actions",
    "modules.utils.basics",
    "modules.utils.info",
    "modules.utils.fun",
    "modules.bot.ai_chat",
    "modules.bot.stickers",
    "modules.games.chase",
    "modules.games.ludo",
    "modules.bot.music",
    "modules.bot.logger",
]

for m in MODULES:
    try:
        importlib.import_module(m)
    except Exception as e:
        print(f"[Bot] WARNING: could not load module '{m}': {type(e).__name__}: {e}")


async def track_new_chats():
    """Keep chats list updated for broadcast / global tools."""
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

    await app.start()
    print("[Bot] Userbot client started.")

    if bot:
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

    if assistant:
        await assistant.start()
        print("[Bot] Assistant client started.")

    await ensure_started(app)
    print("[Bot] PyTgCalls started.")
    print("[Bot] Bot is ready.")

    await asyncio.Event().wait()


if __name__ == "__main__":
    # Pyrogram clients import-time pe loop pakadte hain —
    # asyncio.run() naya loop banata hai → avoid.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
