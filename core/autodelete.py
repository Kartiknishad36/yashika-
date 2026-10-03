"""
Command message auto-delete — AFTER handlers reply.

Group 40 = commands (group 0) pehle chalenge, phir trigger delete.
Bot/userbot ka reply message delete nahi hota.
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message

DELETE_DELAY = 1.0  # reply aane ke baad thoda wait


def register_trigger_autodelete(app):
    @app.on_message(
        filters.text & filters.regex(r"^[.!]\w"),
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
