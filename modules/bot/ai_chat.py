"""
Gemini chatbot:
  DM  → always ON
  Group → /chatbot on  +  (plain | @bot | reply-to-bot)
          dusre pe reply/tag → silent
  /ai /ask /learn /aiclear everywhere
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

SYSTEM = f"""You are {BOT_NAME}, a fun Telegram group chatbot girl.
Talk like a real friend — short, casual, natural.
Match user language (Hindi / English / Hinglish).
Groups: 1–3 short lines max. No essays.
Never say you are an AI. No formal tone. Emojis ok.
"""


def _model():
    if not GEMINI_API_KEY or genai is None:
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL, system_instruction=SYSTEM)


async def _ask(user_id: int, user_text: str) -> str:
    m = _model()
    if m is None:
        return "❌ Set GEMINI_API_KEY + install google-generativeai."

    facts = await ai_get_facts(user_id)
    hist = await ai_get_history(user_id, 4)  # short history = faster

    lines = []
    if facts:
        lines.append("Facts: " + "; ".join(facts[:5]))
    for h in hist:
        role = "User" if h["role"] == "user" else "You"
        lines.append(f"{role}: {str(h.get('text', ''))[:300]}")
    lines.append(f"User: {user_text[:500]}")
    lines.append("You:")

    try:
        r = await m.generate_content_async(
            "\n".join(lines),
            generation_config={
                "max_output_tokens": 120,
                "temperature": 0.9,
            },
        )
        text = (r.text or "...").strip()
    except Exception as e:
        return f"❌ AI error: `{e}`"

    await ai_append(user_id, "user", user_text[:500])
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
        await message.reply_text(
            "✅ Group chatbot **ON** — plain chat / @bot / reply-to-bot pe reply."
        )
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
    ans = await _ask(message.from_user.id, parts[1].strip())
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

    if not is_private:
        if not await get_chatbot(message.chat.id):
            return
        try:
            me = await client.get_me()
        except Exception:
            return

        # Reply to someone else → skip
        if message.reply_to_message and message.reply_to_message.from_user:
            if message.reply_to_message.from_user.id != me.id:
                return

        mentioned_ids = set()
        if message.entities:
            for ent in message.entities:
                if ent.type.name == "TEXT_MENTION" and ent.user:
                    mentioned_ids.add(ent.user.id)

        uname = (me.username or "").lower()
        bot_mentioned = bool(uname and f"@{uname}" in text.lower())
        if me.id in mentioned_ids:
            bot_mentioned = True

        reply_to_bot = bool(
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == me.id
        )

        plain = (
            not message.reply_to_message
            and not mentioned_ids
            and not (uname and f"@{uname}" in text.lower())
        )

        if not (reply_to_bot or bot_mentioned or plain):
            return
    else:
        try:
            me = await client.get_me()
            if message.from_user.id == me.id:
                return
        except Exception:
            pass

    try:
        me = await client.get_me()
        if message.from_user.id == me.id:
            return
    except Exception:
        pass

    ans = await _ask(message.from_user.id, text)
    try:
        await message.reply_text(ans)
    except Exception:
        pass
