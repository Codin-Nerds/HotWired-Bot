import asyncpg
import aiohttp

from discord import Message
from discord.ext.commands import AutoShardedBot as Base_Bot
from discord.ext.commands import Context

from loguru import logger

from bot import config


class Bot(Base_Bot):
    """Subclassed Hotwired bot."""

    def __init__(self, extensions: list, *args, **kwargs) -> None:
        """Initialize the subclass."""
        super().__init__(*args, **kwargs)
        self.extension_list = extensions
        self.first_on_ready = True

        self.default_prefix = config.COMMAND_PREFIX
        self.prefix_dict = {}

        self.pool = None
        self.log_channel = None
        self.session = aiohttp.ClientSession()

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

        query = "SELECT * FROM public.prefixes"
        async with self.pool.acquire(timeout=5) as database:
            for row in await database.fetch(query):
                self.prefix_dict[row["ctx_id"]] = row["prefix"]

    async def close(self) -> None:
        """Close the bot and do some cleanup."""
        logger.info("Closing bot connection")
        await self.session.close()
        await super().close()

        if hasattr(self, "pool"):
            await self.pool.close()

    async def get_prefix(self, message: Message) -> str:
        """Get the prefix from a message."""
        if message.content.startswith(f"{self.default_prefix}help"):
            return self.default_prefix

        return self.prefix_dict.get(
            self.get_id(message),
            self.default_prefix
        )

    def get_id(self, ctx: Context) -> int:
        """Get a context's id."""
        if ctx.guild:
            return ctx.guild.id
        return ctx.channel.id
