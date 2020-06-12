import time

import discord
from cogs.utils.embedHandler import error_embed, info, status_embed
from discord.ext import commands

from .utils import constants
import asyncio


class Custom(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hey there Buddy!')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def ping(self, ctx):
        """Shows bot ping."""
        start = time.perf_counter()
        message = await ctx.send(embed=info("Pong!", ctx.me))
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(embed=info(f":ping_pong: {duration:.2f}ms", ctx.me, "Pong!"))

    @commands.command()
    async def members(self, ctx):
        """Returns the number of members in a server."""
        await ctx.send(embed=info(f"{ctx.guild.member_count}", ctx.me, "Member count"))

    @commands.command()
    async def status(self, ctx, member: discord.Member = None):
        """Returns the status of a member."""
        if member is None:
            member = ctx.author

        if member.id == constants.owner_id:
            embed = status_embed(member, description="Not telling")
        else:
            embed = status_embed(member)

        await ctx.send(embed=embed)

    @commands.command()
    async def pfp(self, ctx, member: discord.Member = None):
        """Displays the profile picture of a member."""
        if member is None:
            message, url = "Your avatar", ctx.author.avatar_url
        elif member == ctx.me:
            message, url = "My avatar", member.avatar_url
        else:
            message, url = f"{member} avatar", member.avatar_url

        embed = info(message, ctx.me)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["git"])
    async def github(self, ctx):
        """GitHub repository"""
        embed = info(f"[HotWired Github Repo.]({constants.github_repo_link})", ctx.me, "Github")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def countdown(self, ctx, start: int):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        message = await ctx.send(start)
        while start:
            minutes, seconds = divmod(start, 60)
            content = f"{minutes:02d}:{seconds:02d}"
            await message.edit(content=content)
            start -= 1
            await asyncio.sleep(1)
        await message.delete()

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
