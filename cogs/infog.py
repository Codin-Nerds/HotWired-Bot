from discord.ext.commands import Bot, Cog, Context, command


class Infog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def infog(self, ctx: Context) -> None:
        await ctx.send("Info gathered")


def setup(bot: Bot) -> None:
    bot.add_cog(Infog(bot))
