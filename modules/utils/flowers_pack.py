"""
Premium Flower Pack 50+
  .rose .lotus .gulab .propose .flowerrain ...
  .flowerlist

Dot → bloom animation + flirty end line (premium).
"""
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!", "/"]
DELAY = 0.55


# cmd -> (grow_frames, final_caption)
FLOWERS: dict[str, tuple[list[str], str]] = {
    "rose": (
        ["·", "•", "●", "🌱", "🌿", "🌷", "🌹"],
        "🌹 <b>Red Rose For You</b> 🌹\n<i>Sirf tere liye khili hai…</i>",
    ),
    "lotus": (
        ["·", "💧", "🌱", "🌸", "🪷"],
        "🪷 <b>Lotus</b> 🪷\n<i>Pure jaise tum — kamal.</i>",
    ),
    "gulab": (
        ["·", "•", "🌹", "🌹🌹"],
        "🌹 <b>Gulab</b> 🌹\n<i>Jaan, yeh gulab tera hai.</i>",
    ),
    "sunflower": (
        ["·", "🌱", "🌿", "🌻", "🌻☀️"],
        "🌻 <b>Sunflower</b> 🌻\n<i>Tu mera suraj hai ☀️</i>",
    ),
    "tulip": (
        ["·", "🌱", "🌷", "🌷🌷"],
        "🌷 <b>Tulip</b> 🌷\n<i>Kitni pyari lagti ho…</i>",
    ),
    "lily": (
        ["·", "•", "🌿", "🤍"],
        "🤍 <b>Lily</b> 🤍\n<i>Cute si lily — tumhari tarah.</i>",
    ),
    "jasmine": (
        ["·", "· ·", "🌿", "🤍🌸"],
        "🤍 <b>Jasmine / Chameli</b>\n<i>Khushbu tumhari yaad ki.</i>",
    ),
    "chameli": (
        ["·", "🌿", "🤍", "🌸"],
        "🤍 <b>Chameli</b>\n<i>Raat bhi khushbu maangti hai.</i>",
    ),
    "marigold": (
        ["·", "🌼", "🧡", "🏵️"],
        "🧡 <b>Genda / Marigold</b>\n<i>Desi swag, full colour.</i>",
    ),
    "genda": (
        ["·", "🌼", "🧡🧡"],
        "🧡 <b>Genda Phool</b>\n<i>Haldi-rose vibes.</i>",
    ),
    "hibiscus": (
        ["·", "🌱", "🌺", "🌺❤️"],
        "🌺 <b>Gudhal / Hibiscus</b>\n<i>Laal laal dil.</i>",
    ),
    "lavender": (
        ["·", "🌿", "💜", "💜💜"],
        "💜 <b>Lavender</b>\n<i>Teri yaadon jaisa soft.</i>",
    ),
    "orchid": (
        ["·", "•", "🌸", "💜"],
        "🌸 <b>Orchid</b>\n<i>Rare ho tum — meri tarah.</i>",
    ),
    "daisy": (
        ["·", "•", "🌼", "🌼🌼"],
        "🌼 <b>Daisy</b>\n<i>Simple & cute — bilkul tum.</i>",
    ),
    "daffodil": (
        ["·", "🌱", "💛", "🌼"],
        "🌼 <b>Daffodil</b>\n<i>Nayi subah, naya dil.</i>",
    ),
    "poppy": (
        ["·", "🌱", "🌺", "❤️"],
        "🌺 <b>Poppy</b>\n<i>Thoda nasha… tera.</i>",
    ),
    "carnation": (
        ["·", "•", "💗", "🌸"],
        "💗 <b>Carnation</b>\n<i>Love you forever.</i>",
    ),
    "cherry": (
        ["·", "🌱", "🌸", "🌸🌸"],
        "🌸 <b>Cherry Blossom</b>\n<i>Soft pink feelings 🇯🇵</i>",
    ),
    "iris": (
        ["·", "•", "💜", "🌸"],
        "💜 <b>Iris</b>\n<i>Aankhon jaisi depth.</i>",
    ),
    "peony": (
        ["·", "🌱", "🌸", "💖"],
        "💖 <b>Peony</b>\n<i>Full bloom, full heart.</i>",
    ),
    "bluebell": (
        ["·", "•", "💙", "🔔"],
        "💙 <b>Bluebell</b>\n<i>Halka sa jingle, tera naam.</i>",
    ),
    "magnolia": (
        ["·", "🌱", "🤍", "🌸"],
        "🤍 <b>Magnolia</b>\n<i>Classy & calm.</i>",
    ),
    "dahlia": (
        ["·", "•", "🌺", "🧡"],
        "🌺 <b>Dahlia</b>\n<i>Bold beauty.</i>",
    ),
    "lilac": (
        ["·", "🌿", "💜💜"],
        "💜 <b>Lilac</b>\n<i>Spring in your smile.</i>",
    ),
    "mogra": (
        ["·", "· ·", "🤍", "🌸"],
        "🤍 <b>Mogra</b>\n<i>Shaam ki khushbu.</i>",
    ),
    "kamal": (
        ["·", "💧", "🌱", "🪷"],
        "🪷 <b>Kamal</b>\n<i>Kechad se upar — strong.</i>",
    ),
    "champa": (
        ["·", "•", "🤍", "🌸"],
        "🌸 <b>Champa</b>\n<i>Raat ko bhi mehekti ho.</i>",
    ),
    "palash": (
        ["·", "🔥", "🧡", "🌺"],
        "🧡 <b>Palash</b>\n<i>Jungle fire colour.</i>",
    ),
    "gulmohar": (
        ["·", "🔥", "❤️", "🌳"],
        "🌳 <b>Gulmohar</b>\n<i>Summer crown.</i>",
    ),
    "bouquet": (
        ["·", "🌷", "🌷🌹", "🌷🌹🌻", "💐"],
        "💐 <b>Bouquet For You</b>\n🌹🌷🌸🌼\n<i>Sab phool tumhare liye.</i>",
    ),
    "garland": (
        ["·", "🌹", "🌹🌹", "📿"],
        "🌹 <b>Mala</b>\n<i>Pehna du kya? 😏</i>",
    ),
    "petals": (
        ["🌸", "🌸  ·", " · 🌸", "🌸 🌸 🌸"],
        "🌸 <b>Petals</b>\n<i>Falling for you…</i>",
    ),
    "bloom": (
        ["·", "🌱", "🌿", "🌺"],
        "🌺 <b>Bloom</b>\n<i>Khil gayi ho tum.</i>",
    ),
    "blossom": (
        ["·", "•", "🌸", "🌸🌸"],
        "🌸 <b>Blossom</b>\n<i>Muskurayi — phool khile.</i>",
    ),
    "garden": (
        ["·", "🌱", "🌿🌸", "🏡"],
        "🏡 <b>Garden</b>\n<i>Tum ho toh garden hai.</i>",
    ),
    "redrose": (
        ["·", "🌹", "🌹🌹", "🌹🌹🌹"],
        "🌹 <b>RED ROSE</b> 🌹\n<i>I love you so much.</i>",
    ),
    "whiterose": (
        ["·", "🤍", "🤍🌹"],
        "🤍 <b>White Rose</b>\n<i>Pure love.</i>",
    ),
    "blackrose": (
        ["·", "🖤", "🖤🌹"],
        "🖤 <b>Black Rose</b>\n<i>Mysterious love.</i>",
    ),
    "pinkrose": (
        ["·", "💗", "💗🌹"],
        "💗 <b>Pink Rose</b>\n<i>Cute love.</i>",
    ),
    "yellowrose": (
        ["·", "💛", "💛🌹"],
        "💛 <b>Yellow Rose</b>\n<i>Dosti wala pyaar.</i>",
    ),
    "roseheart": (
        ["❤️", "🌹", "❤️🌹❤️"],
        "🌹+❤️=<b>You</b>\n  🌹❤️🌹",
    ),
    "rosebouquet": (
        ["🌹", "🌹🌹", "💐", "💐🌹"],
        "💐 <b>100 Roses</b>\n<i>Gin nahi paogi…</i>",
    ),
    "propose": (
        ["·", "•", "🌹", "🌹💍", "💍"],
        "💍 <b>Will You Be Mine?</b> 🌹\n🌹❤️🌹",
    ),
    "kissflower": (
        ["·", "🌹", "😘", "🌹😘"],
        "🌹 <b>Flower Kiss</b>\n<i>Muaahh 😘</i>",
    ),
    "hugflower": (
        ["·", "🌹", "🤗", "🌹🤗"],
        "🌹 <b>Flower Hug</b>\n<i>Ek phool ke saath jhappi.</i>",
    ),
    "missyou": (
        ["·", "💭", "🌹", "🌹😢"],
        "🌹 <b>I Miss You</b>\n<i>Phool bhi udaas hai.</i>",
    ),
    "jaan": (
        ["·", "❤️", "🌹", "🌹❤️"],
        "🌹 <b>Meri Jaan</b>\n<i>Tu hai toh phool hai.</i>",
    ),
    "cutie": (
        ["·", "🌷", "😊", "🌷💕"],
        "🌷 <b>Cutie</b>\n<i>Cute sa phool.</i>",
    ),
    "princess": (
        ["·", "🌸", "👸", "👑🌸"],
        "👸🌸 <b>Princess</b>\n<i>Phoolon ki rani.</i>",
    ),
    "valentine": (
        ["·", "💘", "🌹", "💘🌹"],
        "💘 <b>Be My Valentine?</b> 🌹",
    ),
    "forever": (
        ["·", "🌹", "♾️", "🌹♾️"],
        "🌹 <b>Forever Rose</b>\n<i>Kabhi na murjhaane wala.</i>",
    ),
    "myrose": (
        ["·", "🌹", "🔒🌹"],
        "🌹 <b>My Rose</b>\n<i>Only mine ❤️</i>",
    ),
    "wilted": (
        ["🌹", "🌹🥀", "🥀", "·"],
        "🥀 <b>Wilted</b>\n<i>Bina tere murjha gayi…</i>",
    ),
    "falling": (
        ["🌸", " 🌸", "🌸  🌸", "🌸🌸🌸"],
        "🌸 <b>Falling Petals</b>\n<i>Bas tere naam pe.</i>",
    ),
    "growing": (
        ["·", "🌱", "🌿", "🌿🌸", "🌸"],
        "🌱 <b>Growing</b>\n<i>Humari kahani khil rahi hai.</i>",
    ),
    "mogra2": (
        ["·", "🤍", "🌸🤍"],
        "🤍 <b>Mogra Night</b>\n<i>Khushbu + raat + tum.</i>",
    ),
    "raatrani": (
        ["·", "🌙", "🤍", "🌸"],
        "🌙 <b>Raat Rani</b>\n<i>Raat mein khilti ho.</i>",
    ),
    "sadabahar": (
        ["·", "🌱", "💗", "🌺"],
        "🌺 <b>Sadabahar</b>\n<i>Hamesha fresh.</i>",
    ),
    "aparajita": (
        ["·", "💙", "🌸💙"],
        "💙 <b>Aparajita</b>\n<i>Haar nahi maanti.</i>",
    ),
    "special": (
        ["·", "✨", "🌸", "🌸✨"],
        "🌸 <b>Special</b>\n<i>Mere special person ke liye.</i>",
    ),
    "beautiful": (
        ["·", "🌺", "😍", "🌺💕"],
        "🌺 <b>You Are Beautiful</b>\n<i>Phool se bhi zyada.</i>",
    ),
}


async def _bloom(message: Message, frames: list[str], final: str):
    try:
        msg = await message.reply_text(f"<code>{frames[0]}</code>")
    except Exception:
        return
    for f in frames[1:]:
        await asyncio.sleep(DELAY)
        try:
            await msg.edit_text(f"<code>{f}</code>")
        except Exception:
            return
    await asyncio.sleep(0.45)
    try:
        await msg.edit_text(
            f"━━━━━━━━━━━━━━\n{final}\n━━━━━━━━━━━━━━"
        )
    except Exception:
        pass


def _register():
    for name, (frames, final) in FLOWERS.items():
        async def _cmd(client, message: Message, fr=frames, fin=final):
            await _bloom(message, fr, fin)

        _cmd.__name__ = f"flower_{name}"
        app.on_message(filters.command(name, prefixes=PREFIXES))(sudo_only(_cmd))


_register()


@app.on_message(filters.command("flowerrain", prefixes=PREFIXES))
@sudo_only
async def flowerrain_cmd(client, message: Message):
    frames = ["🌹", "🌹🌷", "🌹🌷🌸", "🌹🌷🌸🌼", "🌹🌷🌸🌼🌺"]
    final = "🌺 <b>Flower Rain</b>\n<i>Falling for you…</i>"
    await _bloom(message, frames, final)


@app.on_message(filters.command("rosefall", prefixes=PREFIXES))
@sudo_only
async def rosefall_cmd(client, message: Message):
    frames = ["🌹", "  🌹", "    🌹", "      🌹"]
    final = "🌹 <b>Rose Fall</b>\n<i>Tum par gir raha hai ❤️</i>"
    await _bloom(message, frames, final)


@app.on_message(filters.command(["flowerlist", "flowers"], prefixes=PREFIXES))
@sudo_only
async def flowerlist_cmd(client, message: Message):
    names = " ".join(f".{k}" for k in sorted(FLOWERS.keys()))
    await message.reply_text(
        "🌸 <b>FLOWER PACK 50+</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"<code>{names}</code>\n\n"
        f".flowerrain .rosefall\n"
        f"Total: <b>{len(FLOWERS) + 2}</b>\n"
        "━━━━━━━━━━━━━━\n"
        "<i>Premium bloom · flirty captions</i>"
    )
