"""
Command auto-delete — deletes YOUR .cmd message after delay.
Reply message stays. Delay 4s so reply pehle aa jaye.
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message

DELETE_DELAY = 4.0


def register_trigger_autodelete(app, enabled: bool = True):
    if not enabled:
        print("[autodelete] OFF")
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

    print(f"[autodelete] ON — delay {DELETE_DELAY}s")
