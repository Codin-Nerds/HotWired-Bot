import os

from bot import config
from bot.core.bot import Bot

from discord import Game, Message


async def command_prefix(bot: Bot, message: Message) -> str:
    """Define the prefix of the commands."""
    return await bot.get_prefix(message)


TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX

extensions = [
    "bot.cogs.asciiart",

    "bot.cogs.codesandbox",
    "bot.cogs.coding",
    "bot.cogs.commands",
    "bot.cogs.common",
    "bot.cogs.conversion",

    "bot.cogs.disjobs",
    "bot.cogs.documentation",

    "bot.cogs.embeds",
    "bot.cogs.emotes",
    "bot.cogs.events",

    "bot.cogs.games",
    "bot.cogs.github",

    "bot.cogs.help",

    "bot.cogs.lock",

    "bot.cogs.moderation",
    "bot.cogs.music",

    "bot.cogs.nasa",
    "bot.cogs.nsfw",

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
    command_prefix=command_prefix,
    activity=Game(name=f"Ping me using {config.COMMAND_PREFIX}help"),
    case_insensitive=True,
)


if __name__ == "__main__":
    bot.run(TOKEN)
