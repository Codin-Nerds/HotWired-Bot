import traceback

from discord import Color, Embed, Message
from discord.ext.commands import Bot, Cog


class Custom(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        # Check that the message is not from bot account
        if message.author.bot:
            return

        if message.content.lower().startswith("help"):
            await message.channel.send("Hey! Why don't you run the help command with `>>help`")

    @Cog.listener()
    async def on_error(self, event: str, *args, **kwargs) -> None:
        error_message = f"```py\n{traceback.format_exc()}\n```"
        if len(error_message) > 2000:
            async with self.session.post("https://www.hastebin.com/documents", data=error_message) as resp:
                error_message = "https://www.hastebin.com/" + (await resp.json())["key"]

        embed = Embed(color=Color.red(), description=error_message, title=event)

        if not self.dev_mode:
            await self.error_hook.send(embed=embed)
        else:
            traceback.print_exc()


def setup(bot: Bot) -> None:
    bot.add_cog(Custom(bot))
