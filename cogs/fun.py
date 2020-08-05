import random
import textwrap
import urllib
import typing as t
import aiohttp
import discord
from .utils import constants
from random import choice, randint
from discord import Color, Embed, Message
from discord.ext.commands import BadArgument, Bot, BucketType, Cog, Context, command, cooldown, is_nsfw, errors

from cogs.utils.errors import ServiceError

from .endpoints.endpoints import nekos
import nekos as n


class Fun(Cog):
    """This is a cog for simple fun commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.user_agent = {"User-Agent": "HotWired"}
        self.dadjoke = {
            "User-Agent": "HotWired",
            "Accept": "text/plain",
        }
        self.session = aiohttp.ClientSession()

    @command()
    async def catfact(self, ctx: Context) -> None:
        """Sends a random cat fact"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cat-fact.herokuapp.com/facts") as response:
                self.all_facts = await response.json()
        fact = choice(self.all_facts["all"])
        await ctx.send(embed=Embed(title="Did you Know?", description=fact["text"], color=0x690E8))

    @command()
    async def textcat(self, ctx: Context) -> None:
        """Sends a random textcat"""
        try:
            embed = Embed(color=0x690E8)
            embed.set_image(url=n.textcat())
            await ctx.send(embed=embed)
        except n.errors.NothingFound:
            await ctx.send("Couldn't Fetch Textcat! :(")

    @command()
    async def whydoes(self, ctx: Context) -> None:
        """Sends a random why?__"""
        try:
            embed = Embed(color=0x690E8)
            embed.set_image(url=n.why())
            await ctx.send(embed=embed)
        except n.errors.NothingFound:
            await ctx.send('Couldn\'t Fetch any "WHY!" :(')

    @command()
    async def fact(self, ctx: Context) -> None:
        """Sends a random fact"""
        try:
            embed = Embed(color=0x690E8)
            embed.set_image(url=n.fact())
            await ctx.send(embed=embed)
        except n.errors.NothingFound:
            await ctx.send('Couldn\'t Fetch any "Fact" :(')

    @command()
    @is_nsfw()
    async def image(self, ctx: Context, type: str) -> None:
        """Sends a random image(sfw and nsfw)."""
        try:
            embed = Embed(color=0x690E8)
            embed.set_image(url=n.img(type))
            await ctx.send(embed=embed)
        except errors.NSFWChannelRequired:
            await ctx.send("Hey dude! Go use this command in a NSFW Channel, this ain't ur home.")
        except n.errors.InvalidArgument:
            await ctx.send(f"Invalid type! Possible types are : ```{', '.join(constants.nsfw_possible)}```")
        except n.errors.NothingFound:
            await ctx.send("Sorry, No Images Found.")

    @command()
    async def chuck(self, ctx: Context) -> t.Union[None, Message]:
        """Get a random Chuck Norris joke."""
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
    async def cat(self, ctx: Context) -> None:
        """Random cat images. Awww, so cute! Powered by random.cat."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://aws.random.cat/meow", headers=self.user_agent) as r:
                if r.status == 200:
                    js = await r.json()
                    em = discord.Embed(name="random.cat", colour=0x690E8)
                    em.set_image(url=js["file"])
                    await ctx.send(embed=em)
                else:
                    await ctx.send(f"Couldn't Fetch cute cats :( [status : {r.status}]")

    @command()
    async def httpcat(self, ctx: Context, http_id: int) -> None:
        """http.cat images."""
        if http_id in constants.http_codes:
            httpcat_em = discord.Embed(name="http.cat", colour=0x690E8)
            httpcat_em.set_image(url=f"https://http.cat/{http_id}.jpg")
            await ctx.send(embed=httpcat_em)
        else:
            await ctx.send("Invalid HTTP Code Specified")

    @command()
    async def fox(self, ctx: Context) -> None:
        """Sends a random fox picture."""
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
            n = random.randint(0, 1)
            if n == 0:
                return "https://random.dog/woof"
            elif n == 1:
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
                    await ctx.send(f"Couldn't Fetch cute doggos :( [status : {shibe_get.status}]")

    @command()
    async def lizard(self, ctx) -> None:
        """Shows a random lizard picture."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/lizard", headers=self.user_agent) as lizr:
                if lizr.status == 200:
                    img = await lizr.json()
                    liz_em = discord.Embed(colour=0x690E8)
                    liz_em.set_image(url=img["url"])
                    await ctx.send(embed=liz_em)
                else:
                    await ctx.send(f"Something went Boom! [status : {lizr.status}]")

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
                    await ctx.send(f"Something went Boom! [status : {why.status}]")

    @command(aliases=["rhash", "robothash", "rh", "rohash"])
    async def robohash(self, ctx: Context, *, meme: str) -> None:
        """text => robot image thing."""
        try:
            e = discord.Embed(colour=0x690E8)
            meme = urllib.parse.quote_plus(meme)
            e.set_image(url=f"https://robohash.org/{meme}.png")
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"Something Broke. LOL [{e!s}]")

    async def get_answer(self, ans: str) -> str:
        if ans == "yes":
            return "Yes."
        elif ans == "no":
            return "NOPE"
        elif ans == "maybe":
            return "maaaaaaybe?"
        else:
            return "Internal Error: Invalid answer LMAOO"

    @command(aliases=["shouldi", "ask"])
    async def yesno(self, ctx: Context, *, question: str) -> None:
        """Why not make your decisions with a bot?"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://yesno.wtf/api", headers=self.user_agent) as meme:
                if meme.status == 200:
                    mj = await meme.json()
                    ans = await self.get_answer(mj["answer"])
                    em = discord.Embed(title=ans, description=f"And the answer to {question} is this:", colour=0x690E8,)
                    em.set_image(url=mj["image"])
                    await ctx.send(embed=em)
                else:
                    await ctx.send(f"OMFG! [STATUS : {meme.status}]")

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
                    await ctx.send(f"RIP Dad! :'( [STATUS : {jok.status}]")

    @command(aliases=["bofh", "techproblem"])
    async def excuse(self, ctx: Context) -> None:
        """
        Bastard Operator from Hell excuses.

        Source: http://pages.cs.wisc.edu/~ballard/bofh
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("http://pages.cs.wisc.edu/~ballard/bofh/excuses") as r:
                data = await r.text()
        lines = data.split("\n")
        embed = Embed(title="Excuses", description=random.choice(lines), color=Color.gold())

        await ctx.send(embed=embed)

    @command()
    async def neko(self, ctx: Context) -> None:
        """Shows a neko."""
        async with aiohttp.ClientSession() as session:
            async with session.get(nekos["sfw"]) as neko:
                if neko.status == 200:
                    img = await neko.json()
                    neko_em = discord.Embed(colour=0x690E8)
                    neko_em.set_image(url=img["neko"])
                    await ctx.send(embed=neko_em)
                else:
                    raise ServiceError(f"ERROR CODE: {neko.status})")

    @command()
    async def xkcd(self, ctx: Context, comic_type: str = "latest") -> None:
        """Get your favorite xkcd comics."""
        comic_type = comic_type.lower()

        if comic_type not in ["latest", "random"]:
            url = f"https://xkcd.com/{comic_type}/info.0.json"
        else:
            url = "https://xkcd.com/info.0.json"

        if comic_type == "random":
            async with aiohttp.ClientSession() as session:
                async with session.get("https://xkcd.com/info.0.json") as r:
                    data = await r.json()
                random_comic = random.randint(1, data["num"])

                url = f"https://xkcd.com/{random_comic}/info.0.json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    data = await r.json()
                    day, month, year = data["day"], data["month"], data["year"]
                    comic_num = data["num"]

                    embed = discord.Embed(title=data["title"], description=data["alt"], color=Color.blurple())
                    embed.set_image(url=data["img"])
                    embed.set_footer(text=f"Comic date : [{day}/{month}/{year}] | Comic Number - {comic_num}")

                    await ctx.send(embed=embed)
                else:
                    url = "https://xkcd.com/info.0.json"
                    async with aiohttp.ClientSession() as csession:
                        async with csession.get(url) as req:
                            data = await req.json()
                            latest_comic_num = data["num"]

                    help_embed = discord.Embed(
                        title="XKCD HELP",
                        description=f"""
                        **{constants.COMMAND_PREFIX}xkcd latest** - (Get the latest comic)
                        **{constants.COMMAND_PREFIX}xkcd <num>** - (Enter a comic number | range 1 to {latest_comic_num})
                        **{constants.COMMAND_PREFIX}xkcd random** - (Get a random comic)
                        """,
                    )
                    await ctx.send(embed=help_embed)

    @command()
    async def slap(self, ctx: Context, member: discord.Member = None) -> None:
        """Slap a User."""
        if member == ctx.author.mention or member is None:
            embed = Embed(title="Slap In The Face!", description=f"{ctx.author.mention} got slapped him/her self LMAO!", color=Color.blurple(),)
            embed.set_image(url="https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif")
        else:
            embed = Embed(
                title="Slap In The Face!", description=f"{member.mention} got slapped in the face by {ctx.author.mention}!", color=Color.blurple()
            )
            embed.set_image(url="https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif")
        await ctx.send(embed=embed)

    @command()
    async def punch(self, ctx: Context, member: discord.Member = None) -> None:
        """Punch a User."""
        img_links = [
            "https://media.giphy.com/media/13HXKG2HGN8aPK/giphy.gif",
            "https://media.giphy.com/media/dAknWZ0gEXL4A/giphy.gif",
        ]
        if member == ctx.author.mention or member is None:
            embed = Embed(title="Punch In The Face!", description=f"{ctx.author.mention} punched him/her self LMAO!", color=Color.blurple(),)
            embed.set_image(url=random.choice(img_links))
        else:
            embed = Embed(
                title="Punch In The Face!", description=f"{member.mention} got punched in the face by {ctx.author.mention}!", color=Color.blurple()
            )
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
        # TODO: Adding points here should increase their rank in leaderboard.

    @cookie.error
    async def cookie_error(self, ctx: Context, error: Exception) -> None:
        if isinstance(error, BadArgument):
            embed = Embed(title="❌ERROR", description="You can only get a cookie **Once Every 2 Hours**.", color=Color.red(),)
            await ctx.send(embed=embed)

    @command()
    @cooldown(1, 5, BucketType.user)
    async def tweet(self, ctx: Context, username: str, *, text: str) -> None:
        """Tweet as someone."""
        async with ctx.typing():
            base_url = "https://nekobot.xyz/api/imagegen?type=tweet"
            async with self.session.get(f"{base_url}&username={username}&text={text}") as r:
                res = await r.json()

            embed = Embed(color=Color.dark_green())
            embed.set_image(url=res["message"])
        await ctx.send(embed=embed)

    @command()
    @cooldown(1, 5, BucketType.user)
    async def clyde(self, ctx: Context, *, text: str) -> None:
        """Make clyde say something."""
        async with ctx.typing():
            async with self.session.get(f"https://nekobot.xyz/api/imagegen?type=clyde&text={text}") as r:
                res = await r.json()

            embed = discord.Embed(color=Color.dark_green())
            embed.set_image(url=res["message"])
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Fun(bot))
