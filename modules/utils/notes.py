"""
Notes / Snips (userbot):
  .save <name> <text>     — save note (or reply to msg)
  .get <name> / #<name>   — get note
  .notes                  — list names
  .clearnote <name>       — delete one
  .clearallnotes          — delete all (owner)

Stored in storage.json via mongo helpers.
"""
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import _read, _write, _lock  # reuse JSON storage

PREFIXES = [".", "!"]


async def _notes_all() -> dict:
    async with _lock:
        data = _read()
        data.setdefault("notes", {})
        return dict(data["notes"])


async def _note_set(name: str, text: str):
    async with _lock:
        data = _read()
        data.setdefault("notes", {})
        data["notes"][name.lower()] = text
        _write(data)


async def _note_del(name: str) -> bool:
    async with _lock:
        data = _read()
        data.setdefault("notes", {})
        if name.lower() in data["notes"]:
            del data["notes"][name.lower()]
            _write(data)
            return True
        return False


async def _note_clear():
    async with _lock:
        data = _read()
        data["notes"] = {}
        _write(data)


@app.on_message(filters.command(["save", "snips"], prefixes=PREFIXES))
@sudo_only
async def save_note(client, message: Message):
    # .save name text  |  reply + .save name
    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n`.save hi Hello!`\nReply + `.save hi`"
        )
        return

    name = message.command[1].strip().lower()
    if not name.isalnum() and "_" not in name:
        await message.reply_text("Name: letters/numbers/`_` only.")
        return

    body = ""
    if message.reply_to_message:
        body = (
            message.reply_to_message.text
            or message.reply_to_message.caption
            or ""
        )
    if len(message.command) > 2:
        extra = message.text.split(None, 2)[2]
        body = (body + "\n" + extra).strip() if body else extra

    if not body:
        await message.reply_text("Kuch text do ya msg pe reply karke `.save name`.")
        return

    await _note_set(name, body[:4000])
    await message.reply_text(f"✅ Note saved: <code>{name}</code>")


@app.on_message(filters.command(["get", "note"], prefixes=PREFIXES))
@sudo_only
async def get_note(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `.get hi`")
        return
    name = message.command[1].strip().lower()
    notes = await _notes_all()
    if name not in notes:
        await message.reply_text(f"❌ Note nahi mili: <code>{name}</code>")
        return
    await message.reply_text(notes[name])


@app.on_message(filters.command(["notes", "saved"], prefixes=PREFIXES))
@sudo_only
async def list_notes(client, message: Message):
    notes = await _notes_all()
    if not notes:
        await message.reply_text("No notes yet. `.save name text`")
        return
    names = ", ".join(f"<code>{n}</code>" for n in sorted(notes.keys()))
    await message.reply_text(f"📌 <b>Notes</b> ({len(notes)}):\n{names}")


@app.on_message(filters.command(["clearnote", "rmnote"], prefixes=PREFIXES))
@sudo_only
async def clear_note(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `.clearnote hi`")
        return
    name = message.command[1].strip().lower()
    ok = await _note_del(name)
    await message.reply_text(
        f"{'✅ Deleted' if ok else '❌ Not found'}: <code>{name}</code>"
    )


@app.on_message(filters.command(["clearallnotes"], prefixes=PREFIXES))
@sudo_only
async def clear_all_notes(client, message: Message):
    await _note_clear()
    await message.reply_text("✅ All notes cleared.")


# Optional: #name shorthand (group/private)
@app.on_message(
    filters.regex(r"^#([A-Za-z0-9_]+)$") & filters.incoming,
    group=12,
)
@sudo_only
async def hash_note(client, message: Message):
    name = message.matches[0].group(1).lower()
    notes = await _notes_all()
    if name not in notes:
        return
    await message.reply_text(notes[name])
