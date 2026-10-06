import asyncio
from pyrogram import filters
from pyrogram.types import Message
from config import AUTO_DELETE, DELETE_DELAY


def register_trigger_autodelete(client, enabled=None):
    on = AUTO_DELETE if enabled is None else enabled
    if not on or client is None:
        print("[autodelete] userbot OFF")
        return

    async def _out(_, __, message: Message):
        if not getattr(message, "outgoing", False):
            return False
        text = (message.text or "").strip()
        return bool(text) and text[0] in ".!" and len(text) > 1

    @client.on_message(filters.create(_out), group=40)
    async def _delete_trigger(client, message: Message):
        async def _task():
            await asyncio.sleep(float(DELETE_DELAY))
            try:
                await message.delete()
            except Exception:
                pass
        asyncio.create_task(_task())

    print(f"[autodelete] userbot ON — {DELETE_DELAY}s")


def register_bot_autodelete(bot_client, enabled=None):
    on = AUTO_DELETE if enabled is None else enabled
    if not on or bot_client is None:
        print("[autodelete] bot OFF")
        return
    print(f"[autodelete] bot mode — {DELETE_DELAY}s")


async def auto_delete_msg(message: Message, delay=None):
    d = float(DELETE_DELAY if delay is None else delay)

    async def _task():
        await asyncio.sleep(d)
        try:
            await message.delete()
        except Exception:
            pass

    asyncio.create_task(_task())
