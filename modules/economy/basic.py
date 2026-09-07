"""
Economy: /bal /daily /pfp /protect /rob /kill
Runs on BOT client so group members can use it (not only userbot owner).
"""
import random
import time
from pyrogram import filters
from pyrogram.types import Message

from core.clients import bot
from database.mongo import eco_get, eco_set, eco_add_balance, eco_try_daily

if bot is None:
    raise RuntimeError("modules.economy.basic requires BOT_TOKEN")

PREFIXES = ["/", ".", "!"]


def _rank(balance: int) -> int:
    return max(1, 20000 - int(balance) // 10)


def _fmt_time(seconds: int) -> str:
    h, r = divmod(max(0, seconds), 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


@bot.on_message(filters.command(["bal", "balance", "stats"], prefixes=PREFIXES))
async def bal_cmd(client, message: Message):
    target = message.from_user
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    if not target:
        return

    st = await eco_get(target.id)
    bal = int(st.get("balance", 0))
    gems = float(st.get("gems", 0))
    kills = int(st.get("kills", 0))
    prot = int(st.get("protect_until", 0))
    prot_txt = "Yes 🛡" if prot > time.time() else "No"

    name = target.mention or target.first_name or str(target.id)
    await message.reply_text(
        f"📊 <b>STATS — {name}</b>\n\n"
        f"💰 Balance: <code>{bal}</code>\n"
        f"🏆 Rank: <code>{_rank(bal)}</code>\n"
        f"💎 Gems: <code>{gems:.2f}</code>\n"
        f"⚔ Kills: <code>{kills}</code>\n"
        f"🛡 Protect: {prot_txt}"
    )


@bot.on_message(filters.command("daily", prefixes=PREFIXES))
async def daily_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return
    ok, val, bal = await eco_try_daily(user.id)
    if not ok:
        await message.reply_text(
            f"⏳ Daily already claimed.\nTry again in <b>{_fmt_time(val)}</b>."
        )
        return
    await message.reply_text(
        f"🎁 Daily reward: <b>+{val}</b> coins\n"
        f"💰 New balance: <code>{bal}</code>"
    )


@bot.on_message(filters.command("pfp", prefixes=PREFIXES))
async def pfp_cmd(client, message: Message):
    target = message.from_user
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    if not target:
        return
    try:
        photos = [p async for p in client.get_chat_photos(target.id, limit=1)]
        if not photos:
            await message.reply_text("No profile photo.")
            return
        await message.reply_photo(
            photos[0].file_id,
            caption=f"🖼 PFP — {target.mention}",
        )
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@bot.on_message(filters.command("protect", prefixes=PREFIXES))
async def protect_cmd(client, message: Message):
    """1 hour shield — costs 100 coins."""
    user = message.from_user
    if not user:
        return
    cost = 100
    st = await eco_get(user.id)
    if int(st.get("balance", 0)) < cost:
        await message.reply_text(f"❌ Need {cost} coins for protect.")
        return
    if int(st.get("protect_until", 0)) > time.time():
        left = int(st["protect_until"] - time.time())
        await message.reply_text(f"🛡 Already protected for {_fmt_time(left)}.")
        return

    new_bal = await eco_add_balance(user.id, -cost)
    until = int(time.time()) + 3600
    await eco_set(user.id, protect_until=until)
    await message.reply_text(
        f"🛡 Protected for <b>1 hour</b>\n💰 Balance: <code>{new_bal}</code>"
    )


@bot.on_message(filters.command("rob", prefixes=PREFIXES))
async def rob_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("Reply to someone: `/rob`")
        return

    victim = message.reply_to_message.from_user
    if victim.id == user.id:
        await message.reply_text("Khud ko rob nahi kar sakte.")
        return
    if victim.is_bot:
        await message.reply_text("Bots se rob nahi hota.")
        return

    me = await eco_get(user.id)
    them = await eco_get(victim.id)

    if int(them.get("protect_until", 0)) > time.time():
        await message.reply_text("🛡 Target protected hai.")
        return
    if int(them.get("balance", 0)) < 50:
        await message.reply_text("Target ke paas enough coins nahi.")
        return

    # 55% success
    if random.random() < 0.55:
        amount = random.randint(20, min(150, int(them["balance"]) // 4 or 20))
        await eco_add_balance(victim.id, -amount)
        new_bal = await eco_add_balance(user.id, amount)
        await message.reply_text(
            f"💀 Rob success! +<b>{amount}</b> from {victim.mention}\n"
            f"💰 Balance: <code>{new_bal}</code>"
        )
    else:
        fine = random.randint(10, 40)
        new_bal = await eco_add_balance(user.id, -fine)
        await message.reply_text(
            f"🚨 Caught! Fine <b>-{fine}</b>\n💰 Balance: <code>{new_bal}</code>"
        )


@bot.on_message(filters.command("kill", prefixes=PREFIXES))
async def kill_cmd(client, message: Message):
    """Fun kill — +1 kill, small coin steal chance."""
    user = message.from_user
    if not user:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("Reply to someone: `/kill`")
        return

    victim = message.reply_to_message.from_user
    if victim.id == user.id:
        await message.reply_text("...")
        return

    them = await eco_get(victim.id)
    if int(them.get("protect_until", 0)) > time.time():
        await message.reply_text("🛡 Target protected.")
        return

    st = await eco_get(user.id)
    kills = int(st.get("kills", 0)) + 1
    await eco_set(user.id, kills=kills)

    bonus = 0
    if random.random() < 0.4 and int(them.get("balance", 0)) >= 30:
        bonus = random.randint(5, 30)
        await eco_add_balance(victim.id, -bonus)
        await eco_add_balance(user.id, bonus)

    extra = f"\n💰 Loot +{bonus}" if bonus else ""
    await message.reply_text(
        f"⚔ {user.mention} killed {victim.mention}\n"
        f"Kills: <code>{kills}</code>{extra}"
  )
