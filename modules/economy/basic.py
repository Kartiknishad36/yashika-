"""Economy on userbot — no BOT_TOKEN required."""
import random
import time
from pyrogram.types import Message

from core.clients import app
from database.mongo import eco_get, eco_set, eco_add_balance, eco_try_daily
from modules.owner.sudoers import ub_cmd


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


@app.on_message(ub_cmd("bal", "balance", "stats"))
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
    prot_txt = "Yes" if prot > time.time() else "No"
    name = target.mention or target.first_name or str(target.id)
    await message.reply_text(
        f"<b>STATS — {name}</b>\n"
        f"Balance: <code>{bal}</code>\n"
        f"Rank: <code>{_rank(bal)}</code>\n"
        f"Gems: <code>{gems:.2f}</code>\n"
        f"Kills: <code>{kills}</code>\n"
        f"Protect: {prot_txt}"
    )


@app.on_message(ub_cmd("daily"))
async def daily_cmd(client, message: Message):
    user = message.from_user
    if not user:
        return
    ok, val, bal = await eco_try_daily(user.id)
    if not ok:
        await message.reply_text(f"Daily claimed. Wait <b>{_fmt_time(val)}</b>")
        return
    await message.reply_text(f"Daily +<b>{val}</b>\nBalance: <code>{bal}</code>")


@app.on_message(ub_cmd("rob"))
async def rob_cmd(client, message: Message):
    user = message.from_user
    if not user or not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("Reply: <code>.rob</code>")
        return
    victim = message.reply_to_message.from_user
    if victim.id == user.id:
        await message.reply_text("Can't rob self.")
        return
    them = await eco_get(victim.id)
    if int(them.get("protect_until", 0)) > time.time():
        await message.reply_text("Target protected.")
        return
    if int(them.get("balance", 0)) < 50:
        await message.reply_text("Target low balance.")
        return
    if random.random() < 0.55:
        amount = random.randint(20, min(150, max(20, int(them["balance"]) // 4)))
        await eco_add_balance(victim.id, -amount)
        new_bal = await eco_add_balance(user.id, amount)
        await message.reply_text(f"Rob +<b>{amount}</b>\nBalance: <code>{new_bal}</code>")
    else:
        fine = random.randint(10, 40)
        new_bal = await eco_add_balance(user.id, -fine)
        await message.reply_text(f"Caught -{fine}\nBalance: <code>{new_bal}</code>")


@app.on_message(ub_cmd("kill"))
async def kill_cmd(client, message: Message):
    user = message.from_user
    if not user or not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply_text("Reply: <code>.kill</code>")
        return
    victim = message.reply_to_message.from_user
    if victim.id == user.id:
        return
    them = await eco_get(victim.id)
    if int(them.get("protect_until", 0)) > time.time():
        await message.reply_text("Protected.")
        return
    st = await eco_get(user.id)
    kills = int(st.get("kills", 0)) + 1
    await eco_set(user.id, kills=kills)
    bonus = 0
    if random.random() < 0.4 and int(them.get("balance", 0)) >= 30:
        bonus = random.randint(5, 30)
        await eco_add_balance(victim.id, -bonus)
        await eco_add_balance(user.id, bonus)
    extra = f"\nLoot +{bonus}" if bonus else ""
    await message.reply_text(f"{user.mention} killed {victim.mention}\nKills: <code>{kills}</code>{extra}")


print("[economy] OK")
