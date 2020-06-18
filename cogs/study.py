import discord
from discord.ext.commands import Bot, Cog, Context, command
import aiohttp

from utils.mathscrape import get_math_results
from utils.wolframscrape import get_wolfram_data
from .urbandict_utils.urbandictpages import UrbanDictionaryPages


class Study(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @command()
    async def calc(self, ctx: Context, *, equation: str) -> None:
        """Calculate an equation"""
        res = get_math_results(equation)

        if res.lower() == "invalid equation":
            emb = discord.Embed(title="ERROR!", description="❌ Invalid Equation Specified, Please Recheck the Equation", color=discord.Color.red())
            emb.set_footer(text=f"Invoked by {str(ctx.message.author)}")

            await ctx.send(embed=emb)

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

    @command(aliases=["dict"])
    async def urban(self, ctx: Context, *, word: str) -> None:
        """Searches urban dictionary."""
        url = "http://api.urbandictionary.com/v0/define"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"term": word}) as resp:
                if resp.status != 200:
                    await ctx.send(f"An error occurred: {resp.status} {resp.reason}.")
                    embed = discord.Embed(
                        title="Response Error Occured!", description=f"Status Code: {resp.status} \nReason: {resp.reason}", color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    return

                js = await resp.json()
                data = js.get("list", [])
                if not data:
                    embed = discord.Embed(description="No results found, sorry.", color=discord.Color.red())
                    await ctx.send(embed=embed)
                    return

        try:
            pages = UrbanDictionaryPages(ctx, data)
            await pages.paginate()
        except Exception as e:  # everything else is handled by the classes.
            embed = discord.Embed(title="Unexpected Error Occured!", description=e, color=discord.Color.red())
            await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Study(bot))
