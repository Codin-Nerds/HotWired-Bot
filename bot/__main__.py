import os

from discord import Game
from discord.ext.commands import when_mentioned_or

from bot import config
from bot.core.bot import Bot

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    command_prefix=when_mentioned_or(config.COMMAND_PREFIX),
    activity=Game(name=f"Ping me using {config.COMMAND_PREFIX}help"),
    case_insensitive=True,
)

if __name__ == "__main__":
    bot.run(TOKEN)
