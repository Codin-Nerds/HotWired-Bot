from discord.ext.commands import Bot as Base_Bot
from loguru import logger

from bot import config


class Bot(Base_Bot):
    def __init__(self, extensions: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extension_list = extensions
        self.initial_call = True

    async def on_ready(self) -> None:
        if self.initial_call:
            self.initial_call = False

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
