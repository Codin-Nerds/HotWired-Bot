import os

from discord import Game
from discord.ext.commands import when_mentioned_or

from bot import config
from bot.core.bot import Bot

TOKEN = os.getenv("BOT_TOKEN")

extensions = [
    "bot.cogs.codesandbox",
    "bot.cogs.commands",
    "bot.cogs.conversion",
    "bot.cogs.common",
    "bot.cogs.emotes",
    "bot.cogs.events",
    "bot.cogs.fun",
    "bot.cogs.games",
    "bot.cogs.moderation",
    "bot.cogs.study",
    "bot.cogs.sudo",
    "bot.cogs.support",
    "bot.cogs.tools",
    "bot.cogs.search",
    "bot.cogs.security",
    "bot.cogs.embeds",
    "bot.cogs.comics",
    "bot.cogs.coding",
    "bot.cogs.documentation",
    "bot.cogs.reddit",
    "bot.cogs.translate",
    "bot.cogs.github",
    "bot.cogs.nasa",
]

bot = Bot(
    extensions,
    command_prefix=when_mentioned_or(config.COMMAND_PREFIX),
    activity=Game(name=f"Ping me using {config.COMMAND_PREFIX}help"),
    case_insensitive=True,
)


if __name__ == "__main__":
    bot.run(TOKEN)
