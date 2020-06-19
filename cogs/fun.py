import random
import textwrap
import urllib
import typing as t
import aiohttp
import os
import discord
from random import choice, randint
from discord import Color, Embed, Message
from discord.ext.commands import BadArgument, Bot, BucketType, Cog, Context, command, cooldown, tasks

from cogs.utils.errors import ServiceError

from .endpoints.endpoints import nekos


file = open("assets" + os.path.sep + "excuses.txt", "r", encoding="utf-8")
excuses = file.readlines()
file.close()


class Fun(Cog):
    """This is a cog for simple fun commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.catfact_update.start()
        self.user_agent = {"User-Agent": "HotWired"}
        self.dadjoke = {
            "User-Agent": "HotWired",
            "Accept": "text/plain",
        }

    @tasks.loop(hours=12)
    async def catfact_update(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cat-fact.herokuapp.com/facts") as response:
                self.all_facts = await response.json()

    @command()
    async def catfact(self, ctx: Context) -> None:
        """Sends a random cat fact"""
        fact = choice(self.all_facts["all"])
        await ctx.send(embed=Embed(title="Did you Know?", description=fact["text"], color=0x690E8))

    @command()
    async def chuck(self, ctx: Context) -> t.Union[None, Message]:
        """Get a random Chuck Norris joke"""
        if randint(0, 1):
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.chucknorris.io/jokes/random") as r:
                    joke = await r.json()
                    return await ctx.send(joke["value"])
        if ctx.guild:
            if not ctx.channel.is_nsfw():
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://api.icndb.com/jokes/random?exclude=[explicit]") as r:
                        joke = await r.json()
                        return await ctx.send(joke["value"]["joke"])

        async with aiohttp.ClientSession() as session:
            async with session.get("http://api.icndb.com/jokes/random") as r:
                joke = await r.json()
                await ctx.send(joke["value"]["joke"].replace("&quote", '"'))

    @command()
    async def dong(self, ctx: Context, dick: discord.Member = None) -> None:
        """How long is this person's dong ?"""
        if not dick:
            dick = ctx.author
        await ctx.send(f"{dick.mention}'s magnum dong is this long : 8{'=' * randint(0, 15)}>")

    @command()
    async def cat(self, ctx: Context) -> None:
        """Random cat images. Awww, so cute! Powered by random.cat"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://aws.random.cat/meow", headers=self.user_agent) as r:
                if r.status == 200:
                    js = await r.json()
                    em = discord.Embed(name="random.cat", colour=0x690E8)
                    em.set_image(url=js["file"])
                    await ctx.send(embed=em)
                else:
                    raise ServiceError(f"could not fetch cute cat :( (http {r.status})")

    @command()
    async def httpcat(self, ctx: Context, http_id: int) -> None:
        """http.cat images - ^httpcat <http code>"""
        codes = [
            100,
            101,
            200,
            201,
            202,
            204,
            206,
            207,
            300,
            301,
            302,
            303,
            304,
            305,
            307,
            400,
            401,
            402,
            403,
            404,
            405,
            406,
            408,
            409,
            410,
            411,
            412,
            413,
            414,
            416,
            417,
            418,
            420,
            421,
            422,
            423,
            424,
            425,
            426,
            429,
            444,
            450,
            451,
            500,
            502,
            503,
            504,
            506,
            507,
            508,
            509,
            511,
            599,
        ]
        if http_id in codes:
            httpcat_em = discord.Embed(name="http.cat", colour=0x690E8)
            httpcat_em.set_image(url=f"https://http.cat/{http_id}.jpg")
            await ctx.send(embed=httpcat_em)
        else:
            raise BadArgument("Specified HTTP code invalid")

    @command()
    async def fox(self, ctx: Context) -> None:
        """Sends a random fox picture"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://randomfox.ca/floof/") as response:
                picture = await response.json()
                embed = discord.Embed(title="Fox", color=0x690E8)
                embed.set_image(url=picture["image"])
                await ctx.send(embed=embed)

    @command()
    async def dog(self, ctx: Context) -> None:
        """Random doggos just because!"""

        def decide_source() -> str:
            n = random.random()
            if n < 0.5:
                return "https://random.dog/woof"
            elif n > 0.5:
                return "https://dog.ceo/api/breeds/image/random"

        async with aiohttp.ClientSession() as session:
            async with session.get(decide_source(), headers=self.user_agent) as shibe_get:
                if shibe_get.status == 200:
                    if shibe_get.host == "random.dog":
                        shibe_img = await shibe_get.text()
                        shibe_url = "https://random.dog/" + shibe_img
                    elif shibe_get.host == "dog.ceo":
                        shibe_img = await shibe_get.json()
                        shibe_url = shibe_img["message"]

                    if ".mp4" in shibe_url:
                        await ctx.send("video: " + shibe_url)
                    else:
                        shibe_em = discord.Embed(colour=0x690E8)
                        shibe_em.set_image(url=shibe_url)
                        await ctx.send(embed=shibe_em)
                else:
                    raise ServiceError(f"could not fetch pupper :( (http {shibe_get.status})")

    @command()
    async def lizard(self, ctx) -> None:
        """Shows a random lizard picture"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/lizard", headers=self.user_agent) as lizr:
                if lizr.status == 200:
                    img = await lizr.json()
                    liz_em = discord.Embed(colour=0x690E8)
                    liz_em.set_image(url=img["url"])
                    await ctx.send(embed=liz_em)
                else:
                    raise ServiceError(f"something went boom (http {lizr.status})")

    @command()
    async def why(self, ctx: Context) -> None:
        """Why _____?"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/why", headers=self.user_agent) as why:
                if why.status == 200:
                    why_js = await why.json()
                    why_em = discord.Embed(title=f"{ctx.author.name} wonders...", description=why_js["why"], colour=0x690E8,)
                    await ctx.send(embed=why_em)
                else:
                    raise ServiceError(f"something went boom (http {why.status})")

    @command(aliases=["rhash", "robothash", "rh", "rohash"])
    async def robohash(self, ctx: Context, *, meme: str) -> None:
        """text => robot image thing"""
        try:
            e = discord.Embed(colour=0x690E8)
            meme = urllib.parse.quote_plus(meme)
            e.set_image(url=f"https://robohash.org/{meme}.png")
            await ctx.send(embed=e)
        except Exception as e:
            raise ServiceError(f"something broke: {e!s}")

    async def get_answer(self, ans: str) -> str:
        if ans == "yes":
            return "Yes."
        elif ans == "no":
            return "NOPE"
        elif ans == "maybe":
            return "maaaaaaybe?"
        else:
            raise BadArgument("internal error: invalid answer lmaoo")

    @command(aliases=["shouldi", "ask"])
    async def yesno(self, ctx: Context, *, question: str) -> None:
        """Why not make your decisions with a bot?"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://yesno.wtf/api", headers=self.user_agent) as meme:
                if meme.status == 200:
                    mj = await meme.json()
                    ans = await self.get_answer(mj["answer"])
                    em = discord.Embed(title=ans, description="And the answer to" f" {question} is this", colour=0x690E8,)
                    em.set_image(url=mj["image"])
                    await ctx.send(embed=em)
                else:
                    raise ServiceError(f"oof (http {meme.status})")

    @command(aliases=["dadjoke", "awdad", "dadpls", "shitjoke", "badjoke"])
    async def joke(self, ctx: Context) -> None:
        """Dad joke simulator 3017, basically"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com", headers=self.dadjoke) as jok:
                if jok.status == 200:
                    res = await jok.text()
                    res = res.encode("utf-8").decode("utf-8")
                    await ctx.send(f"`{res}`")
                else:
                    raise ServiceError(f"rip dad (http {jok.status})")

    @command(aliases=["bofh", "techproblem"])
    async def excuse(self, ctx: Context) -> None:
        """
        Bastard Operator from Hell excuses.

        Source: http://pages.cs.wisc.edu/~ballard/bofh
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("http://pages.cs.wisc.edu" "/~ballard/bofh/excuses") as r:
                data = await r.text()
                lines = data.split("\n")
                line = random.choice(lines)
                await ctx.send(f"`{line}`")

    @command()
    async def neko(self, ctx: Context) -> None:
        """Shows a neko"""
        async with aiohttp.ClientSession() as session:
            # TODO : WIP, can be merged
            async with session.get(session, nekos["sfw"]) as neko:
                if neko.status == 200:
                    img = await neko.json()
                    neko_em = discord.Embed(colour=0x690E8)
                    neko_em.set_image(url=img["neko"])
                    await ctx.send(embed=neko_em)
                else:
                    raise ServiceError(f"ERROR CODE: {neko.status})")

    @command()
    async def slap(self, ctx: Context, member: discord.Member) -> None:
        """Slap a User."""
        actor = ctx.author.mention if ctx.author == member else "him/her self LMAO"
        embed = Embed(title="Slap In The Face!", description=f"{member.mention} got slapped in the face by {actor}!", color=Color.blurple(),)
        embed.set_image(url="https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif")
        await ctx.send(embed=embed)

    @command()
    async def punch(self, ctx: Context, member: discord.Member = None) -> None:
        """Punch a User."""
        img_links = [
            "https://media.giphy.com/media/13HXKG2HGN8aPK/giphy.gif",
            "https://media.giphy.com/media/dAknWZ0gEXL4A/giphy.gif",
        ]
        actor = ctx.author.mention if ctx.author is not None or not member else "him/her self LMAO"
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
        # TODO : Add points after db integration
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
