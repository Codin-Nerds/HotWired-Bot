from datetime import datetime
from itertools import cycle
import os

import asyncpg
from discord import Color, Embed, Game
from discord.ext.commands import Bot as Base_Bot

from bot import config


class Bot(Base_Bot):
    """Subclassed Hotwired bot."""

    def __init__(self, extensions: list, *args, **kwargs) -> None:
        """Initialize the hotwired bot."""
        super().__init__(*args, **kwargs)
        self.extension_list = extensions
        self.first_on_ready = True

        self.pool = None
        self.log_channel = None

    async def on_ready(self) -> None:
        """Initialize some stuff once the bot is ready."""
        if self.first_on_ready:
            self.first_on_ready = False

            self.pool = await asyncpg.create_pool(
                database=os.getenv("DATABASE_NAME", "hotwired"),
                host="127.0.0.1", min_size=int(os.getenv("POOL_MIN", "20")),
                max_size=int(os.getenv("POOL_MAX", "100")),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
            )

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

        print("Bot is ready")

    async def close(self) -> None:
        """Close the bot and do some cleanup."""
        await super().close()
        await self.pool.close()
