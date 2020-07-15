import os

import asyncpg
from discord.ext.commands import Bot
from loguru import logger

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

            # Load all extensions
            for extension in self.extension_list:
                with logger.catch(message=f"Cog {extension} failed to load"):
                    self.load_extension(extension)
                    logger.debug(f"Cog {extension} loaded.")

            logger.info("Bot is ready")
        else:
            logger.info("Bot connection reinitialized")

    async def close(self) -> None:
        logger.info("Closing bot connection")
        await super().close()
        # In case bot doesn't get to on_ready
        if hasattr(self, "pool"):
            await self.pool.close()
