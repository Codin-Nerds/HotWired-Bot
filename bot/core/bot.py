from datetime import datetime

import asyncpg
from discord import Color, Embed
from discord.ext.commands import Bot as Base_Bot
from discord.ext.commands import ExtensionError
from loguru import logger

from bot import config


class Bot(Base_Bot):
    """Subclassed Hotwired bot."""

    def __init__(self, extensions: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extension_list = extensions
        self.first_on_ready = True

        self.pool = None
        self.log_channel = None

    async def on_ready(self) -> None:
        """Initialize some stuff once the bot is ready."""
        if self.first_on_ready:
            self.first_on_ready = False

            try:
                self.pool = await asyncpg.create_pool(**config.DATABASE)
            except asyncpg.exceptions.PostgresError:
                print("Database connection error. Killing program.")
                return await self.close()

            # Load all extensions
            for extension in self.extension_list:
                with logger.catch(message=f"Cog {extension} failed to load"):
                    self.load_extension(extension)
                    logger.debug(f"Cog {extension} loaded.")

            logger.info("Bot is ready")
        else:
            logger.info("Bot connection reinitialized")

    async def close(self) -> None:
        """Close the bot and do some cleanup."""
        logger.info("Closing bot connection")
        await super().close()
        if hasattr(self, "pool"):
            await self.pool.close()
