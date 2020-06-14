import time

import discord
from discord.ext import Bot
import textwrap

from discord import Embed, Color
from discord.ext.commands import Cog, command, has_permissions, Context


class Custom(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def hello(self, ctx: Context) -> None:
        """Greet a User."""
        await ctx.send("Hey there Buddy!")

    @command()
    @has_permissions(manage_messages=True)
    async def ping(self, ctx: Context) -> None:
        """Shows bot ping."""
        start = time.perf_counter()
        embed = Embed(title="Info", description="Pong!", color=Color.blurple())
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)
        embed = Embed(title="Info", description=f":ping_pong: Pong! ({duration}ms)", color=Color.blurple(),)
        await message.edit(embed=embed)

    @command(aliases=["asking"])
    async def howtoask(self, ctx: Context) -> None:
        """How to ask a Question."""
        embed = Embed(
            title="How To Ask a Question?",
            description=textwrap.dedent(
                """
                **1 ❯** Pick the appropriate channel
                **2 ❯** Post your question mentioning all the details
                **3 ❯** Ping the appropriate helper role or someone for your question
                **4 ❯** Patiently wait for a helper to respond
                """
            ),
            color=Color.blurple(),
        )
        img_url = "https://media.giphy.com/media/3ojqPGJAHWqC1VQPDk/giphy.gif"
        embed.set_image(url=img_url)
        await ctx.send("**A S K I N G   A   Q U E S T I O N ❓**")
        await ctx.send(embed=embed)

    @command(aliases=["thank", "ty"])
    async def thanks(self, ctx: Context, member: discord.Member, *, reason: str = None) -> None:
        """Thank a User."""
        if ctx.author == member:
            embed = Embed(title="WARNING", description=f"{ctx.author.mention} **You Cannot Thank Yourself!**", color=Color.orange(),)
            await ctx.send(embed=embed)
        else:
            embed = Embed(
                title="THANKS",
                description=textwrap.dedent(
                    f"""
                    {member.mention} was thanked by {ctx.author.mention}!
                    {'**MESSAGE**:' + reason if reason else ''}
                    """
                ),
                color=Color.blurple(),
            )
            embed.set_image(url="https://media.giphy.com/media/6tHy8UAbv3zgs/giphy.gif")
            await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Custom(bot))


# TODO: Custom is a bad name for a cog, this should be renamed
