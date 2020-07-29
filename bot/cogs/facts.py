from discord import Embed, Color
import randfacts

from discord.ext.commands import Cog, Context, command

from bot.core.bot import Bot


class Facts(Cog):
    """A Class For A Random Fact"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def randomfact(self, ctx: Context) -> None:
        """Get A Random fact"""
        randomfact = randfacts.getFact()
        await ctx.send(embed=Embed(
            title="Did You Know?",
            description=randomfact["text"],
            color=Color.blurple()
        ))

# E
# E
# E
# E
# E
# E
# E
# E
# E
# E
# E


def setup(bot: Bot) -> None:
    bot.add_cog(Facts(bot))
