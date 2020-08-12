import json
import os

from bot import config
from bot.core.bot import Bot

from discord import Game


def get_prefix(_, message) -> str:
    with open("bot/assets/prefixes.json", "r") as file:
        prefixes = json.load(file)

    return prefixes.get(str(message.guild.id))


TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX

extensions = [
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
    command_prefix=get_prefix,
    activity=Game(name=f"Ping me using {config.COMMAND_PREFIX}help"),
    case_insensitive=True,
)


if __name__ == "__main__":
    bot.run(TOKEN)
