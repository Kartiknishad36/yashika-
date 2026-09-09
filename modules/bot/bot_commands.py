from pyrogram.types import BotCommand
from core.clients import bot

async def setup_bot_commands():
    if bot is None:
        return
    cmds = [
        BotCommand("start", "Start the bot"),
        BotCommand("play", "Play song in VC"),
        BotCommand("vplay", "Play video in VC"),
        BotCommand("skip", "Skip track"),
        BotCommand("stop", "Stop & leave VC"),
        BotCommand("queue", "Show queue"),
        BotCommand("pause", "Pause"),
        BotCommand("resume", "Resume"),
        BotCommand("bal", "Your balance"),
        BotCommand("daily", "Daily coins"),
        BotCommand("couple", "Cute couple"),
        BotCommand("td", "Truth or dare"),
        BotCommand("dice", "Dice game"),
        BotCommand("kiss", "Send kiss"),
        BotCommand("hug", "Send hug"),
        BotCommand("ai", "Ask AI"),
        BotCommand("chatbot", "on/off group AI"),
    ]
    await bot.set_bot_commands(cmds)
