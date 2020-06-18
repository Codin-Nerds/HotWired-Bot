import random
import textwrap

import discord
from discord import Color, Embed
from discord.ext.commands import BadArgument, Bot, BucketType, Cog, Context, command, cooldown


class Fun(Cog):
    """This is a cog for simple fun commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def slap(self, ctx: Context, member: discord.Member) -> None:
        """Slap a User."""
        actor = ctx.author.mention if ctx.author == member else "him/her self LMAO"
        embed = Embed(title="Slap In The Face!", description=f"{member.mention} got slapped in the face by {actor}!", color=Color.blurple(),)
        embed.set_image(url="https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif")
        await ctx.send(embed=embed)

    @command()
    async def punch(self, ctx: Context, member: discord.Member) -> None:
        """Punch a User."""
        img_links = [
            "https://media.giphy.com/media/13HXKG2HGN8aPK/giphy.gif",
            "https://media.giphy.com/media/dAknWZ0gEXL4A/giphy.gif",
        ]
        actor = ctx.author.mention if ctx.author == member else "him/her self LMAO"
        embed = Embed(title="Punch In The Face!", description=f"{member.mention} got punched in the face by {actor}!", color=Color.blurple(),)
        embed.set_image(url=random.choice(img_links))
        await ctx.send(embed=embed)

    @command()
    async def shoot(self, ctx: Context, member: discord.Member) -> None:
        """Shoot a User."""
        embed = Embed(
            title="Boom! Bam! He's Dead!", description=f"{member.mention} shot by {ctx.author.mention} :gun: :boom:", color=Color.blurple(),
        )
        embed.set_image(url="https://media.giphy.com/media/xT9IguC6bxYHsGIRb2/giphy.gif")
        await ctx.send(embed=embed)

    @command(aliases=["table", "flip", "tableflip"])
    async def throw(self, ctx: Context) -> None:
        """Throw the table."""
        embed = Embed(title="Table Throw!", description=f"{ctx.author.mention} threw the table! :boom:", color=Color.blurple(),)
        embed.set_image(url="https://media.giphy.com/media/pzFB1KY4wob0jpbuPa/giphy.gif")
        await ctx.send(embed=embed)

    @command(aliases=["cookies", "cook"])
    @cooldown(1, 30, BucketType.user)
    async def cookie(self, ctx: Context, member: discord.Member) -> None:
        """Give a User a cookie."""
        num = random.randint(1, 4)

        author = "You're a" if ctx.author == member else f"{member.mention} is"
        actor = f" from {ctx.author.mention}" if ctx.author != member else ""

        if num == 1:
            embed = Embed(
                title="Cookie Giver!",
                description=textwrap.dedent(
                    f"""
                    {author} Lucky Guy! You got a **Huge Cookie**{actor}!
                    **You got +10 points!**
                    """
                ),
                color=Color.blurple(),
            )
            embed.set_image(url="https://media.giphy.com/media/7GYHmjk6vlqY8/giphy.gif")
        else:
            embed = Embed(
                title="Cookie Giver!",
                description=textwrap.dedent(
                    f"""
                    {author} got a cookie{actor}! ➡ :cookie: :cookie: :cookie:
                    *You got +{num} points!**"
                    """
                ),
                color=Color.blurple(),
            )
        await ctx.send(embed=embed)
        # TODO: Adding points here should either do something or they shouldn't be mentioned as user will expect them to do something

    @cookie.error
    async def cookie_error(self, ctx: Context, error: Exception) -> None:
        if isinstance(error, BadArgument):
            embed = Embed(title="❌ERROR", description="You can only get a cookie **Once Every 2 Hours**.", color=Color.red(),)
            await ctx.send(embed=embed)


# TODO: kiss, hug, pat => commands to be added
# cuddle hug insult kiss lick nom pat poke slap stare highfive bite greet punch handholding tickle kill hold pats wave boop


def setup(bot: Bot) -> None:
    bot.add_cog(Fun(bot))
