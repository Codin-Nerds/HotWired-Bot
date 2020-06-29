from discord import Embed, Color
from discord.ext.commands import Cog, command, Context, Bot


class Latex(Cog):
    """LaTeX."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(pass_context=True, no_pm=True)
    async def latex(self, ctx: Context, *, equation: str) -> None:
        """Takes a LaTeX expression and makes it pretty"""
        base_url = "http://latex.codecogs.com/gif.latex?x&space;=&space;"
        equations = equation.split("\n")
        equation = ''.join(equations)
        url = f"{base_url}{equation}"

        embed = Embed(description='', colour=Color.green())
        embed.set_author(name=equation, icon_url=ctx.author.avatar_url)
        embed.set_image(url=url)
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Latex(bot))
