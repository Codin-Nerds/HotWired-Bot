import os

from discord.ext.commands import when_mentioned_or

import config
from core.bot import Bot

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX

extensions = [
    "cogs.codesandbox",
    "cogs.coding",
    "cogs.commands",
    "cogs.converters",
    "cogs.common",
    "cogs.emotes",
    "cogs.events",
    "cogs.fun",
    "cogs.games",
    "cogs.infog",
    "cogs.moderation",
    "cogs.study",
    "cogs.sudo",
    "cogs.support",
    "cogs.tools",
]


bot = Bot(
    extensions,
    PREFIX,
    when_mentioned_or(PREFIX),
    case_insensitive=True,
)

if __name__ == "__main__":
    bot.run(TOKEN)
