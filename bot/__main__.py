import os

from discord import Game
from discord.ext.commands import when_mentioned_or

from bot import constants
from bot.core.bot import Bot

TOKEN = os.getenv("BOT_TOKEN")

extensions = [
    "bot.cogs.codesandbox",
    "bot.cogs.commands",
    "bot.cogs.converters",
    "bot.cogs.common",
    "bot.cogs.emotes",
    "bot.cogs.events",
    "bot.cogs.fun",
    "bot.cogs.games",
    "bot.cogs.infog",
    "bot.cogs.moderation",
    "bot.cogs.study",
    "bot.cogs.sudo",
    "bot.cogs.support",
    "bot.cogs.tools",
    "bot.cogs.search",
    "bot.cogs.malware_protection"
    # "bot.cogs.coding"
]

bot = Bot(
    extensions,
    command_prefix=when_mentioned_or(constants.COMMAND_PREFIX),
    activity=Game(name=f"Ping me using {constants.COMMAND_PREFIX}help"),
    case_insensitive=True
)

if __name__ == "__main__":
    bot.run(TOKEN)
