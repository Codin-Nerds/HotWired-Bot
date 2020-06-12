import discord
from discord.ext import commands

from utils.mathscrape import get_math_results
from utils.wolframscrape import get_wolfram_data
from .urbandict_utils.urbandictpages import UrbanDictionaryPages


class Study(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pcalc(self, ctx):
        pass

    @commands.command()
    async def calc(self, ctx, *, equation: str):
        """Calculate an equation"""

        res = get_math_results(equation)

        if res.lower() == "invalid equation":
            emb = discord.Embed(
                title="ERROR!", description="❌ Invalid Equation Specified, Please Recheck the Equation",
                color=discord.Color.red())
            emb.set_footer(text=f'Invoked by {str(ctx.message.author)}')

            await ctx.send(embed=emb)

        else:
            embed = discord.Embed(title="Equation Results")

            embed.add_field(name="**❯❯ Question**", value=equation, inline=False)
            embed.add_field(name="**❯❯ Result**", value=res, inline=False)

            embed.set_footer(text=f'Invoked by {str(ctx.message.author)}')

            await ctx.send(embed=embed)

    @commands.command(aliases=['wq', 'wolframquestion', 'wquestion'])
    async def ask_question(self, ctx, conversation_mode="true", *, question: str):
        """Ask the answer of an question"""

        data = get_wolfram_data(question, conversation_mode)

        embed = discord.Embed(title="Question Results")

        embed.add_field(name="**❯❯ Question**", value=question, inline=False)
        embed.add_field(name="**❯❯ Result**", value=data, inline=False)

        embed.set_footer(text=f'Invoked by {str(ctx.message.author)}')

        await ctx.send(embed=embed)

    @commands.command(name='urban')
    async def _urban(self, ctx, *, word):
        """Searches urban dictionary."""

        url = 'http://api.urbandictionary.com/v0/define'
        async with ctx.session.get(url, params={'term': word}) as resp:
            if resp.status != 200:
                return await ctx.send(f'An error occurred: {resp.status} {resp.reason}.')

            js = await resp.json()
            data = js.get('list', [])
            if not data:
                return await ctx.send('No results found, sorry.')

        try:
            pages = UrbanDictionaryPages(ctx, data)
            await pages.paginate()
        except Exception as e:
            await ctx.send(e)


def setup(client):
    client.add_cog(Study(client))
