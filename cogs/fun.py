import random

import discord
from discord.ext import Bot
from discord.ext.commands import (BadArgument, BucketType, Cog, Context,
                                  command, cooldown)

from cogs.utils.embedHandler import error_embed, info


class Fun(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def slap(self, ctx: Context, member: discord.Member) -> None:
        """Slap a User."""
        if ctx.author == member:
            embed = info(f"{member.mention} slapped him/her self LMAO", ctx.me, "Slap in The Face!")
            img_url = "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif"
        else:
            embed = info(f"{member.mention} got slapped in the face by: {ctx.author.mention}!", ctx.me, "Slap In The Face!")
            img_url = "https://media.giphy.com/media/Ql5voX2wAVUYw/giphy.gif"
        embed.set_image(url=img_url)
        await ctx.send(embed=embed)

    @command()
    async def punch(self, ctx: Context, member: discord.Member) -> None:
        """Punch a User."""
        img_links = [
            'https://media.giphy.com/media/13HXKG2HGN8aPK/giphy.gif',
            'https://media.giphy.com/media/dAknWZ0gEXL4A/giphy.gif'
        ]
        if ctx.author == member:
            embed = info(f"{member.mention} punched him/her self LMAO", ctx.me, "Punch in The Face!")
            img_url = random.choice(img_links)
        else:
            embed = info(f"{member.mention} got punched in the face by: {ctx.author.mention}!", ctx.me, "Punch In The Face!")
            img_url = random.choice(img_links)
        embed.set_image(url=img_url)
        await ctx.send(embed=embed)

    @command()
    async def shoot(self, ctx: Context, member: discord.Member) -> None:
        """Shoot a User."""
        embed = info(f"{member.mention} shot by {ctx.author.mention}  :gun: :boom:", ctx.me, "Boom! Bam! He's Dead!")
        embed.set_image(url="https://media.giphy.com/media/xT9IguC6bxYHsGIRb2/giphy.gif")
        await ctx.send(embed=embed)

    @command(aliases=["table", "flip"])
    async def throw(self, ctx: Context) -> None:
        """Throw the table."""
        embed = info(f"{ctx.author.mention} :boom:", ctx.me, "Table Throw!")
        embed.set_image(url="https://media.giphy.com/media/pzFB1KY4wob0jpbuPa/giphy.gif")
        await ctx.send(embed=embed)

    @command(aliases=['cookies', 'cook'])
    @cooldown(1, 30, BucketType.user)
    async def cookie(self, ctx: Context, member: discord.Member = None) -> None:
        """Give a User a cookie."""
        if member is None:
            member = ctx.author

        num = random.randint(1, 4)

        if num == 1:
            if ctx.author == member:
                embed = info(f"You're a Lucky Guy! {member.mention} You got a **Huge Cookie**!\n**You got +10 points!**", ctx.me, "Cookie Giver!")
                img_url = "https://media.giphy.com/media/7GYHmjk6vlqY8/giphy.gif"
                embed.set_image(url=img_url)
                await ctx.send(embed=embed)
            else:
                embed = info(f"{member.mention} is a Lucky Guy! You got a **Huge Cookie**! from {ctx.author.mention}\n"
                             "**You got +10 points!**", ctx.me, "Cookie Giver!")
                img_url = "https://media.giphy.com/media/7GYHmjk6vlqY8/giphy.gif"
                embed.set_image(url=img_url)
                await ctx.send(embed=embed)
        else:
            if ctx.author == member:
                embed = info(f"You got a Cookie! {member.mention} ➡ :cookie: :cookie: :cookie: \n**You got +{num} points!**", ctx.me, "Cookie Giver!")
                await ctx.send(embed=embed)
            else:
                embed = info(f"{member.mention} got a cookie from {ctx.author.mention}➡ :cookie: :cookie: :cookie: \n**You got +{num} points!**",
                             ctx.me, "Cookie Giver!")
                await ctx.send(embed=embed)

    @cookie.error
    async def cookie_error(self, ctx: Context, error: Exception) -> None:
        if isinstance(error, BadArgument):
            embed = error_embed("You Can get a Cookie **Once Every 2 Hours**", "❌ERROR")
            await ctx.send(embed=embed)

# TODO: kiss, hug, pat => commands to be added
# cuddle hug insult kiss lick nom pat poke slap stare highfive bite greet punch handholding tickle kill hold pats wave boop


def setup(bot: Bot) -> None:
    bot.add_cog(Fun(bot))
