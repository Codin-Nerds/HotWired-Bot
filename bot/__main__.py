import os

from discord import Game
from discord.ext.commands import when_mentioned_or

from bot import config
from bot.core.bot import Bot

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX

extensions = [
    "bot.cogs.codesandbox",
    "bot.cogs.coding",
    "bot.cogs.commands",

    "bot.cogs.comics",
    "bot.cogs.common",
    "bot.cogs.conversion",
    "bot.cogs.documentation",
    "bot.cogs.embeds",
    "bot.cogs.emotes",
    "bot.cogs.events",
    "bot.cogs.fun",
    "bot.cogs.games",
    "bot.cogs.github",
    "bot.cogs.moderation",
    "bot.cogs.nasa",
    "bot.cogs.reddit",
    "bot.cogs.search",
    "bot.cogs.security",
    "bot.cogs.study",
    "bot.cogs.sudo",
    "bot.cogs.support",
    "bot.cogs.tools",
    "bot.cogs.translate",
]


bot = Bot(
    extensions,
    command_prefix=when_mentioned_or(PREFIX),
    activity=Game(name=f"Ping me using {PREFIX}help"),
    case_insensitive=True,
)

if __name__ == "__main__":
    bot.run(TOKEN)
