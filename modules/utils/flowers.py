"""
50 flower name animations — .rose .lotus .gulab ...
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

FLOWERS = {
    "rose": (["·", "•", "●", "🌱", "🌿", "🌷", "🌹"], "🌹 Red Rose For You 🌹"),
    "lotus": (["·", "· ·", "💧", "🌱", "🌸", "🪷"], "🪷 Lotus / Kamal 🪷"),
    "tulip": (["·", "🌱", "🌱🌱", "🌷", "🌷🌷"], "🌷 Tulip 🌷"),
    "sunflower": (["·", "🌱", "🌿", "🌻", "🌻☀️"], "🌻 Sunflower 🌻"),
    "lily": (["·", "•", "🌿", "🌼"], "🤍 White Lily 🤍"),
    "jasmine": (["·", "· ·", "🌿", "🤍", "🌸🤍"], "🤍 Jasmine / Chameli 🤍"),
    "chameli": (["·", "· ·", "🌿", "🤍", "🌸"], "🤍 Chameli 🤍"),
    "daisy": (["·", "•", "🌼", "🌼🌼"], "🌼 Daisy 🌼"),
    "hibiscus": (["·", "🌱", "🌺", "🌺🌺"], "🌺 Hibiscus 🌺"),
    "marigold": (["·", "🌼", "🌼🌼", "🧡"], "🧡 Marigold 🧡"),
    "genda": (["·", "🌼", "🧡🧡"], "🧡 Genda Phool 🧡"),
    "orchid": (["·", "•", "🌸", "💜🌸"], "🌸 Orchid 🌸"),
    "cherry": (["·", "🌱", "🌸", "🌸🌸"], "🌸 Cherry Blossom 🌸"),
    "lavender": (["·", "🌿", "💜", "💜💜"], "💜 Lavender 💜"),
    "poppy": (["·", "🌱", "🌺", "❤️"], "❤️ Poppy ❤️"),
    "iris": (["·", "•", "💜", "🌸"], "💜 Iris 💜"),
    "daffodil": (["·", "🌱", "💛", "🌼"], "🌼 Daffodil 🌼"),
    "carnation": (["·", "•", "💗", "🌸"], "💗 Carnation 💗"),
    "peony": (["·", "🌱", "🌸", "💖"], "💖 Peony 💖"),
    "bluebell": (["·", "•", "💙", "🔔"], "💙 Bluebell 💙"),
    "magnolia": (["·", "🌱", "🤍", "🌸"], "🤍 Magnolia 🤍"),
    "dahlia": (["·", "•", "🌺", "🧡"], "🌺 Dahlia 🌺"),
    "zinnia": (["·", "🌱", "🌼", "💛"], "🌼 Zinnia 🌼"),
    "aster": (["·", "•", "💜", "🌸"], "🌸 Aster 🌸"),
    "begonia": (["·", "🌱", "💗", "🌺"], "💗 Begonia 💗"),
    "camellia": (["·", "•", "❤️", "🌸"], "🌸 Camellia 🌸"),
    "chrys": (["·", "🌱", "💛", "🌼"], "🌼 Chrysanthemum 🌼"),
    "freesia": (["·", "•", "💛", "🌸"], "🌸 Freesia 🌸"),
    "gardenia": (["·", "🌱", "🤍", "🌼"], "🤍 Gardenia 🤍"),
    "gladiolus": (["·", "•", "❤️", "🌺"], "🌺 Gladiolus 🌺"),
    "heather": (["·", "🌿", "💜"], "💜 Heather 💜"),
    "hyacinth": (["·", "•", "💙", "🌸"], "💙 Hyacinth 💙"),
    "lilac": (["·", "🌿", "💜💜"], "💜 Lilac 💜"),
    "mogra": (["·", "· ·", "🤍", "🌸"], "🤍 Mogra 🤍"),
    "gulab": (["·", "•", "●", "🌹", "🌹🌹"], "🌹 Gulab 🌹"),
    "kamal": (["·", "💧", "🌱", "🪷"], "🪷 Kamal 🪷"),
    "belapatra": (["·", "🌿", "🤍"], "🤍 Bela 🤍"),
    "raatrani": (["·", "🌙", "🤍", "🌸"], "🌙 Raat Rani 🌸"),
    "sadabahar": (["·", "🌱", "💗", "🌺"], "🌺 Sadabahar 🌺"),
    "aparajita": (["·", "•", "💙", "🌸"], "💙 Aparajita 💙"),
    "palash": (["·", "🔥", "🧡", "🌺"], "🧡 Palash 🌺"),
    "gulmohar": (["·", "🔥", "❤️", "🌳"], "🌳 Gulmohar ❤️"),
    "kewda": (["·", "🌿", "💛"], "💛 Kewda 💛"),
    "champa": (["·", "•", "🤍", "🌸"], "🌸 Champa 🌸"),
    "bouquet": (["·", "🌷", "🌷🌹", "🌷🌹🌻", "💐"], "💐 Full Bouquet 💐"),
    "wilted": (["🌹", "🌹🌹", "🥀", "🥀·"], "🥀 Wilted Rose 🥀"),
    "falling": (["🌸", "🌸  ·", " · 🌸", "🌸🌸🌸"], "🌸 Falling Petals 🌸"),
    "growing": (["·", "🌱", "🌿", "🌿🌸", "🌸"], "🌱 Growing Flower 🌸"),
    "proposal": (["·", "•", "🌱", "🌹", "🌹💍"], "💍 Will You Marry Me? 🌹"),
}


async def _anim(message: Message, frames, end, delay=0.4):
    msg = await message.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(delay)
        try:
            await msg.edit_text(f)
        except Exception:
            return
    await asyncio.sleep(0.5)
    try:
        await msg.edit_text(end)
    except Exception:
        pass


def _make(cmd, frames, end):
    async def handler(client, message: Message):
        await _anim(message, frames, end)
    handler.__name__ = f"flower_{cmd}"
    return handler


for _cmd, (_frames, _end) in FLOWERS.items():
    app.on_message(filters.command(_cmd, prefixes=PREFIXES))(
        sudo_only(_make(_cmd, _frames, _end))
)
