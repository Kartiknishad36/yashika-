"""
Bro auto-reply (sudo/owner)

  .bro / .broall   → reply user → DM + GROUP auto-reply
  .brodm           → reply user → only DM
  .brogroup        → reply user → only GROUP
  .unbro / .bro off → disable (reply or id)
  .brolist         → list targets

Target jab bhi message kare (group/DM as per mode), random line se reply.
"""
import random

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

BRO_LINES = [
    "𝗠𝗔̂𝗔̂𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘 𝗚𝗛𝗨𝗧𝗞𝗔 𝗞𝗛𝗔𝗔𝗞𝗘 𝗧𝗛𝗢𝗢𝗞 𝗗𝗨𝗡𝗚𝗔 🤣🤣",
    "𝗧𝗘𝗥𝗘 𝗕𝗘́𝗛𝗘𝗡 𝗞 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘 𝗖𝗛𝗔𝗞𝗨 𝗗𝗔𝗔𝗟 𝗞𝗔𝗥 𝗖𝗛𝗨𝗨́𝗧 𝗞𝗔 𝗞𝗛𝗢𝗢𝗡 𝗞𝗔𝗥 𝗗𝗨𝗚𝗔",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗡𝗛𝗜 𝗛𝗔𝗜 𝗞𝗬𝗔? 9 𝗠𝗔𝗛𝗜𝗡𝗘 𝗥𝗨𝗞 𝗦𝗔𝗚𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗘𝗧𝗔 𝗛𝗨 🤣🤣🤩",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗘𝗥𝗢𝗣𝗟𝗔𝗡𝗘𝗣𝗔𝗥𝗞 𝗞𝗔𝗥𝗞𝗘 𝗨𝗗𝗔𝗔𝗡 𝗕𝗛𝗔𝗥 𝗗𝗨𝗚𝗔 ✈️🛫",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 💣",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘 𝗦𝗖𝗢𝗢𝗧𝗘𝗥 𝗗𝗔𝗔𝗟 𝗗𝗨𝗚𝗔👅",
    "𝗗𝗨𝗗𝗛 𝗛𝗜𝗟𝗔𝗔𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗘 𝗨𝗣𝗥 𝗡𝗜𝗖𝗛𝗘 🆙🆒😙",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘 ✋ 𝗛𝗔𝗧𝗧𝗛 𝗗𝗔𝗟𝗞𝗘 👶 𝗕𝗔𝗖𝗖𝗛𝗘 𝗡𝗜𝗞𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 😍",
    "𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘 𝗞𝗘𝗟𝗘 𝗞𝗘 𝗖𝗛𝗜𝗟𝗞𝗘 🍌🍌😍",
    "𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘 𝗨𝗦𝗘𝗥𝗕𝗢𝗧 𝗟𝗔𝗚𝗔𝗔𝗨𝗡𝗚𝗔 𝗦𝗔𝗦𝗧𝗘 𝗦𝗣𝗔𝗠 𝗞𝗘 𝗖𝗛𝗢𝗗𝗘",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗗𝗛𝗔𝗡𝗗𝗛𝗘 𝗩𝗔𝗔𝗟𝗜 😋😛",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘 𝗔𝗖 𝗟𝗔𝗚𝗔 𝗗𝗨𝗡𝗚𝗔 𝗦𝗔𝗔𝗥𝗜 𝗚𝗔𝗥𝗠𝗜 𝗡𝗜𝗞𝗔𝗟 𝗝𝗔𝗔𝗬𝗘𝗚𝗜",
    "𝗧𝗘𝗥𝗜 𝗩𝗔𝗛𝗘𝗘𝗡 𝗞𝗢 𝗛𝗢𝗥𝗟𝗜𝗖𝗞𝗦 𝗣𝗘𝗘𝗟𝗔𝗨𝗡𝗚𝗔 𝗠𝗔̂𝗔̂𝗗𝗔𝗥𝗖𝗛Ø𝗗😚",
    "𝗧𝗘𝗥𝗔 𝗣𝗘𝗛𝗟𝗔 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗠𝗔̂𝗔̂𝗗𝗔𝗥𝗖𝗛Ø𝗗",
    "𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗙𝗔𝗡𝗧𝗔𝗦𝗬 𝗛𝗨 𝗟𝗔𝗪𝗗𝗘, 𝗧𝗨 𝗔𝗣𝗡𝗜 𝗕𝗛𝗘𝗡 𝗞𝗢 𝗦𝗠𝗕𝗛𝗔𝗔𝗟 😈😈",
    "𝗔𝗨𝗞𝗔𝗔𝗧 𝗠𝗘 𝗥𝗘𝗛 𝗩𝗥𝗡𝗔 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗗𝗔𝗡𝗗𝗔 𝗗𝗔𝗔𝗟 𝗞𝗘 𝗠𝗨𝗛 𝗦𝗘 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 🙄",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘𝗜 𝗕𝗔𝗧𝗧𝗘𝗥𝗬 𝗟𝗔𝗚𝗔 𝗞𝗘 𝗣𝗢𝗪𝗘𝗥𝗕𝗔𝗡𝗞 𝗕𝗔𝗡𝗔 𝗗𝗨𝗡𝗚𝗔 🔋🔥",
    "𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗠𝗘𝗜 𝗔𝗣𝗣𝗟𝗘 𝗞𝗔 18𝗪 𝗪𝗔𝗟𝗔 𝗖𝗛𝗔𝗥𝗚𝗘𝗥 🔥🤩",
    "𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨́𝗧 𝗞𝗔𝗔𝗟𝗜 🙁🤣💥",
    "𝗦𝗨𝗡 𝗠𝗔̂𝗔̂𝗗𝗔𝗥𝗖𝗛Ø𝗗 𝗝𝗬𝗔𝗗𝗔 𝗡𝗔 𝗨𝗖𝗛𝗔𝗟 𝗠𝗔́𝗔̀ 𝗖𝗛𝗢𝗗 𝗗𝗘𝗡𝗚𝗘 𝗘𝗞 𝗠𝗜𝗡 𝗠𝗘𝗜 ✅",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗗𝗔𝗟 𝗞𝗘 𝗟𝗢𝗙𝗜 𝗕𝗔𝗝𝗔𝗨𝗡𝗚𝗔 𝗗𝗜𝗡 𝗕𝗛𝗔𝗥 😍",
    "𝗧𝗘𝗥𝗔 𝗕𝗔𝗔𝗣 𝗛𝗨 𝗕𝗛𝗢𝗦𝗗𝗜𝗞𝗘 🍷🤩🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗦𝗔𝗣𝗡𝗘 𝗠𝗘𝗜 𝗕𝗛𝗜 𝗬𝗔𝗔𝗗 𝗞𝗔𝗥𝗘𝗚𝗜 🥳",
    "𝗦𝗨𝗡 𝗕𝗘 𝗥Æ𝗡𝗗𝗜 𝗞𝗜 𝗔𝗨𝗟𝗔𝗔𝗗 😏🔥",
    "𝗧𝗘𝗥𝗜 𝗠𝗔́𝗔̀ 𝗞𝗔 𝗬𝗔𝗔𝗥 𝗛𝗨 𝗠𝗘𝗜 🤩🤣💥",
]


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
            f"Usage: kisi user pe <b>reply</b> + <code>.bro</code> / <code>.brodm</code> / <code>.brogroup</code>\n"
            f"Ya: <code>.bro {mode} <user_id></code>"
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
        f"✅ Auto-Reply <b>ON</b> ({label})\nTarget: {mention}\nID: <code>{tid}</code>"
    )


@app.on_message(cmd("bro", "broall"))
@sudo_only
async def bro_cmd(client, message: Message):
    # .bro off / .bro stop → disable
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
    await message.reply_text("💕 <b>Bro list</b>\n\n" + "\n".join(lines))


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
