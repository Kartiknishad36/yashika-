"""
Local JSON-file storage — replaces MongoDB entirely so no external DB/network
dependency is needed. Same function names/signatures as before, so no other
module needs to change.
"""
import json
import asyncio
import os
import time

_DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "storage.json",
)
_lock = asyncio.Lock()

_DEFAULT = {
    "sudoers": [],
    "gbans": {},
    "chats": {},
    "warns": {},
    "approved_pm": [],
    "welcome": {},
    "bro_targets": [],
    "vcinfo": {},
    "economy": {},
    "chatbot": {},
    "ai_history": {},
    "ai_facts": {},
}

_DEFAULT_BALANCE = 300
_DAILY_REWARD = 200
_DAILY_COOLDOWN = 24 * 60 * 60


def _read() -> dict:
    if not os.path.exists(_DATA_FILE):
        return dict(_DEFAULT)
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in _DEFAULT.items():
            data.setdefault(k, v if not isinstance(v, (dict, list)) else type(v)())
        return data
    except (json.JSONDecodeError, FileNotFoundError):
        return dict(_DEFAULT)


def _write(data: dict):
    tmp = _DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, _DATA_FILE)


# ===================== Sudo users =====================
async def add_sudo(user_id: int):
    async with _lock:
        data = _read()
        if user_id not in data["sudoers"]:
            data["sudoers"].append(user_id)
        _write(data)


async def remove_sudo(user_id: int):
    async with _lock:
        data = _read()
        data["sudoers"] = [u for u in data["sudoers"] if u != user_id]
        _write(data)


async def get_sudoers() -> list[int]:
    async with _lock:
        return list(_read()["sudoers"])


# ===================== Global ban =====================
async def gban_user(user_id: int, reason: str = "No reason given"):
    async with _lock:
        data = _read()
        data["gbans"][str(user_id)] = reason
        _write(data)


async def ungban_user(user_id: int):
    async with _lock:
        data = _read()
        data["gbans"].pop(str(user_id), None)
        _write(data)


async def is_gbanned(user_id: int) -> bool:
    async with _lock:
        return str(user_id) in _read()["gbans"]


async def get_gban_list() -> list[dict]:
    async with _lock:
        data = _read()
        return [
            {"user_id": int(uid), "reason": reason}
            for uid, reason in data["gbans"].items()
        ]


# ===================== Chats =====================
async def add_chat(chat_id: int, title: str = ""):
    async with _lock:
        data = _read()
        data["chats"][str(chat_id)] = title
        _write(data)


async def remove_chat(chat_id: int):
    async with _lock:
        data = _read()
        data["chats"].pop(str(chat_id), None)
        _write(data)


async def get_all_chats() -> list[int]:
    async with _lock:
        return [int(cid) for cid in _read()["chats"].keys()]


# ===================== Warns =====================
def _warn_key(chat_id: int, user_id: int) -> str:
    return f"{chat_id}:{user_id}"


async def add_warn(chat_id: int, user_id: int, reason: str = "No reason given") -> int:
    async with _lock:
        data = _read()
        data.setdefault("warns", {})
        key = _warn_key(chat_id, user_id)
        entry = data["warns"].setdefault(key, [])
        entry.append(reason)
        _write(data)
        return len(entry)


async def get_warns(chat_id: int, user_id: int) -> list[str]:
    async with _lock:
        return list(data.get("warns", {}).get(_warn_key(chat_id, user_id), [])) if False else list(
            _read().get("warns", {}).get(_warn_key(chat_id, user_id), [])
        )


async def reset_warns(chat_id: int, user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("warns", {})
        data["warns"].pop(_warn_key(chat_id, user_id), None)
        _write(data)


# ===================== PM Guard =====================
async def approve_pm(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("approved_pm", [])
        if user_id not in data["approved_pm"]:
            data["approved_pm"].append(user_id)
        _write(data)


async def unapprove_pm(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("approved_pm", [])
        data["approved_pm"] = [u for u in data["approved_pm"] if u != user_id]
        _write(data)


async def get_approved_pm() -> list[int]:
    async with _lock:
        return list(_read().get("approved_pm", []))


# ===================== Welcome =====================
DEFAULT_WELCOME_TEXT = "👋 Welcome {mention} to {chat}!"


async def set_welcome_enabled(chat_id: int, enabled: bool):
    async with _lock:
        data = _read()
        data.setdefault("welcome", {})
        entry = data["welcome"].setdefault(str(chat_id), {})
        entry["enabled"] = enabled
        _write(data)


async def get_welcome_enabled(chat_id: int) -> bool:
    async with _lock:
        entry = _read().get("welcome", {}).get(str(chat_id), {})
        return bool(entry.get("enabled", False))


async def set_welcome_text(chat_id: int, text: str):
    async with _lock:
        data = _read()
        data.setdefault("welcome", {})
        entry = data["welcome"].setdefault(str(chat_id), {})
        entry["text"] = text
        _write(data)


async def get_welcome_text(chat_id: int) -> str:
    async with _lock:
        entry = _read().get("welcome", {}).get(str(chat_id), {})
        return entry.get("text") or DEFAULT_WELCOME_TEXT


# ===================== Bro targets =====================
async def add_bro_target(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("bro_targets", [])
        if user_id not in data["bro_targets"]:
            data["bro_targets"].append(user_id)
        _write(data)


async def remove_bro_target(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("bro_targets", [])
        data["bro_targets"] = [u for u in data["bro_targets"] if u != user_id]
        _write(data)


async def get_bro_targets() -> list[int]:
    async with _lock:
        return list(_read().get("bro_targets", []))


async def is_bro_target(user_id: int) -> bool:
    async with _lock:
        return user_id in _read().get("bro_targets", [])


# ===================== VC info (per chat) =====================
async def set_vcinfo_enabled(chat_id: int, enabled: bool):
    async with _lock:
        data = _read()
        data.setdefault("vcinfo", {})
        data["vcinfo"][str(chat_id)] = bool(enabled)
        _write(data)


async def get_vcinfo_enabled(chat_id: int) -> bool:
    """Default OFF."""
    async with _lock:
        return bool(_read().get("vcinfo", {}).get(str(chat_id), False))


# ===================== Economy =====================
def _eco_user(data: dict, user_id: int) -> dict:
    data.setdefault("economy", {})
    key = str(user_id)
    if key not in data["economy"]:
        data["economy"][key] = {
            "balance": _DEFAULT_BALANCE,
            "gems": 0.0,
            "kills": 0,
            "protect_until": 0,
            "last_daily": 0,
        }
    return data["economy"][key]


async def eco_get(user_id: int) -> dict:
    async with _lock:
        data = _read()
        return dict(_eco_user(data, user_id))


async def eco_set(user_id: int, **fields):
    async with _lock:
        data = _read()
        u = _eco_user(data, user_id)
        u.update(fields)
        _write(data)


async def eco_add_balance(user_id: int, amount: int) -> int:
    async with _lock:
        data = _read()
        u = _eco_user(data, user_id)
        u["balance"] = int(u.get("balance", 0)) + int(amount)
        if u["balance"] < 0:
            u["balance"] = 0
        _write(data)
        return int(u["balance"])


async def eco_try_daily(user_id: int) -> tuple[bool, int, int]:
    """Returns (ok, reward_or_seconds_left, new_balance)."""
    async with _lock:
        data = _read()
        u = _eco_user(data, user_id)
        now = int(time.time())
        last = int(u.get("last_daily", 0))
        left = _DAILY_COOLDOWN - (now - last)
        if left > 0:
            return False, left, int(u["balance"])
        u["last_daily"] = now
        u["balance"] = int(u.get("balance", 0)) + _DAILY_REWARD
        _write(data)
        return True, _DAILY_REWARD, int(u["balance"])


# ===================== Chatbot on/off (per group) =====================
async def set_chatbot(chat_id: int, enabled: bool):
    async with _lock:
        data = _read()
        data.setdefault("chatbot", {})
        data["chatbot"][str(chat_id)] = bool(enabled)
        _write(data)


async def get_chatbot(chat_id: int) -> bool:
    """Groups default OFF."""
    async with _lock:
        return bool(_read().get("chatbot", {}).get(str(chat_id), False))


# ===================== AI memory =====================
async def ai_get_history(user_id: int, limit: int = 12) -> list:
    async with _lock:
        hist = _read().get("ai_history", {}).get(str(user_id), [])
        return list(hist[-limit:])


async def ai_append(user_id: int, role: str, text: str, max_keep: int = 24):
    async with _lock:
        data = _read()
        data.setdefault("ai_history", {})
        key = str(user_id)
        hist = data["ai_history"].setdefault(key, [])
        hist.append({"role": role, "text": text})
        data["ai_history"][key] = hist[-max_keep:]
        _write(data)


async def ai_clear(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("ai_history", {})
        data["ai_history"][str(user_id)] = []
        _write(data)


async def ai_learn_fact(user_id: int, fact: str):
    async with _lock:
        data = _read()
        data.setdefault("ai_facts", {})
        key = str(user_id)
        facts = data["ai_facts"].setdefault(key, [])
        if fact not in facts:
            facts.append(fact[:200])
        data["ai_facts"][key] = facts[-30:]
        _write(data)


async def ai_get_facts(user_id: int) -> list:
    async with _lock:
        return list(_read().get("ai_facts", {}).get(str(user_id), []))
# ===================== Feature toggles (global) =====================
async def set_feature(name: str, enabled: bool):
    async with _lock:
        data = _read()
        data.setdefault("features", {})
        data["features"][name] = bool(enabled)
        _write(data)


async def get_feature(name: str, default: bool = True) -> bool:
    async with _lock:
        data = _read()
        return bool(data.get("features", {}).get(name, default))


# ===================== Per-chat toggles =====================
async def set_chat_flag(chat_id: int, name: str, enabled: bool):
    async with _lock:
        data = _read()
        data.setdefault("chat_flags", {})
        entry = data["chat_flags"].setdefault(str(chat_id), {})
        entry[name] = bool(enabled)
        _write(data)


async def get_chat_flag(chat_id: int, name: str, default: bool = False) -> bool:
    async with _lock:
        data = _read()
        entry = data.get("chat_flags", {}).get(str(chat_id), {})
        return bool(entry.get(name, default))
