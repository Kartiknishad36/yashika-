"""Delete own .cmd after delay (outgoing only)."""
import asyncio
from pyrogram import filters
from pyrogram.types import Message

DELETE_DELAY = 1.5


def register_trigger_autodelete(app, enabled: bool = True):
    if not enabled:
        print("[autodelete] OFF")
        return

    async def _out(_, __, message: Message):
        if not getattr(message, "outgoing", False):
            return False
        text = (message.text or "").strip()
        return bool(text) and text[0] in ".!" and len(text) > 1

    @app.on_message(filters.create(_out), group=40)
    async def _delete_trigger(client, message: Message):
        async def _task():
            await asyncio.sleep(DELETE_DELAY)
            try:
                await message.delete()
            except Exception:
                pass

        asyncio.create_task(_task())

    print(f"[autodelete] ON — {DELETE_DELAY}s")
