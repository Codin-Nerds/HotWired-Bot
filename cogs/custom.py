import time

import discord
from cogs.utils.embedHandler import error_embed, info
from discord.ext import commands

from .utils import constants


class Custom(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f'Hey there Buddy! My Creator is {constants.creator}')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def ping(self, ctx):
        """Shows bot ping."""
        start = time.perf_counter()
        message = await ctx.send(embed=info("Pong!", ctx.me))
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(embed=info(f":ping_pong: {duration:.2f}ms", ctx.me, "Pong!"))

    @commands.command(aliases=("poll",))
    async def vote(self, ctx: commands.Context, title: str, *options: str) -> None:
        """
        Build a quick voting poll with matching reactions with the provided options.
        A maximum of 20 options can be provided, as Discord supports a max of 20
        reactions on a single message.
        """
        if len(options) < 2:
            raise commands.BadArgument("Please provide at least 2 options.")
        if len(options) > 20:
            raise commands.BadArgument("I can only handle 20 options!")

        codepoint_start = 127462  # represents "regional_indicator_a" unicode value
        options = {chr(i): f"{chr(i)} - {v}" for i, v in enumerate(options, start=codepoint_start)}
        embed = discord.Embed(title=title, description="\n".join(options.values()))
        message = await ctx.send(embed=embed)
        for reaction in options:
            await message.add_reaction(reaction)

    @commands.command(aliases=['asking'])
    async def howtoask(self, ctx):
        """How to ask a Question."""
        embed = info(
            "**1 ❯** Pick the appropriate channel\n"
            "**2 ❯** Post your question mentioning all the details\n"
            "**3 ❯** Ping the appropriate helper role or someone for your question\n"
            "**4 ❯** Patiently wait for a helper to respond\n",
            ctx.me, "How To Ask a Question?"
        )
        img_url = "https://media.giphy.com/media/3ojqPGJAHWqC1VQPDk/giphy.gif"
        embed.set_image(url=img_url)
        await ctx.send('**A S K I N G   A   Q U E S T I O N ❓**')
        await ctx.send(embed=embed)

    @commands.command(aliases=['thank', 'ty'])
    async def thanks(self, ctx, member: discord.Member, *, reason=None):
        """Thank a User."""
        if ctx.author == member:
            embed = error_embed(f"{ctx.author.mention} **You Cannot Thank Yourself!**", "WARNING!")
            await ctx.send(embed=embed)
        else:
            if reason is not None:
                embed = info(f"{member.mention} was Thanked By {ctx.author.mention} \n**MESSAGE** : {reason}", ctx.me, "THANKS")
                img_url = "https://media.giphy.com/media/6tHy8UAbv3zgs/giphy.gif"
                embed.set_image(url=img_url)
            else:
                embed = info(f"{member.mention} was Thanked By {ctx.author.mention} !", ctx.me, "THANKS")
                img_url = "https://media.giphy.com/media/osjgQPWRx3cac/giphy.gif"
                embed.set_image(url=img_url)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Custom(client))
