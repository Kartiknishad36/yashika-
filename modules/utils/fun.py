"""Fun ASCII animations — rose/cat/hacker/butterfly/love/etc."""
import asyncio

from pyrogram.types import Message
from pyrogram.errors import FloodWait

from core.clients import app
from modules.owner.sudoers import ub_cmd

CAT_ANIMATION = ["🐈",
    "🐈\nWalking...",
    "🐈\nWalking...",
    "╱|、\n( .. )\n |、˜〵\nじしˍ,)ノ",
    "╱|、\n( > < )\n |、˜〵\nじしˍ,)ノ",
    "╱|、\n(˚ˎ 。7\n |、˜〵\nじしˍ,)ノ",
    "╱|、\n(˚ˎ 。7  < Meow! 🎵\n |、˜〵\nじしˍ,)ノ" ]
FLOWER_BLOOM = ["🌱", "🌿\n🌿\n🌿", "🌷\n🌷\n🌷", "🌹\n🌹\n🌹"]
ROSE_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⢔⣒⠂⣀⣀⣤⣄⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣴⣿⠋⢠⣟⡼⣷⠼⣆⣼⢇⣿⣄⠱⣄
⠀⠀⠀⠀⠀⠀⠀⠹⣿⡀⣆⠙⠢⠐⠉⠉⣴⣾⣽⢟⡰⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣦⠀⠤⢴⣿⠿⢋⣴⡏⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡙⠻⣿⣶⣦⣭⣉⠁⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷⠀⠈⠉⠉⠉⠉⠇⡟⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⣘⣦⣀⠀⠀⣀⡴⠊⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⢻⣿⣿⣿⣿⠻⣧⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠫⣿⠉⠻⣇⠘⠓⠂⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢶⣾⣿⣿⣿⣿⣿⣶⣄⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣧⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠙⠻⢿⣿⣿⠿⠛⣄⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣷⠂⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⠀⠀⠀
"""
HACKER_ART = r"""
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠈⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⢀⣠⣤⣤⣤⣤⣄⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠾⣿⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⣤⣶⣤⣉⣿⣿⡯⣀⣴⣿⡗⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⡈⠀⠀⠉⣿⣿⣶⡉⠀⠀⣀⡀⠀⠀⠀⢻⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⢸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠉⢉⣽⣿⠿⣿⡿⢻⣯⡍⢁⠄⠀⠀⠀⣸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠐⡀⢉⠉⠀⠠⠀⢉⣉⠀⡜⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠿⠁⠀⠀⠀⠘⣤⣭⣟⠛⠛⣉⣁⡜⠀⠀⠀⠀⠀⠛⠿⣿⣿⣿
⡿⠟⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⡀⠀⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
ERROR_ART = r"""
▒▒▒▒▒▒▒▒▄▄▄▄▄▄▄▄▒▒▒▒▒▒
▒▒█▒▒▒▄██████████▄▒▒▒▒
▒█▐▒▒▒████████████▒▒▒▒
▒▌▐▒▒██▄▀██████▀▄██▒▒▒
▐┼▐▒▒██▄▄▄▄██▄▄▄▄██▒▒▒
▐┼▐▒▒██████████████▒▒▒
▐▄▐████─▀▐▐▀█─█─▌▐██▄▒
▒▒█████──────────▐███▌
▒▒█▀▀██▄█─▄───▐─▄███▀▒
▒▒█▒▒███████▄██████▒▒▒
▒▒▒▒▒██████████████▒▒▒
▒▒▒▒▒█████████▐▌██▌▒▒▒
▒▒▒▒▒▐▀▐▒▌▀█▀▒▐▒█▒▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▐▒▒▒▒▌▒▒▒▒▒
"""
FUCK_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⢀⡤⠤⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣾⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡾⠋⠻⡇⠀⠀⢸⣧⣀⡀⠀⠀⠀⠀
⠀⠀⢀⣾⠁⠀⠀⡇⠀⠀⢸⠁⠀⢹⣀⠀⠀⠀
⢀⡴⠋⡟⠀⠀⢠⡇⠀⠀⢸⠀⠀⠀⡇⠉⢆⠀
⡎⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⠈⣆
⢷⡀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⠀⠻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾
⠀⠀⠈⠻⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠁
⠀⠀⠀⠀⠈⣷⠀⠀⠀⠀⠀⠀⠀⠀⢰⠋⠀⠀
⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⠀
⠀⠀⠀⠀⠀⠛⠒⠒⠒⠒⠒⠒⠒⠚⠃⠀⠀⠀
"""
BUTTERFLY_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢔⣶⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀⠀⡼⠗⡿⣾⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⣀⠀⠀⠀⡇⢀⡼⠓⡞⢩⣯⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⠀⠀⠀⠀⠉⠳⢜⠰⡹⠁⢰⠃⣩⣿⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣿⠿⣉⣩⠛⠲⢶⡠⢄⢙⣣⠃⣰⠗⠋⢀⣯⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣯⣠⠬⠦⢤⣀⠈⠓⢽⣿⢔⣡⡴⠞⠻⠙⢳⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣵⣳⠖⠉⠉⢉⣩⣵⣿⣿⣒⢤⣴⠤⠽⣬⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢻⣟⠟⠋⢡⡎⢿⢿⠳⡕⢤⡉⡷⡽⠁
⣧⢮⢭⠛⢲⣦⣀⠀⠀⠀⠀⡀⠀⠀⠀⡾⣥⣏⣖⡟⠸⢺⠀⠀⠈⠙⠋⠁⠀⠀
⠈⠻⣶⡛⠲⣄⠀⠙⠢⣀⠀⢇⠀⠀⠀⠘⠿⣯⣮⢦⠶⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢻⣿⣥⡬⠽⠶⠤⣌⣣⣼⡔⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢠⣿⣧⣤⡴⢤⡴⣶⣿⣟⢯⡙⠒⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠘⣗⣞⣢⡟⢋⢜⣿⠛⡿⡄⢻⡮⣄⠈⠳⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠻⠮⠴⠵⢋⣇⡇⣷⢳⡀⢱⡈⢋⠛⣄⣹⣲⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣱⡇⣦⢾⣾⠿⠟⠿⠷⠷⣻⠧⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⠽⠞⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
YOURMOM_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣾⣶⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠐⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⡿⠟⣡⣴⣦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀
⠀⣠⣤⣴⣶⣿⡀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠈⠻⢿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀
⢸⣿⣿⣿⣿⣿⡅⠀⠀⠀⠀⠀⢸⣿⣿⣿⣀⣀⣀⡙⢿⣿⣿⣿⣿⡄⠀⠀⠀⠀
⠸⣿⣿⣿⣿⠟⣠⣤⣴⣶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⡄⢹⣿⣿⣿⠀⠀⠀⠀⠀
⠀⠈⠉⠉⠁⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⢸⣿⣿⣿⠄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⣿⡿⠛⠛⠛⠛⠛⠛⠛⠛⣿⣿⣿⣯⢸⣿⣿⣿⠂⠀⠀⠀⠀
⢀⣤⣤⣤⣤⣤⣿⣿⣗⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣾⣿⣿⣿⣷⣶⣶⣶⣄
⠸⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟
"""
MYSON_ART = r"""
  ⠀     (\__/)
      (•ㅅ•)      Don’t talk to
   ＿ノヽ ノ＼＿      me or my son
/　/ ⌒Ｙ⌒ Ｙ  ヽ     ever again.
( 　(三ヽ人　 /　  |
|　ﾉ⌒＼ ￣￣ヽ   ノ
ヽ＿＿＿＞､＿_／
      ｜( 王 ﾉ〈  (\__/)
      /ﾐ`ー―彡\  (•ㅅ•)
     / ╰    ╯ \ /    \>
"""


async def smart_edit(message: Message, text: str, sleep_time: float = 0.5):
    try:
        await message.edit_text(text)
        await asyncio.sleep(sleep_time)
    except FloodWait as e:
        if e.value < 8:
            await asyncio.sleep(e.value)
            try:
                await message.edit_text(text)
                await asyncio.sleep(sleep_time)
            except Exception:
                pass
    except Exception:
        pass


async def draw_art(message: Message, art_var: str, header: str = "", footer: str = "", chunk_size: int = 4):
    lines = art_var.strip().split("\n")
    current = ""
    for i, line in enumerate(lines):
        current += line + "\n"
        if (i + 1) % chunk_size == 0 or i == len(lines) - 1:
            if header:
                display = f"<b>{header}</b>\n<code>{current}</code>"
            else:
                display = f"<code>{current}</code>"
            if i == len(lines) - 1 and footer:
                display += f"\n\n<b>{footer}</b>"
            await smart_edit(message, display, 0.45)


@app.on_message(ub_cmd("cat"), group=-8)
async def cat_cmd(client, message: Message):
    m = await message.reply_text("🐈")
    for frame in CAT_ANIMATION:
        await smart_edit(m, f"<code>{frame}</code>", 0.4)


@app.on_message(ub_cmd("rose"), group=-8)
async def rose_cmd(client, message: Message):
    m = await message.reply_text("🌱")
    for frame in FLOWER_BLOOM:
        await smart_edit(m, f"<code>{frame}</code>", 0.55)
    await draw_art(m, ROSE_ART, footer="🌹 FOR YOU!")


@app.on_message(ub_cmd("hacker", "hack"), group=-8)
async def hacker_cmd(client, message: Message):
    m = await message.reply_text("💻 Hacking System...")
    await draw_art(m, HACKER_ART, footer="💻 SYSTEM HACKED!")


@app.on_message(ub_cmd("error"), group=-8)
async def error_cmd(client, message: Message):
    m = await message.reply_text("⚠️ SYSTEM CRASHING...")
    await draw_art(m, ERROR_ART, footer="⚠️ FATAL ERROR DETECTED!")


@app.on_message(ub_cmd("fuck"), group=-8)
async def fuck_cmd(client, message: Message):
    m = await message.reply_text("🖕 Loading...")
    await draw_art(m, FUCK_ART, footer="🖕 FUCK YOU!")


@app.on_message(ub_cmd("butterfly"), group=-8)
async def butterfly_cmd(client, message: Message):
    m = await message.reply_text("🦋 Drawing...")
    await draw_art(m, BUTTERFLY_ART, footer="🦋 Fly High!")


@app.on_message(ub_cmd("love", "heart"), group=-8)
async def love_cmd(client, message: Message):
    frames = [
        "❤️🧡💛💚💙💜🖤🤍🤎\n❤️🧡💛💚💙💜🖤🤍🤎\n❤️🧡💛💚💙💜🖤🤍🤎",
        "🧡💛💚💙💜🖤🤍🤎❤️\n🧡💛💚💙💜🖤🤍🤎❤️\n🧡💛💚💙💜🖤🤍🤎❤️",
        "💛💚💙💜🖤🤍🤎❤️🧡\n💛💚💙💜🖤🤍🤎❤️🧡\n💛💚💙💜🖤🤍🤎❤️🧡",
        "💚💙💜🖤🤍🤎❤️🧡💛\n💚💙💜🖤🤍🤎❤️🧡💛\n💚💙💜🖤🤍🤎❤️🧡💛",
        "💙💜🖤🤍🤎❤️🧡💛💚\n💙💜🖤🤍🤎❤️🧡💛💚\n💙💜🖤🤍🤎❤️🧡💛💚",
        "💜🖤🤍🤎❤️🧡💛💚💙\n💜🖤🤍🤎❤️🧡💛💚💙\n💜🖤🤍🤎❤️🧡💛💚💙",
        "🖤🤍🤎❤️🧡💛💚💙💜\n🖤🤍🤎❤️🧡💛💚💙💜\n🖤🤍🤎❤️🧡💛💚💙💜",
        "🤍🤎❤️🧡💛💚💙💜🖤\n🤍🤎❤️🧡💛💚💙💜🖤\n🤍🤎❤️🧡💛💚💙💜🖤",
        "🤎❤️🧡💛💚💙💜🖤🤍\n🤎❤️🧡💛💚💙💜🖤🤍\n🤎❤️🧡💛💚💙💜🖤🤍",
        "❤️❤️❤️❤️❤️❤️❤️❤️❤️\n❤️❤️❤️❤️❤️❤️❤️❤️❤️\n❤️❤️❤️❤️❤️❤️❤️❤️❤️",
        "<b>I LOVE YOU ❤️</b>",
    ]
    m = await message.reply_text("❤️")
    for frame in frames:
        await smart_edit(m, frame, 0.55)


@app.on_message(ub_cmd("yourmom"), group=-8)
async def yourmom_cmd(client, message: Message):
    m = await message.reply_text("🤱 Searching...")
    await draw_art(m, YOURMOM_ART, header="🤱 VS YOUR MOM", footer="Done")


@app.on_message(ub_cmd("myson"), group=-8)
async def myson_cmd(client, message: Message):
    m = await message.reply_text("🐰 Summoning...")
    await draw_art(m, MYSON_ART, footer="🐰 Me & My Son")
