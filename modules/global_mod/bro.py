"""
.bro / .broall / .brodm / .brogroup / .unbro / .brolist
"""
import json
import random
import re
from pathlib import Path

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd
from database.mongo import (
    add_bro_target, remove_bro_target, get_bro_targets, get_bro_mode,
)

_SEED = [
    "MADARCHOD TERI MAA KI CHUUT ME GHUTKA KHAAKE THOOK DUNGA",
    "TERE BEHEN K CHUUT ME CHAKU DAAL KAR CHUUT KA KHOON KAR DUGA",
    "TERI VAHEEN NHI HAI KYA? 9 MAHINE RUK SAGI VAHEEN DETA HU",
    "TERI MAA K BHOSDE ME AEROPLANEPARK KARKE UDAAN BHAR DUGA",
    "TERI MAA KI CHUUT ME SUTLI BOMB FOD DUNGA",
    "TERA BAAP HU BHOSDIKE",
    "SUN MADARCHOD JYADA NA UCHAL MAA CHOD DENGE EK MIN MEI",
    "TERI MAA KA YAAR HU MEI",
]


def _load_lines() -> list:
    folder = Path(__file__).parent
    out = list(_SEED)
    seen = set(out)
    for p in sorted(folder.glob("bro_part_*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for line in data:
                    if line and line not in seen:
                        out.append(line)
                        seen.add(line)
        except Exception:
            pass
    if len(out) < 50:
        try:
            import urllib.request
            url = (
                "https://raw.githubusercontent.com/Kartiknishad36/yashika-/"
                "33d776563482c2bfea302d31b25d2cde61fdbc79/modules/global_mod/bro.py"
            )
            with urllib.request.urlopen(url, timeout=12) as r:
                text = r.read().decode("utf-8", errors="ignore")
            m = re.search(r"BRO_LINES\s*=\s*\[(.*?)\]\s*\n", text, re.S)
            if m:
                for s in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1)):
                    if s and s not in seen:
                        out.append(s)
                        seen.add(s)
        except Exception:
            pass
    return out if out else _SEED


BRO_LINES = _load_lines()


def _target_from_message(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        return u.id, u.mention
    parts = (message.text or "").split()
    if len(parts) > 1:
        arg = parts[-1]
        if arg.lstrip("-").isdigit():
            return int(arg), f"<code>{arg}</code>"
    return None, None


async def _enable(client, message: Message, mode: str):
    tid, mention = _target_from_message(message)
    if not tid:
        await message.reply_text("Reply + <code>.bro</code> / <code>.brodm</code>")
        return
    try:
        me = await client.get_me()
        if tid == me.id:
            await message.reply_text("Khud pe bro nahi.")
            return
    except Exception:
        pass
    await add_bro_target(tid, mode)
    label = {"all": "DM+GROUP", "dm": "DM", "group": "GROUP"}.get(mode, mode)
    await message.reply_text(
        f"Auto-Reply <b>ON</b> ({label})\nTarget: {mention}\n"
        f"Pool: <code>{len(BRO_LINES)}</code>"
    )


async def _disable_bro(client, message: Message):
    tid, mention = _target_from_message(message)
    if not tid:
        await message.reply_text("Reply + <code>.unbro</code>")
        return
    await remove_bro_target(tid)
    await message.reply_text(f"Auto-Reply <b>OFF</b> for {mention or tid}")


@app.on_message(ub_cmd("bro", "broall") & filters.me)
async def bro_cmd(client, message: Message):
    parts = (message.text or "").split()
    if len(parts) > 1 and parts[1].lower() in ("off", "stop", "remove", "del", "disable"):
        return await _disable_bro(client, message)
    await _enable(client, message, "all")


@app.on_message(ub_cmd("brodm") & filters.me)
async def brodm_cmd(client, message: Message):
    await _enable(client, message, "dm")


@app.on_message(ub_cmd("brogroup") & filters.me)
async def brogroup_cmd(client, message: Message):
    await _enable(client, message, "group")


@app.on_message(ub_cmd("unbro", "brooff") & filters.me)
async def unbro_cmd(client, message: Message):
    await _disable_bro(client, message)


@app.on_message(ub_cmd("brolist") & filters.me)
async def brolist_cmd(client, message: Message):
    targets = await get_bro_targets()
    if not targets:
        await message.reply_text("Bro list empty.")
        return
    lines = []
    for uid in targets:
        mode = await get_bro_mode(uid) or "?"
        lines.append(f"• <code>{uid}</code> — <b>{mode}</b>")
    await message.reply_text(
        f"<b>Bro list</b> (pool: {len(BRO_LINES)})\n\n" + "\n".join(lines)
    )


@app.on_message(
    filters.incoming & ~filters.bot & ~filters.via_bot & ~filters.service & ~filters.me,
    group=50,
)
async def bro_auto_reply(client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    mode = await get_bro_mode(user_id)
    if not mode:
        return
    is_private = message.chat.type == ChatType.PRIVATE
    if mode == "dm" and not is_private:
        return
    if mode == "group" and is_private:
        return
    text = message.text or message.caption or ""
    if text.startswith((".", "!", "/")):
        return
    line = random.choice(BRO_LINES)
    try:
        await message.reply_text(f"{message.from_user.mention}, {line}")
    except Exception:
        pass
