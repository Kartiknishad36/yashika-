"""
Gemini AI:
  DM  → always ON for normal text
  Group → only if /chatbot on
  /ai /ask always works everywhere
  /learn /aiclear
  Multi-language (reply in user's language)
"""
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

from core.clients import bot
from config import GEMINI_API_KEY, GEMINI_MODEL, BOT_NAME
from database.mongo import (
    get_chatbot,
    set_chatbot,
    ai_get_history,
    ai_append,
    ai_clear,
    ai_learn_fact,
    ai_get_facts,
)

if bot is None:
    raise RuntimeError("ai_chat needs BOT_TOKEN")

try:
    import google.generativeai as genai
except ImportError:
    genai = None

PREFIXES = ["/", ".", "!"]

SYSTEM = f"""You are {BOT_NAME}, a friendly Telegram AI.
Reply in the SAME language the user uses (Hindi, English, Hinglish, any language).
Be short in groups, warmer in private.
Use known user facts when useful.
You are an AI, not a human.
"""


def _model():
    if not GEMINI_API_KEY or genai is None:
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL, system_instruction=SYSTEM)


async def _ask(user_id: int, user_text: str) -> str:
    m = _model()
    if m is None:
        return "❌ Set `GEMINI_API_KEY` + install `google-generativeai`."

    facts = await ai_get_facts(user_id)
    hist = await ai_get_history(user_id, 10)
    lines = []
    if facts:
        lines.append("User facts:\n- " + "\n- ".join(facts))
    for h in hist:
        lines.append(("User: " if h["role"] == "user" else "Assistant: ") + h["text"])
    lines.append(f"User: {user_text}")
    lines.append("Assistant:")
    try:
        r = await m.generate_content_async("\n".join(lines))
        text = (r.text or "...").strip()
    except Exception as e:
        return f"❌ AI error: `{e}`"
    await ai_append(user_id, "user", user_text)
    await ai_append(user_id, "assistant", text)
    return text


@bot.on_message(filters.command(["chatbot"], prefixes=PREFIXES) & filters.group)
async def chatbot_toggle(client, message: Message):
    if len(message.command) < 2:
        on = await get_chatbot(message.chat.id)
        await message.reply_text(
            f"Chatbot is **{'ON' if on else 'OFF'}** here.\n"
            f"`/chatbot on` | `/chatbot off`"
        )
        return
    arg = message.command[1].lower()
    if arg in ("on", "enable", "1"):
        await set_chatbot(message.chat.id, True)
        await message.reply_text("✅ Group chatbot **ON** BABY AAO HUM ROMANTICBATE KARTE HE .")
    elif arg in ("off", "disable", "0"):
        await set_chatbot(message.chat.id, False)
        await message.reply_text("❌ Group chatbot **OFF**.")
    else:
        await message.reply_text("Usage: `/chatbot on` | `/chatbot off`")


@bot.on_message(filters.command(["ai", "ask"], prefixes=PREFIXES))
async def ai_manual(client, message: Message):
    if not message.from_user:
        return
    parts = (message.text or "").split(None, 1)
    if len(parts) < 2:
        await message.reply_text("`/ai your message`")
        return
    w = await message.reply_text("💭...")
    ans = await _ask(message.from_user.id, parts[1].strip())
    try:
        await w.edit_text(ans)
    except Exception:
        await message.reply_text(ans)


@bot.on_message(filters.command("learn", prefixes=PREFIXES))
async def learn_cmd(client, message: Message):
    if not message.from_user or len(message.command) < 2:
        await message.reply_text("`/learn I like tea`")
        return
    fact = " ".join(message.command[1:])[:200]
    await ai_learn_fact(message.from_user.id, fact)
    await message.reply_text(f"✅ Learned:\n<i>{fact}</i>")


@bot.on_message(filters.command("aiclear", prefixes=PREFIXES))
async def aiclear_cmd(client, message: Message):
    if not message.from_user:
        return
    await ai_clear(message.from_user.id)
    await message.reply_text("🧹 Memory cleared.")


def _is_cmd(text: str) -> bool:
    if not text:
        return True
    return text.startswith(("/", ".", "!"))


@bot.on_message(
    filters.text
    & ~filters.via_bot
    & ~filters.service
    & filters.incoming,
    group=40,
)
async def ai_auto(client, message: Message):
    if not message.from_user or message.from_user.is_bot:
        return
    text = (message.text or "").strip()
    if not text or _is_cmd(text):
        return

    is_private = message.chat.type == ChatType.PRIVATE

    # DM — hamesha
    if is_private:
        pass
    else:
        # Group — chatbot ON chahiye
        if not await get_chatbot(message.chat.id):
            return

        try:
            me = await client.get_me()
        except Exception:
            return

        # 1) Reply to someone else (not bot) → ignore
        if message.reply_to_message and message.reply_to_message.from_user:
            rid = message.reply_to_message.from_user.id
            if rid != me.id:
                return

        # 2) Mention only other users (bot mention nahi) → ignore
        mentioned_ids = set()
        if message.entities:
            for ent in message.entities:
                if ent.type.name == "MENTION":
                    # @username — resolve later
                    pass
                if ent.type.name == "TEXT_MENTION" and ent.user:
                    mentioned_ids.add(ent.user.id)

        bot_mentioned = False
        # text mention @botusername
        uname = (me.username or "").lower()
        if uname and f"@{uname}" in text.lower():
            bot_mentioned = True
        if me.id in mentioned_ids:
            bot_mentioned = True

        # reply to bot?
        reply_to_bot = bool(
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == me.id
        )

        plain = (
            not message.reply_to_message
            and not mentioned_ids
            and not (uname and "@" in text)
        )

        # Allow: reply-to-bot OR bot-mention OR plain chat
        if not (reply_to_bot or bot_mentioned or plain):
            return

    # don't reply to self
    try:
        me = await client.get_me()
        if message.from_user.id == me.id:
            return
    except Exception:
        pass

    # direct reply (no "💭..." delay)
    ans = await _ask(message.from_user.id, text)
    try:
        await message.reply_text(ans)
    except Exception:
        pass
