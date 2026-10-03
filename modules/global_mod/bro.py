"""
.bro / .broall → DM+GROUP | .brodm | .brogroup | .unbro | .brolist
Lines: modules/global_mod/bro_part_*.json (200+)
"""
import json
import random
from pathlib import Path

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import sudo_only
from database.mongo import (
    add_bro_target,
    remove_bro_target,
    get_bro_targets,
    get_bro_mode,
)

PREFIXES = [".", "!"]


def _load_lines() -> list:
    folder = Path(__file__).parent
    out = []
    for p in sorted(folder.glob("bro_part_*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                out.extend(data)
        except Exception:
            pass
    if not out:
        single = folder / "bro_lines.json"
        if single.exists():
            try:
                data = json.loads(single.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    out = data
            except Exception:
                pass
    if not out:
        out = ["𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘 𝗚𝗛𝗨𝗧𝗞𝗔 𝗞𝗛𝗔𝗔𝗞𝗘 𝗧𝗛𝗢𝗢𝗞 𝗗𝗨𝗡𝗚𝗔 🤣🤣"]
    return out


BRO_LINES = _load_lines()


def cmd(*names):
    return filters.command(list(names), prefixes=PREFIXES)


def _target_from_message(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        return u.id, u.mention
    if len(message.command) > 1:
        arg = message.command[-1]
        if arg.lstrip("-").isdigit():
            return int(arg), f"<code>{arg}</code>"
    return None, None


async def _enable(client, message: Message, mode: str):
    tid, mention = _target_from_message(message)
    if not tid:
        await message.reply_text(
            "Usage: kisi user pe <b>reply</b> + <code>.bro</code> / "
            "<code>.brodm</code> / <code>.brogroup</code>"
        )
        return
    try:
        me = await client.get_me()
        if tid == me.id:
            await message.reply_text("Khud pe bro enable nahi kar sakte.")
            return
    except Exception:
        pass
    await add_bro_target(tid, mode)
    label = {"all": "DM + GROUP", "dm": "sirf DM", "group": "sirf GROUP"}.get(mode, mode)
    await message.reply_text(
        f"✅ Auto-Reply <b>ON</b> ({label})\nTarget: {mention}\nID: <code>{tid}</code>\n"
        f"Lines loaded: <code>{len(BRO_LINES)}</code>"
    )


@app.on_message(cmd("bro", "broall"))
@sudo_only
async def bro_cmd(client, message: Message):
    if len(message.command) > 1 and message.command[1].lower() in (
        "off", "stop", "remove", "del", "disable"
    ):
        return await _disable_bro(client, message)
    await _enable(client, message, "all")


@app.on_message(cmd("brodm"))
@sudo_only
async def brodm_cmd(client, message: Message):
    await _enable(client, message, "dm")


@app.on_message(cmd("brogroup"))
@sudo_only
async def brogroup_cmd(client, message: Message):
    await _enable(client, message, "group")


@app.on_message(cmd("unbro", "brooff"))
@sudo_only
async def unbro_cmd(client, message: Message):
    await _disable_bro(client, message)


async def _disable_bro(client, message: Message):
    tid, mention = _target_from_message(message)
    if not tid:
        await message.reply_text("Reply + <code>.unbro</code> ya <code>.unbro <id></code>")
        return
    await remove_bro_target(tid)
    await message.reply_text(f"✅ Auto-Reply <b>OFF</b> for {mention or tid}")


@app.on_message(cmd("brolist"))
@sudo_only
async def brolist_cmd(client, message: Message):
    targets = await get_bro_targets()
    if not targets:
        await message.reply_text("Bro list khali hai.")
        return
    lines = []
    for uid in targets:
        mode = await get_bro_mode(uid) or "?"
        lines.append(f"• <code>{uid}</code> — <b>{mode}</b>")
    await message.reply_text(
        f"💕 <b>Bro list</b> (lines pool: {len(BRO_LINES)})\n\n" + "\n".join(lines)
    )


@app.on_message(
    filters.incoming
    & ~filters.bot
    & ~filters.via_bot
    & ~filters.service
    & ~filters.me,
    group=50,
)
async def bro_auto_reply(client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    mode = await get_bro_mode(user_id)
    if not mode:
        return
    try:
        me = await client.get_me()
        if user_id == me.id:
            return
    except Exception:
        pass
    is_private = message.chat.type == ChatType.PRIVATE
    if mode == "dm" and not is_private:
        return
    if mode == "group" and is_private:
        return
    text = message.text or message.caption or ""
    if text.startswith((".", "!", "/")):
        return
    line = random.choice(BRO_LINES)
    mention = message.from_user.mention
    try:
        await message.reply_text(f"{mention}, {line}")
    except Exception:
        try:
            await client.send_message(message.chat.id, f"{mention}, {line}")
        except Exception:
            pass
