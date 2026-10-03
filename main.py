import asyncio
import importlib
from datetime import datetime, timezone

from core.clients import app, assistant
from core.call_manager import ensure_started
from core.autodelete import register_trigger_autodelete
from database.mongo import add_chat
from modules.owner.sudoers import load_sudoers, SUDO_USERS
from config import LOG_GROUP_ID, BOT_NAME, OWNER_ID

MODULES = [
    # Owner / security
    "modules.owner.sudoers",
    "modules.owner.pmguard",
    "modules.owner.pm_extra",
    "modules.owner.clone",
    "modules.owner.tracker",
    "modules.owner.raid_spam",
    "modules.owner.ghostmod",
    "modules.owner.secretlog",

    # VC / Music
    "modules.vc.play",
    "modules.vc.controls",
    "modules.utils.vc_welcome",

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
    "modules.global_mod.antiflood",
    "modules.global_mod.locks",
    "modules.global_mod.rules",
    "modules.global_mod.nightmode",
    "modules.global_mod.slowmode",
    "modules.global_mod.zombies",
    "modules.global_mod.autokick",
    "modules.global_mod.admin_extra",

    # Economy
    "modules.economy.basic",

    # Utils
    "modules.utils.basics",
    "modules.utils.info",
    "modules.utils.user_scan",
    "modules.utils.mongo_dp",
    "modules.utils.fun",
    "modules.utils.afk",
    "modules.utils.protect",
    "modules.utils.notes",
    "modules.utils.voice",
    "modules.utils.nuinfo",
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
    "modules.utils.qrcode_cmd",
    "modules.utils.stats_cmd",
    "modules.utils.setgroup",
    "modules.utils.autobio",
    "modules.utils.telegraph",
    "modules.utils.autojoin",
    "modules.utils.autoreply",
    "modules.utils.gclone",
    "modules.utils.help_cmd",

    # Media
    "modules.media.kang",
    "modules.media.download",
    "modules.media.social",
]

for m in MODULES:
    try:
        importlib.import_module(m)
    except Exception as e:
        print(f"[Userbot] WARNING: could not load '{m}': {type(e).__name__}: {e}")


async def track_chats():
    from pyrogram import filters

    # group=-1 runs BEFORE command handlers (group=0).
    # MUST continue_propagation — warna koi bhi .help/.menu/.ping fire nahi hota!
    @app.on_message(filters.group | filters.private, group=-1)
    async def _track(client, message):
        try:
            chat = message.chat
            if chat:
                title = (
                    getattr(chat, "title", None)
                    or getattr(chat, "first_name", None)
                    or ""
                )
                await add_chat(chat.id, title)
        except Exception:
            pass
        try:
            message.continue_propagation()
        except Exception:
            pass


async def _notify_log(text: str):
    if not LOG_GROUP_ID:
        return
    try:
        await app.send_message(LOG_GROUP_ID, text)
    except Exception as e:
        print(f"[Userbot] LOG_GROUP notify failed: {e}")


async def main():
    await load_sudoers()
    await track_chats()
    register_trigger_autodelete(app)

    me = None
    try:
        await app.start()
        me = await app.get_me()
        SUDO_USERS.add(me.id)
        if OWNER_ID:
            SUDO_USERS.add(OWNER_ID)
        print(f"[Userbot] Started as {me.first_name} (@{me.username or me.id})")
    except Exception as e:
        print(f"[Userbot] FATAL: start failed: {e}")
        raise

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    uname = f"@{me.username}" if me.username else "—"
    await _notify_log(
        "🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢\n"
        f"✅ <b>USERBOT STARTED</b>\n"
        "🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢\n\n"
        f"👑 Name: <b>{me.first_name}</b>\n"
        f"🔗 Username: {uname}\n"
        f"🆔 ID: <code>{me.id}</code>\n"
        f"💎 Bot: <b>{BOT_NAME or 'Yashika'}</b>\n"
        f"⏱ Time: <code>{now}</code>\n\n"
        f"📌 Try: <code>.help</code> <code>.menu</code> <code>.ping</code>"
    )

    await asyncio.sleep(1)

    if assistant:
        try:
            await assistant.start()
            a_me = await assistant.get_me()
            print(f"[Userbot] Assistant: {a_me.first_name} (@{a_me.username or a_me.id})")
            a_un = f"@{a_me.username}" if a_me.username else "—"
            await _notify_log(
                "🩵🩵🩵🩵🩵🩵🩵🩵🩵🩵\n"
                f"✅ <b>ASSISTANT STARTED</b>\n"
                "🩵🩵🩵🩵🩵🩵🩵🩵🩵🩵\n\n"
                f"🎧 Name: <b>{a_me.first_name}</b>\n"
                f"🔗 Username: {a_un}\n"
                f"🆔 ID: <code>{a_me.id}</code>\n"
                f"⏱ Time: <code>{now}</code>"
            )
        except Exception as e:
            print(f"[Userbot] WARNING: assistant failed: {e}")
            await _notify_log(
                f"⚠️ <b>ASSISTANT FAILED</b>\n<code>{type(e).__name__}: {e}</code>"
            )
    else:
        await _notify_log(
            "⚪️ <b>ASSISTANT</b>: not set\n"
            "(optional: <code>ASSISTANT_SESSION</code>)"
        )

    try:
        await ensure_started(app)
        print("[Userbot] PyTgCalls started.")
        await _notify_log("🎵 <b>PyTgCalls</b> · VC engine ready")
    except Exception as e:
        print(f"[Userbot] WARNING: PyTgCalls failed: {e}")
        await _notify_log(
            f"⚠️ <b>PyTgCalls failed</b>\n<code>{type(e).__name__}: {e}</code>"
        )

    print("[Userbot] Ready.")
    await _notify_log(
        "✨━━━━━━━━━━━━━━━━━━✨\n"
        f"💜 <b>{BOT_NAME or 'Yashika'} READY</b>\n"
        "✨━━━━━━━━━━━━━━━━━━✨\n\n"
        "Commands online.\n"
        "<code>.help</code> · <code>.menu</code> · <code>.ping</code>"
    )
    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
