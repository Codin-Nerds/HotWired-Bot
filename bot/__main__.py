import os

from bot import config
from bot.core.bot import Bot

import colorama

from discord import Game
from discord.ext.commands import when_mentioned_or


TOKEN = os.getenv("BOT_TOKEN")

extensions = [
    "bot.cogs.paginator_pr_test.py"  # ! TODO remove this line
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
]

bot = Bot(
    extensions,
    command_prefix=when_mentioned_or(config.COMMAND_PREFIX),
    activity=Game(name=f"Invoke me using {config.COMMAND_PREFIX}help"),
    case_insensitive=True,
)


class TokenNotFoundError(Exception):
    """
    Raised if token is not found
    """
    pass


if __name__ == "__main__":
    if TOKEN is not None:
        bot.run(TOKEN)
    else:
        colorama.init(autoreset=True)

        raise TokenNotFoundError(
            colorama.Fore.RED + "\n"
            "Token is not found, are you sure\n"
            "you are running this file through\n"
            "pipenv and there is a .env file\n"
            "containing a BOT_TOKEN key on your\n"
            "current working directory?"
        )
