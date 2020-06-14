import discord
from discord.ext import Bot
from discrod.ext.commands import Cog, command, Context

from utils.mathscrape import get_math_results
from utils.wolframscrape import get_wolfram_data


class Study(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def calc(self, ctx: Context, *, equation: str) -> None:
        """Calculate an equation"""
        res = get_math_results(equation)

        if res.lower() == "invalid equation":
            embed = discord.Embed(title="ERROR!", description="❌ Invalid Equation Specified, Please Recheck the Equation", color=discord.Color.red(),)
            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")
        else:
            embed = discord.Embed(title="Equation Results")
            embed.add_field(name="**❯❯ Question**", value=equation, inline=False)
            embed.add_field(name="**❯❯ Result**", value=res, inline=False)
            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command(aliases=["wq", "wolframquestion", "wquestion"])
    async def ask_question(self, ctx: Context, conversation_mode: str = "true", *, question: str) -> None:
        """Ask the answer of an question"""
        data = get_wolfram_data(question, conversation_mode)

        embed = discord.Embed(title="Question Results")
        embed.add_field(name="**❯❯ Question**", value=question, inline=False)
        embed.add_field(name="**❯❯ Result**", value=data, inline=False)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Study(bot))
