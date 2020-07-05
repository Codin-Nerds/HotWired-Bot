import os
from datetime import datetime
import asyncpg

from discord import Color, Embed
from discord.ext.commands import Bot

from bot import constants

DATABASE = {
    "host": "127.0.0.1",
    "database": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "min_size": int(os.getenv("POOL_MIN", "20")),
    "max_size": int(os.getenv("POOL_MAX", "100")),
}


class Bot(Bot):
    def __init__(self, extensions: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extension_list = extensions
        self.initial_call = True

    async def on_ready(self) -> None:
        if self.initial_call:
            self.initial_call = False

            # connect to the database
            self.pool = await asyncpg.create_pool(**DATABASE)

            # Log new connection
            self.log_channel = self.get_channel(constants.log_channel)
            embed = Embed(
                title="Bot Connection",
                description="New connection initialized.",
                timestamp=datetime.utcnow(),
                color=Color.dark_teal()
            )
            await self.log_channel.send(embed=embed)

            # Load all extensions
            for extension in self.extension_list:
                try:
                    print(f"Cog {extension} loaded.")
                    self.load_extension(extension)
                except Exception as e:
                    print(f"Cog {extension} failed to load with {type(e)}: {e}")
        else:
            embed = Embed(
                title="Bot Connection",
                description="Connection re-initialized.",
                timestamp=datetime.utcnow(),
                color=Color.dark_teal()
            )
            await self.log_channel.send(embed=embed)

        print("Bot is ready")

    async def close(self) -> None:
        await super().close()
        await self.pool.close()
