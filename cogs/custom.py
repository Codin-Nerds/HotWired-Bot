import time

import discord
from discord.ext import Bot

from cogs.utils.embedHandler import error_embed, info
from discord.ext.commands import Cog, command, has_permissions, Context


class Custom(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def hello(self, ctx: Context) -> None:
        """Greet a User."""
        await ctx.send('Hey there Buddy!')

    @command()
    @has_permissions(manage_messages=True)
    async def ping(self, ctx: Context) -> None:
        """Shows bot ping."""
        start = time.perf_counter()
        message = await ctx.send(embed=info("Pong!", ctx.me))
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)
        await message.edit(embed=info(f":ping_pong: Pong! ({duration}ms)", ctx.me))

    @command(aliases=['asking'])
    async def howtoask(self, ctx: Context) -> None:
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

    @command(aliases=['thank', 'ty'])
    async def thanks(self, ctx: Context, member: discord.Member, *, reason: str = None) -> None:
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


def setup(bot: Bot):
    bot.add_cog(Custom(bot))

# TODO: Custom is a bad name for a cog, this should be renamed
