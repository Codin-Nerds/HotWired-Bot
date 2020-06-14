import hashlib

from discord import Color, Embed
from discord.ext.commands import Bot, Cog, Context, command

from utils.mathscrape import get_math_results
from utils.wolframscrape import get_wolfram_data


class Tools(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.hash_algos = sorted([h for h in hashlib.algorithms_available if h.islower()])

    @command(aliases=["calculator", "equation"])
    async def calc(self, ctx: Context, *, equation: str) -> None:
        """Calculate an equation."""
        res = get_math_results(equation)

        if res.lower() == "invalid equation":
            embed = Embed(title="ERROR!", description="❌ Invalid Equation Specified", color=Color.red(),)
            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Equation Results")
            embed.add_field(name="**❯❯ Question**", value=equation, inline=False)
            embed.add_field(name="**❯❯ Result**", value=res, inline=False)
            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

            await ctx.send(embed=embed)

    @command(aliases=["wq", "wolframquestion", "wquestion"])
    async def ask_question(self, ctx: Context, conversation_mode: str = "true", *, question: str) -> None:
        """Ask the answer of an question."""
        data = get_wolfram_data(question, conversation_mode)

        embed = Embed(title="Question Results")
        embed.add_field(name="**❯❯ Question**", value=question, inline=False)
        embed.add_field(name="**❯❯ Result**", value=data, inline=False)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Tools(bot))
