from datetime import datetime

import aiohttp

from bot import config

import colorama

from discord import Color, Embed
from discord.ext.commands import Bot as Base_Bot

colorama.init(autoreset=True)


class Bot(Base_Bot):
    def __init__(self, extensions: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extension_list = extensions
        self.initial_call = True
        self.aio_session = aiohttp.ClientSession

    async def on_ready(self) -> None:
        if self.initial_call:
            self.initial_call = False

            # Log new connection
            self.log_channel = self.get_channel(config.log_channel)
            embed = Embed(
                title="Bot Connection",
                description="New connection initialized.",
                timestamp=datetime.utcnow(),
                color=Color.dark_teal(),
            )
            await self.log_channel.send(embed=embed)

            # Load all extensions
            for extension in self.extension_list:
                try:
                    self.load_extension(extension)
                    print(f"Cog {extension} loaded.")
                except Exception as e:
                    print(
                        f"Cog {extension} failed to load with {type(e)}: {e}"
                    )
        else:
            embed = Embed(
                title="Bot Connection",
                description="Connection re-initialized.",
                timestamp=datetime.utcnow(),
                color=Color.dark_teal(),
            )
            await self.log_channel.send(embed=embed)

        print(colorama.Fore.GREEN + "Bot is ready")

    async def shutoff(self) -> None:
        colorama.init(autoreset=True)

        print(colorama.Fore.BLUE + "Shutting Down...")

        await super().close()
        await self.aio_session.close(self.aio_session)
        print(colorama.Fore.GREEN + "The bot and aiohttp connections are properly closed ✔️")
