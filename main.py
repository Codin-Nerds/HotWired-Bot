from __future__ import annotations

import os
from datetime import datetime
from itertools import cycle

import aiohttp

# import asyncpg
import discord
from discord.ext import commands, tasks
from yaml import safe_load

from cogs.utils import constants

TOKEN = os.getenv("BOT_TOKEN")

PREFIX = constants.COMMAND_PREFIX

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


class BaseBot(commands.Bot):
    def __init__(self, *args, **kwargs,) -> None:
        super().__init__(
            *args, **kwargs,
        )
        # self.pool = await asyncpg.create_pool(
        #     database=os.getenv("DATABASE_NAME", "chaotic"),
        #     host="127.0.0.1", min_size=int(os.getenv("POOL_MIN", "20")),
        #     max_size=int(os.getenv("POOL_MAX", "100")),
        #     user=os.getenv("DATABASE_USER"),
        #     password=os.getenv("DATABASE_PASSWORD"),
        # )


Bot = BaseBot(commands.when_mentioned_or(PREFIX), case_insensitive=True,)


Bot_statuses = cycle(
    [
        "😁Working At The Codin' Hole! Join me at https://discord.gg/aYF76yY",
        "▶Check out My Creator's Youtube channel : https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ/",
        f"Ping me using {PREFIX}help",
        "Official Instagram of My Creator ❌ https://instagram.com/the.codin.hole/",
        "Ready To Work and Get Worked! My Github 🔆 https://github.com/janaSunrise",
    ]
)


@tasks.loop(hours=3)
async def change_status() -> None:
    await Bot.change_presence(activity=discord.Game(name=next(Bot_statuses)))


@tasks.loop(seconds=1)
async def update_languages(self,) -> None:
    async with Bot.aio_session as client_session:
        async with client_session.get(
            "https://tio.run/languages.json"
        ) as response:
            if response.status != 200:
                print(f"Error: (status code: {response.status}).")
            print(await response.json())
            languages = tuple(sorted(await response.json()))

            if self.languages != languages:
                self.languages = languages


@Bot.event
async def on_ready() -> None:

    change_status.start()

    log_channel = Bot.get_channel(constants.log_channel)

    print(f"Bot is ready.\nLogged in as {Bot.user.name} : {Bot.user.id}")

    embed = discord.Embed(
        title="Bot Connection",
        description="New connection initialized.",
        color=discord.Color.green(),
    )
    embed.timestamp = datetime.utcnow()

    await log_channel.send(embed=embed)

    for ext in extensions:
        Bot.load_extension(ext)


if __name__ == "__main__":
    if TOKEN is not None:
        Bot.run(TOKEN)
    else:
        print(
            """The token environment variable is None, are you
            sure you added an environment variable called 'BOT_TOKEN'
            inside of a .env file on the workspace directory? And are
            you sure you are running this file with pipenv?
            (pipenv run start from the command line)"""
        )
