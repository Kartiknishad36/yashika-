"""Fun ASCII animations — rose/cat/moon/heart + text banners"""
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

MOON_PHASES = [
    "🌑  New Moon...",
    "🌒  Waxing Crescent...",
    "🌓  First Quarter...",
    "🌔  Waxing Gibbous...",
    "🌕  Full Moon rising...",
    "✨ Stars appear...",
]
MOON_ART = r"""
            .          .
     .             *        .
          .     .=======.      *
      *       .  FULL  MOON .        .
           . /    moon    \  .
            |   *     *   |      *
         *   \    night  /   .
              .       .
        .       =======      *
              *         .
         .         *          .
"""

HEART_BUILD = [
    "❤️",
    "  ❤️\n❤️  ❤️",
    "   ❤️\n ❤️  ❤️\n❤️    ❤️",
    "    ❤️❤️\n  ❤️    ❤️\n ❤️      ❤️\n  ❤️    ❤️\n    ❤️❤️",
]
HEART_ART = r"""
     ******       ******
   **      **   **      **
 **          ***          **
**                          **
**                          **
 **                        **
  **                      **
    **                  **
      **              **
        **          **
          **      **
            **  **
              **
"""

OK_ART = r"""
  ___  _  __
 / _ \| |/ /
| |_| |   <
 \___/|_|\_\
"""

VIP_ART = r"""
 __     _____ _____
 \ \   / /_ _|  _ \
  \ \ / / | || |_) |
   \ V /  | ||  __/
    \_/  |___|_|
"""

BOSS_ART = r"""
 ____   ___  ____ ____
| __ ) / _ \/ ___/ ___|
|  _ \| | | \___ \___ \
| |_) | |_| |___) |__) |
|____/ \___/|____/____/
"""

PRO_ART = r"""
 ____  ____   ___
|  _ \|  _ \ / _ \
| |_) | |_) | | | |
|  __/|  _ <| |_| |
|_|   |_| \_\___/
"""

KING_ART = r"""
 _  _____ _   _  ____
| |/ /_ _| \ | |/ ___|
| ' / | ||  \| | |  _
| . \ | || |\  | |_| |
|_|\_\___|_| \_|\____|
"""

YASHIKA_ART = r"""
__   __        _     _ _
\ \ / /_ _ ___| |__ (_) | ____ _
 \ V / _` / __| '_ \| | |/ / _` |
  | | (_| \__ \ | | | |   < (_| |
  |_|\__,_|___/_| |_|_|_|\_\__,_|
"""

WIN_ART = r"""
\ \      / (_)_ __
 \ \ /\ / /| | '_ \
  \ V  V / | | | | |
   \_/\_/  |_|_| |_|
"""

GG_ART = r"""
  ____  ____
 / ___/ ___|
| |  _| |  _
| |_| | |_| |
 \____|\____|
"""

HI_ART = r"""
 _   _ ___
| | | |_ _|
| |_| || |
|  _  || |
|_| |_|___|
"""

BYE_ART = r"""
 ____  __   __ _____
| __ )/ / /\ \ | ____|
|  _ \\ \/  \/ /|  _|
| |_) \  /\  / | |___
|____/ \/  \/  |_____|
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


@app.on_message(ub_cmd("love"), group=-8)
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


@app.on_message(ub_cmd("moon", "chand"), group=-8)
async def moon_cmd(client, message: Message):
    m = await message.reply_text("🌑")
    for frame in MOON_PHASES:
        await smart_edit(m, frame, 0.5)
    await draw_art(m, MOON_ART, header="🌕 NIGHT SKY", footer="✨ Good night")


@app.on_message(ub_cmd("heart", "heartart"), group=-8)
async def heartart_cmd(client, message: Message):
    m = await message.reply_text("❤️")
    for frame in HEART_BUILD:
        await smart_edit(m, f"<code>{frame}</code>", 0.45)
    await draw_art(m, HEART_ART, footer="❤️ FOR YOU")


@app.on_message(ub_cmd("yourmom"), group=-8)
async def yourmom_cmd(client, message: Message):
    m = await message.reply_text("🤱 Searching...")
    await draw_art(m, YOURMOM_ART, header="🤱 VS YOUR MOM", footer="TERI MAA MERE LAND PAR")


@app.on_message(ub_cmd("myson"), group=-8)
async def myson_cmd(client, message: Message):
    m = await message.reply_text("🐰 Summoning...")
    await draw_art(m, MYSON_ART, footer="🐰 Me & My Son")


@app.on_message(ub_cmd("ok"), group=-8)
async def ok_cmd(client, message: Message):
    m = await message.reply_text("✅")
    await draw_art(m, OK_ART, footer="✅ OK")


@app.on_message(ub_cmd("vip"), group=-8)
async def vip_cmd(client, message: Message):
    m = await message.reply_text("💎")
    await draw_art(m, VIP_ART, footer="💎 VIP")


@app.on_message(ub_cmd("boss"), group=-8)
async def boss_cmd(client, message: Message):
    m = await message.reply_text("👑")
    await draw_art(m, BOSS_ART, footer="👑 BOSS")


@app.on_message(ub_cmd("pro"), group=-8)
async def pro_cmd(client, message: Message):
    m = await message.reply_text("⚡")
    await draw_art(m, PRO_ART, footer="⚡ PRO")


@app.on_message(ub_cmd("king"), group=-8)
async def king_cmd(client, message: Message):
    m = await message.reply_text("👑")
    await draw_art(m, KING_ART, footer="👑 KING")


@app.on_message(ub_cmd("yashika"), group=-8)
async def yashika_cmd(client, message: Message):
    m = await message.reply_text("✨")
    await draw_art(m, YASHIKA_ART, footer="✨ YASHIKA")


@app.on_message(ub_cmd("win"), group=-8)
async def win_cmd(client, message: Message):
    m = await message.reply_text("🏆")
    await draw_art(m, WIN_ART, footer="🏆 WIN")


@app.on_message(ub_cmd("gg"), group=-8)
async def gg_cmd(client, message: Message):
    m = await message.reply_text("🔥")
    await draw_art(m, GG_ART, footer="🔥 GG")


@app.on_message(ub_cmd("hi"), group=-8)
async def hi_cmd(client, message: Message):
    m = await message.reply_text("👋")
    await draw_art(m, HI_ART, footer="👋 HI")


@app.on_message(ub_cmd("bye"), group=-8)
async def bye_cmd(client, message: Message):
    m = await message.reply_text("👋")
    await draw_art(m, BYE_ART, footer="👋 BYE")


@app.on_message(ub_cmd("funhelp", "arts"), group=-8)
async def funhelp_cmd(client, message: Message):
    await message.reply_text(
        "🎨 <b>FUN ARTS</b>\n"
        "<code>.cat</code> <code>.rose</code> <code>.hacker</code>\n"
        "<code>.error</code> <code>.fuck</code> <code>.butterfly</code>\n"
        "<code>.love</code> <code>.moon</code> <code>.heart</code>\n"
        "<code>.yourmom</code> <code>.myson</code>\n\n"
        "📜 <b>TEXT</b>\n"
        "<code>.ok</code> <code>.vip</code> <code>.boss</code> <code>.pro</code>\n"
        "<code>.king</code> <code>.yashika</code> <code>.win</code>\n"
        "<code>.gg</code> <code>.hi</code> <code>.bye</code>"
    )
