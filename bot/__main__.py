import json
import os

from bot import config
from bot.core.bot import Bot

from discord import Game


def get_prefix(client, message) -> str:
    with open("bot/assets/prefixes.json", "r") as file:
        prefixes = json.load(file)

    try:
        prefix = prefixes[str(message.guild.id)]
    except KeyError:
        prefix = config.COMMAND_PREFIX

    return prefix


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
    command_prefix=get_prefix,
    activity=Game(name=f"Ping me using {config.COMMAND_PREFIX}help"),
    case_insensitive=True,
)

if __name__ == "__main__":
    bot.run(TOKEN)
