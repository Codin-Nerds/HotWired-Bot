from datetime import datetime

from bot import config

from discord import Color, Embed
from discord.ext.commands import Bot as Base_Bot


class Bot(Base_Bot):
    def __init__(self, extensions: list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extension_list = extensions
        self.initial_call = True

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

        print("Bot is ready")

    async def close(self) -> None:
        await super().close()
