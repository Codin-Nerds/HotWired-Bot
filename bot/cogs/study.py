import re
import textwrap
import typing as t

import aiohttp
import discord
from discord.ext.commands import Bot, Cog, Context, command

from bot.utils.math import get_math_results
from bot.utils.paginator import Pages
from bot.utils.wolframscrape import get_wolfram_data


class UrbanDictionaryPages(Pages):
    BRACKETED = re.compile(r"(\[(.+?)\])")

    def __init__(self, ctx: Context, data: t.List[str]) -> None:
        super().__init__(ctx, entries=data, per_page=1)

    def get_page(self, page: int) -> str:
        return self.entries[page - 1]

    def cleanup_definition(self, definition: str, *, regex: str = BRACKETED) -> str:
        def repl(m) -> str:
            word = m.group(2)
            return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'

        ret = regex.sub(repl, definition)
        if len(ret) >= 2048:
            return ret[0:2000] + " [...]"
        return ret

    def prepare_embed(self, entry: dict, page: int, *, first: bool = False) -> None:
        """Prepare embeds for the paginator."""
        if self.maximum_pages > 1:
            title = f'{entry["word"]}: {page} out of {self.maximum_pages}'
        else:
            title = entry["word"]

        self.embed = e = discord.Embed(colour=0xE86222, title=title, url=entry["permalink"])
        e.set_footer(text=f'Author : {entry["author"]}')
        e.description = self.cleanup_definition(entry["definition"])

        try:
            date = discord.utils.parse_time(entry["written_on"][0:-1])
        except (ValueError, KeyError):
            pass
        else:
            e.timestamp = date


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
                        title="Response Error Occured!",
                        description=textwrap.dedent(
                            f"""
                            Status Code: {resp.status}
                            Reason: {resp.reason}
                            """
                        ),
                        color=discord.Color.red(),
                    )
                    await ctx.send(embed=embed)
                    return

                js = await resp.json()
                data = js.get("list", [])
                if not data:
                    embed = discord.Embed(description="No results found, sorry.", color=discord.Color.red())
                    await ctx.send(embed=embed)
                    return

        pages = UrbanDictionaryPages(ctx, data)
        await pages.paginate()


def setup(bot: Bot) -> None:
    bot.add_cog(Study(bot))
