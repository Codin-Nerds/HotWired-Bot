from discord.ext import Bot
from discord.ext.commands import Cog, command, Context


class Infog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def infog(self, ctx: Context) -> None:
        await ctx.send("Info gathered")


def setup(bot: Bot):
    bot.add_cog(Infog(bot))
