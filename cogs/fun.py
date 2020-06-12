import random

import discord
from cogs.utils.embedHandler import error_embed, info
from discord.ext import commands

from assets.context import Command, argument, example, usage_info
from cogs.utils import misc, parser


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dab(self, ctx, user: discord.User):
        embed = discord.Embed(color=discord.Color.orange())
        embed.set_author(name=f"{ctx.author.mention} subtly, yet epically dabs on {user.mention}")
        embed.set_image(url="https://media.giphy.com/media/A4R8sdUG7G9TG/giphy.gif")
        await ctx.send(embed=embed)

    @commands.command()
    async def default(self, ctx, user: discord.User):
        embed = discord.Embed(color=discord.Color.orange())
        embed.set_author(name=f"{ctx.author.mention} epically defaults on {user.mention}")
        embed.set_image(url="https://media.tenor.com/images/4f71b921b09bfb195c0295116aa4e8dc/tenor.gif")
        await ctx.send(embed=embed)

    @commands.command(aliases=["catfacts"], cls=Command,
                      description="Get a random fact about cats!",
                      syntax=None,
                      examples=[argument("", "Returns a interesting fact about cats")])
    async def catfact(self, ctx):
        link = "https://catfact.ninja/fact?max_length=300/"

        fact = await self.aiohttp_request(link, headers=None)
        fact = json.loads(fact)
        embed = discord.Embed(title="Cat Facts", color=misc.random_color(),
                              description=fact["fact"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["dogfacts"], cls=Command,
                      description="Get a random fact about dogs!",
                      syntax=None,
                      examples=[argument(None, "Returns a interesting fact about dogs")])
    async def dogfact(self, ctx):
        link = "http://dog-api.kinduff.com/api/facts?numbers=1"
        fact = await self.aiohttp_request(link, headers=None)
        fact = json.loads(fact)
        embed = discord.Embed(title="Dog Facts", color=misc.random_color(),
                              description=fact["facts"][0])
        await ctx.send(embed=embed)

    @commands.command(aliases=["dogpic", "dog"], cls=Command,
                      description="Get a random picture of a dog",
                      syntax=None, examples=[argument("", "Get a cute picture of a dog")])
    async def dogpics(self, ctx):
        link = "https://dog.ceo/api/breeds/image/random/Fetch"
        picture_data = await self.aiohttp_request(link, headers=None)
        picture_data = json.loads(picture_data)

        embed = discord.Embed(title="Here's a picture of a dog!", color=misc.random_color())
        embed.set_image(url=picture_data["message"][0])
        await ctx.send(embed=embed)

    @commands.command(aliases=["catpic", "cat"], cls=Command,
                      description="Get a random picture of a cat!",
                      syntax=None, examples=[argument("", "Get a cute picture of a cat")])
    async def catpics(self, ctx):
        link = "https://api.thecatapi.com/v1/images/search?format=json?size=med"
        picture_data = await self.aiohttp_request(link, headers=None)
        picture_data = json.loads(picture_data)

        embed = discord.Embed(title="Here's a picture of a cat!", color=misc.random_color())
        embed.set_image(url=picture_data[0]["url"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["choose", "choice"], cls=Command,
                      description="Chooses a random item out of a list for you!",
                      syntax=[(True, "List of items")],
                      usage_information=[usage_info("", "List of items must be separated by commas or spaces")],
                      examples=[example("1,2,3,4", "Returns a random selection like 2")])
    async def random(self, ctx, *, message):
        """Chooses a random item out of a list for you!
        [prefix]random_picker [Required: list of items]
        list of items must be separated by commas or spaces
        Example
         • `!random_picker 1,2,3,4` Returns a random selection like 2
        """
        if not message:
            return await ctx.send("I can't exactly select a random item when "
                                  "I don't have any items to begin with!")

        message = re.split(", |,| ", message)
        if len(message) == 1:
            return await ctx.send("I'm gonna be needing more than one item to make a choice lol")
        choice = random.choice(message)
        if not choice:
            return await ctx.send("Huh odd looks like I got a empty message out of that. Perhaps try spaces this time?")

        await ctx.send(choice)

    @commands.command()
    async def slap(self, ctx, member: discord.Member):
        """Slap a User."""
        if ctx.author == member:
            embed = info(f"{member.mention} slapped him/her self LMAO", ctx.me, "Slap in The Face!")
            img_url = "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif"
        else:
            embed = info(f"{member.mention} got slapped in the face by: {ctx.author.mention}!", ctx.me, "Slap In The Face!")
            img_url = "https://media.giphy.com/media/Ql5voX2wAVUYw/giphy.gif"
        embed.set_image(url=img_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def punch(self, ctx, member: discord.Member):
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

    @commands.command()
    async def shoot(self, ctx, member: discord.Member):
        """Shoot a User."""
        embed = info(f"{member.mention} shot by {ctx.author.mention}  :gun: :boom:", ctx.me, "Boom! Bam! He's Dead!")
        embed.set_image(url="https://media.giphy.com/media/xT9IguC6bxYHsGIRb2/giphy.gif")
        await ctx.send(embed=embed)

    @commands.command(aliases=["table", "flip"])
    async def throw(self, ctx):
        """Throw the table."""
        embed = info(f"{ctx.author.mention} :boom:", ctx.me, "Table Throw!")
        embed.set_image(url="https://media.giphy.com/media/pzFB1KY4wob0jpbuPa/giphy.gif")
        await ctx.send(embed=embed)

    @commands.command(aliases=['cookies', 'cook'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def cookie(self, ctx, member: discord.Member = None):
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
    async def cookie_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = error_embed("You Can get a Cookie Every **2 Hours Once**", "❌ERROR")
            await ctx.send(embed=embed)
# TODO: kiss, hug, pat => commands to be added
# cuddle hug insult kiss lick nom pat poke slap stare highfive bite greet punch handholding tickle kill hold pats wave boop


def setup(bot):
    bot.add_cog(Fun(bot))
