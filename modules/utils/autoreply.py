"""
Smart Auto-Reply — per chat (DM + Group)

  .autoreply on|off
  .autoreply set <text>
  .autoreply mode smart|fixed
  .stylescan
  .stylestatus

Jis chat me ON — wahi pe reply (DM ya group).
Smart mode: teri style phrases + stickers + emoji.
"""
import asyncio
import random
import re
import time

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from core.clients import app
from modules.owner.sudoers import ub_cmd, sudo_only
from database.mongo import get_chat_flag, set_chat_flag, get_feature, set_feature

DEFAULT_TEXT = "Busy hoon, baad me reply karta hoon ✨"
COOLDOWN = 25
_LAST: dict = {}

_STYLE: dict = {
    "phrases": [],
    "emojis": [],
    "stickers": [],
    "avg_len": 40,
    "premium": False,
    "scanned": 0,
    "romantic": [],
    "dark": [],
    "casual": [],
}

_ROMANTIC_HINT = re.compile(
    r"(pyaar|love|baby|jaan|dil|miss|cute|beautiful|❤️|😍|😘|💕|💋|🥰)",
    re.I,
)
_DARK_HINT = re.compile(
    r"(dark|alone|pain|dead|void|sad|broken|hate|😢|💔|🖤|😔)",
    re.I,
)


async def _persist_style():
    try:
        await set_feature(
            "my_style",
            {
                "phrases": (_STYLE["phrases"] or [])[-200:],
                "emojis": (_STYLE["emojis"] or [])[:50],
                "stickers": (_STYLE["stickers"] or [])[-80:],
                "avg_len": _STYLE["avg_len"],
                "premium": _STYLE["premium"],
                "scanned": _STYLE["scanned"],
                "romantic": (_STYLE["romantic"] or [])[-80:],
                "dark": (_STYLE["dark"] or [])[-80:],
                "casual": (_STYLE["casual"] or [])[-120:],
            },
        )
    except Exception as e:
        print(f"[autoreply] persist: {e}")


async def _restore_style():
    try:
        data = await get_feature("my_style", None)
        if isinstance(data, dict):
            for k in list(_STYLE.keys()):
                if k in data and data[k] is not None:
                    _STYLE[k] = data[k]
            print(f"[autoreply] style phrases={len(_STYLE.get('phrases') or [])}")
    except Exception as e:
        print(f"[autoreply] restore: {e}")


def _extract_emojis(text: str) -> list:
    return re.findall(
        r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F600-\U0001F64F]+",
        text or "",
    )


def _ingest_text(text: str):
    text = (text or "").strip()
    if not text or text.startswith((".", "!", "/")):
        return
    if len(text) < 2 or len(text) > 400:
        return
    _STYLE["phrases"].append(text)
    for e in _extract_emojis(text):
        if e not in _STYLE["emojis"]:
            _STYLE["emojis"].append(e)
    if _ROMANTIC_HINT.search(text):
        _STYLE["romantic"].append(text)
    elif _DARK_HINT.search(text):
        _STYLE["dark"].append(text)
    else:
        _STYLE["casual"].append(text)


async def scan_my_style(client, limit_dialogs: int = 25, limit_msg: int = 40) -> str:
    me = await client.get_me()
    _STYLE["premium"] = bool(getattr(me, "is_premium", False))
    scanned = 0
    dialogs_n = 0
    try:
        async for d in client.get_dialogs(limit=limit_dialogs):
            chat = d.chat
            if not chat:
                continue
            if chat.type not in (ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP):
                continue
            dialogs_n += 1
            try:
                async for msg in client.get_chat_history(chat.id, limit=limit_msg):
                    if not msg.from_user or msg.from_user.id != me.id:
                        continue
                    scanned += 1
                    if msg.sticker:
                        fid = msg.sticker.file_id
                        if fid and fid not in _STYLE["stickers"]:
                            _STYLE["stickers"].append(fid)
                    text = msg.text or msg.caption or ""
                    if text:
                        _ingest_text(text)
            except Exception:
                continue
            await asyncio.sleep(0.12)
    except Exception as e:
        print(f"[autoreply] scan: {e}")

    for key in ("phrases", "romantic", "dark", "casual"):
        _STYLE[key] = list(dict.fromkeys(_STYLE[key]))[-200:]
    _STYLE["stickers"] = _STYLE["stickers"][-100:]
    if _STYLE["phrases"]:
        _STYLE["avg_len"] = int(
            sum(len(p) for p in _STYLE["phrases"]) / max(1, len(_STYLE["phrases"]))
        )
    _STYLE["scanned"] = scanned
    await _persist_style()
    return (
        f"Dialogs={dialogs_n} msgs={scanned}\n"
        f"phrases={len(_STYLE['phrases'])} romantic={len(_STYLE['romantic'])}\n"
        f"dark={len(_STYLE['dark'])} stickers={len(_STYLE['stickers'])}\n"
        f"emojis={len(_STYLE['emojis'])} premium={_STYLE['premium']}"
    )


def _pick_reply(incoming: str) -> str:
    incoming = incoming or ""
    pool = list(_STYLE.get("casual") or [])
    if _ROMANTIC_HINT.search(incoming) and _STYLE.get("romantic"):
        pool = list(_STYLE["romantic"]) + pool[:20]
    elif _DARK_HINT.search(incoming) and _STYLE.get("dark"):
        pool = list(_STYLE["dark"]) + pool[:20]
    if not pool:
        pool = list(_STYLE.get("phrases") or [])
    if not pool:
        return DEFAULT_TEXT
    words = set(re.findall(r"\w+", incoming.lower()))
    scored = []
    for p in pool:
        pw = set(re.findall(r"\w+", p.lower()))
        scored.append((len(words & pw), p))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [p for s, p in scored[:15] if s > 0] or [p for _, p in scored[:20]]
    text = random.choice(top)
    emos = _STYLE.get("emojis") or []
    if emos and random.random() < 0.45 and not _extract_emojis(text):
        text = f"{text} {random.choice(emos)}"
    max_len = 500 if _STYLE.get("premium") else 300
    return text[:max_len]


@app.on_message(ub_cmd("autoreply"))
@sudo_only
async def autoreply_cmd(client, message: Message):
    chat_id = message.chat.id if message.chat else 0
    parts = (message.text or "").split(None, 2)
    if len(parts) < 2:
        on = bool(await get_chat_flag(chat_id, "autoreply", False))
        mode = await get_chat_flag(chat_id, "autoreply_mode", "smart")
        text = await get_chat_flag(chat_id, "autoreply_text", DEFAULT_TEXT)
        kind = "DM" if message.chat and message.chat.type == ChatType.PRIVATE else "GROUP"
        await message.reply_text(
            f"<b>AutoReply</b> ({kind})\n"
            f"Status: <b>{'ON' if on else 'OFF'}</b>\n"
            f"Mode: <code>{mode}</code>\n"
            f"Fixed: <code>{text}</code>\n"
            f"Style phrases: <code>{len(_STYLE.get('phrases') or [])}</code>\n\n"
            f"<code>.autoreply on|off</code>\n"
            f"<code>.autoreply set text</code>\n"
            f"<code>.autoreply mode smart|fixed</code>\n"
            f"<code>.stylescan</code>"
        )
        return
    arg = parts[1].lower()
    if arg in ("on", "enable", "1"):
        await set_chat_flag(chat_id, "autoreply", True)
        kind = "DM" if message.chat and message.chat.type == ChatType.PRIVATE else "GROUP"
        await message.reply_text(f"✅ AutoReply <b>ON</b> — is {kind}")
        return
    if arg in ("off", "disable", "0"):
        await set_chat_flag(chat_id, "autoreply", False)
        await message.reply_text("❌ AutoReply <b>OFF</b>")
        return
    if arg == "set" and len(parts) > 2:
        text = parts[2][:500]
        await set_chat_flag(chat_id, "autoreply_text", text)
        await set_chat_flag(chat_id, "autoreply", True)
        await message.reply_text(f"Saved + ON:\n<code>{text}</code>")
        return
    if arg == "mode" and len(parts) > 2:
        mode = parts[2].lower().strip()
        if mode not in ("smart", "fixed"):
            await message.reply_text("smart | fixed")
            return
        await set_chat_flag(chat_id, "autoreply_mode", mode)
        await message.reply_text(f"Mode: <b>{mode}</b>")
        return
    await message.reply_text("Usage: on|off|set|mode")


@app.on_message(ub_cmd("stylescan", "scanstyle"))
@sudo_only
async def stylescan_cmd(client, message: Message):
    m = await message.reply_text("🔍 Style scan DM + groups…")
    result = await scan_my_style(client)
    await m.edit_text(f"<b>Style Scan</b>\n<code>{result}</code>")


@app.on_message(ub_cmd("stylestatus", "mystyle"))
@sudo_only
async def stylestatus_cmd(client, message: Message):
    await message.reply_text(
        f"<b>My Style</b>\n"
        f"Phrases: <code>{len(_STYLE.get('phrases') or [])}</code>\n"
        f"Romantic: <code>{len(_STYLE.get('romantic') or [])}</code>\n"
        f"Dark: <code>{len(_STYLE.get('dark') or [])}</code>\n"
        f"Stickers: <code>{len(_STYLE.get('stickers') or [])}</code>\n"
        f"Emojis: <code>{len(_STYLE.get('emojis') or [])}</code>\n"
        f"Premium: <b>{_STYLE.get('premium')}</b>\n"
        f"Scanned: <code>{_STYLE.get('scanned')}</code>"
    )


@app.on_message(
    filters.incoming & ~filters.me & ~filters.bot & ~filters.service,
    group=17,
)
async def auto_replier(client, message: Message):
    if not message.chat or not message.from_user:
        return
    chat_id = message.chat.id
    try:
        on = bool(await get_chat_flag(chat_id, "autoreply", False))
    except Exception:
        return
    if not on:
        return
    text0 = message.text or message.caption or ""
    if text0.startswith((".", "!", "/")):
        return
    uid = message.from_user.id
    key = (chat_id, uid)
    now = time.time()
    if now - _LAST.get(key, 0) < COOLDOWN:
        return
    _LAST[key] = now

    mode = await get_chat_flag(chat_id, "autoreply_mode", "smart")
    fixed = await get_chat_flag(chat_id, "autoreply_text", DEFAULT_TEXT)
    try:
        stickers = _STYLE.get("stickers") or []
        chance = 0.35 if _STYLE.get("premium") else 0.22
        if stickers and mode == "smart" and random.random() < chance:
            try:
                await message.reply_sticker(random.choice(stickers))
                return
            except Exception:
                pass
        if mode == "fixed":
            reply = str(fixed or DEFAULT_TEXT)
        elif _STYLE.get("phrases"):
            reply = _pick_reply(text0)
        else:
            reply = str(fixed or DEFAULT_TEXT)
        await message.reply_text(reply)
    except Exception as e:
        print(f"[autoreply] {e}")


async def boot_style_scan():
    await _restore_style()
    if len(_STYLE.get("phrases") or []) >= 25:
        print("[autoreply] style cached, skip scan")
        return
    await asyncio.sleep(10)
    try:
        r = await scan_my_style(app, limit_dialogs=12, limit_msg=20)
        print(f"[autoreply] boot: {r}")
    except Exception as e:
        print(f"[autoreply] boot fail: {e}")


print("[autoreply] smart module loaded")
