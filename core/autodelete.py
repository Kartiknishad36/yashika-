"""
Command auto-delete — DISABLED by default.

Pehle command reply aane do; delete se lagta tha command ignore ho rahi hai
(especially FloodWait pe).

Enable later: register_trigger_autodelete(app, enabled=True)
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message

DELETE_DELAY = 3.0


def register_trigger_autodelete(app, enabled: bool = False):
    if not enabled:
        print("[autodelete] OFF (commands will not auto-delete)")
        return

    @app.on_message(
        filters.me & filters.text & filters.regex(r"^[.!]\w"),
        group=40,
    )
    async def _delete_trigger(client, message: Message):
        async def _task():
            await asyncio.sleep(DELETE_DELAY)
            try:
                await message.delete()
            except Exception:
                pass

        asyncio.create_task(_task())

    print("[autodelete] ON — delay", DELETE_DELAY, "s")
