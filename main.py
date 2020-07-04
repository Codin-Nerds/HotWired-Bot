from __future__ import annotations

import os
from itertools import cycle
from yaml import safe_load
import aiohttp

import asyncpg
import discord
from discord.ext import commands, tasks

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


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.status = cycle(
            [
                "😁Working At The Codin' Hole! Join me at https://discord.gg/aYF76yY",
                "▶Check out My Creator's Youtube channel : https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ/",
                f"Ping me using {PREFIX}help",
                "Official Instagram of My Creator ❌ https://instagram.com/the.codin.hole/",
                "Ready To Work and Get Worked! My Github 🔆 https://github.com/janaSunrise",
            ]
        )
        self.first_on_ready = True

        with open('assets/languages.yml', 'r') as file:
            self.default = safe_load(file)

    async def on_ready(self) -> None:
        if self.first_on_ready:
            self.pool = await asyncpg.create_pool(
                database=os.getenv("DATABASE_NAME"),
                host="127.0.0.1", min_size=int(os.getenv("POOL_MIN", "20")),
                max_size=int(os.getenv("POOL_MAX", "100")),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
            )
            self.change_status.start()
            self.first_on_ready = False
            self.log_channel = self.get_channel(constants.log_channel)
            await self.log_channel.send(f"Bot is ready.\nLogged in as {self.user.name} : {self.user.id}")
            for ext in extensions:
                self.load_extension(ext)
        else:
            await self.log_channel.send("I'm ready (again)")

    async def close(self) -> None:
        await super().close()
        await self.pool.close()

    @tasks.loop(hours=3)
    async def change_status(self) -> None:
        await self.change_presence(activity=discord.Game(name=next(self.status)))

    @tasks.loop(hours=0.01)
    async def update_languages(self) -> None:
        async with aiohttp.ClientSession() as client_session:
            async with client_session.get("https://tio.run/languages.json") as response:
                if response.status != 200:
                    print(f"Error: (status code: {response.status}).")
                print(await response.json())
                languages = tuple(sorted(await response.json()))

                if self.languages != languages:
                    self.languages = languages


bot = Bot(commands.when_mentioned_or(PREFIX), case_insensitive=True)

if __name__ == "__main__":
    bot.run(TOKEN)
