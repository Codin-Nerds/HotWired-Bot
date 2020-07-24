import os
import random
import textwrap
import typing as t
import urllib

import aiohttp
import discord
import nekos
from discord.ext.commands import (BadArgument, BucketType, Cog, Context,
                                  command, cooldown, errors, is_nsfw)

from bot.core.bot import Bot
from bot.utils.errors import ServiceError

file = open("bot/assets" + os.path.sep + "excuses.txt", "r", encoding="utf-8")
excuses = file.readlines()
file.close()


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
        fact = random.choice(self.all_facts["all"])
        await ctx.send(embed=discord.Embed(
            title="Did you Know?",
            description=fact["text"],
            color=0x690E8
        ))

    @command()
    async def textcat(self, ctx: Context) -> None:
        """Sends a random textcat"""
        try:
            embed = discord.Embed(
                description=nekos.textcat(),
                color=0x690E8
            )
            await ctx.send(embed=embed)
        except nekos.errors.NothingFound:
            await ctx.send("Couldn't Fetch Textcat! :(")

    @command()
    async def whydoes(self, ctx: Context) -> None:
        """Sends a random why?__"""
        try:
            embed = discord.Embed(
                description=nekos.why(),
                color=0x690E8
            )
            await ctx.send(embed=embed)
        except nekos.errors.NothingFound:
            await ctx.send('Couldn\'t Fetch any "WHY!" :(')

    @command()
    async def fact(self, ctx: Context) -> None:
        """Sends a random fact"""
        try:
            embed = discord.Embed(
                description=nekos.fact(),
                color=0x690E8
            )
            await ctx.send(embed=embed)
        except nekos.errors.NothingFound:
            await ctx.send('Couldn\'t Fetch any "Fact" :(')

    @command()
    @is_nsfw()
    async def image(self, ctx: Context, type: str) -> None:
        """Sends a random image(sfw and nsfw)."""
        try:
            embed = discord.Embed(
                color=0x690E8
            )
            embed.set_image(url=nekos.img(type))
            await ctx.send(embed=embed)
        except errors.NSFWChannelRequired:
            await ctx.send("Hey dude! Go use this command in a NSFW Channel, this ain't ur home.")
        except nekos.errors.InvalidArgument:
            await ctx.send(f"Invalid type! Possible types are : ```{', '.join(self.bot.nsfw_possible)}```")
        except nekos.errors.NothingFound:
            await ctx.send("Sorry, No Images Found.")

    @command()
    async def chuck(self, ctx: Context) -> t.Union[None, discord.Message]:
        """Get a random Chuck Norris joke."""
        if random.randint(0, 1):
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
                    em = discord.Embed(
                        name="random.cat",
                        colour=0x690E8
                    )
                    em.set_image(url=js["file"])
                    await ctx.send(embed=em)
                else:
                    await ctx.send(f"Couldn't Fetch cute cats :( [status : {r.status}]")

    @command()
    async def httpcat(self, ctx: Context, http_id: int) -> None:
        """http.cat images."""
        if http_id in self.bot.http_codes:
            httpcat_em = discord.Embed(
                name="http.cat",
                colour=0x690E8
            )
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
        embed = discord.Embed(
            title="Fox",
            color=0x690E8
        )
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

    @command(aliases=["leet"])
    async def leetify(self, ctx: Context, *, content: str) -> None:
        """Gives each letter of a given message a different markdown style."""

        leetters = {
            "a": ["A", "4"],
            "e": ["E", "3"],
            "i": ["1", "I", "i"],
            "o": ["O", "0", "o"],
            "s": ["5", "S", "s"]
        }
        content = content.lower()
        leetified_content = ""
        prev_md = ""
        for letter in content:
            if letter in leetters.keys():
                leet_char = random.choice(leetters[letter])
            else:
                leet_char = random.choice([letter, letter.upper()])

            # Apply markdown without using the same style next to each other
            md_list = ["*", "**", "***", "__", "", "`"]
            if prev_md == "":
                md_list.remove("")
            elif "*" in prev_md:
                md_list.remove("*")
                md_list.remove("**")
                md_list.remove("***")
            elif prev_md == "__":
                md_list.remove("__")
            elif prev_md == "`":
                md_list.remove("`")
            random.seed(random.randint(421, 294244))
            chosen_md = random.choice(md_list)
            prev_md = chosen_md
            leetified_content += f"{chosen_md}{leet_char}{chosen_md}"

        await ctx.send(f"{leetified_content}\n-{ctx.message.author.mention}")

    @command()
    async def why(self, ctx: Context) -> None:
        """Why?."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/why", headers=self.user_agent) as why:
                if why.status == 200:
                    why_js = await why.json()
                    why_em = discord.Embed(
                        title=f"{ctx.author.name} wonders...",
                        description=why_js["why"],
                        colour=0x690E8
                    )
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
                    em = discord.Embed(
                        title=ans,
                        description=f"And the answer to {question} is this:",
                        colour=0x690E8
                    )
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
        embed = discord.Embed(
            title="Excuses",
            description=random.choice(lines),
            color=discord.Color.gold()
        )

        await ctx.send(embed=embed)

    @command()
    async def inspireme(self, ctx: Context) -> None:
        """Fetch a random "inspirational message" from the bot."""
        try:
            async with self.session.get("http://inspirobot.me/api?generate=true") as page:
                picture = await page.text(encoding="utf-8")
                embed = discord.Embed()
                embed.set_image(url=picture)
                await ctx.send(embed=embed)
        except Exception:
            await ctx.send("Oops, there was a problem!")

    @command()
    async def neko(self, ctx: Context) -> None:
        """Shows a neko."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.bot.nekos["sfw"]) as neko:
                if neko.status == 200:
                    img = await neko.json()
                    neko_em = discord.Embed(colour=0x690E8)
                    neko_em.set_image(url=img["neko"])
                    await ctx.send(embed=neko_em)
                else:
                    raise ServiceError(f"ERROR CODE: {neko.status})")

    @command()
    async def slap(self, ctx: Context, member: discord.Member = None) -> None:
        """Slap a User."""
        if member == ctx.author.mention or member is None:
            embed = discord.Embed(
                title="Slap In The Face!",
                description=f"{ctx.author.mention} got slapped him/her self LMAO!",
                color=discord.Color.blurple()
            )
            embed.set_image(
                url="https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif")
        else:
            embed = discord.Embed(
                title="Slap In The Face!", description=f"{member.mention} got slapped in the face by {ctx.author.mention}!",
                color=discord.Color.blurple()
            )
            embed.set_image(
                url="https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif")
        await ctx.send(embed=embed)

    @command()
    async def punch(self, ctx: Context, member: discord.Member = None) -> None:
        """Punch a User."""
        img_links = [
            "https://media.giphy.com/media/13HXKG2HGN8aPK/giphy.gif",
            "https://media.giphy.com/media/dAknWZ0gEXL4A/giphy.gif",
        ]
        if member == ctx.author.mention or member is None:
            embed = discord.Embed(
                title="Punch In The Face!",
                description=f"{ctx.author.mention} punched him/her self LMAO!",
                color=discord.Color.blurple()
            )
            embed.set_image(url=random.choice(img_links))
        else:
            embed = discord.Embed(
                title="Punch In The Face!", description=f"{member.mention} got punched in the face by {ctx.author.mention}!",
                color=discord.Color.blurple()
            )
            embed.set_image(url=random.choice(img_links))
        await ctx.send(embed=embed)

    @command()
    async def shoot(self, ctx: Context, member: discord.Member) -> None:
        """Shoot a User."""
        embed = discord.Embed(
            title="Boom! Bam! He's Dead!",
            description=f"{member.mention} shot by {ctx.author.mention} :gun: :boom:",
            color=discord.Color.blurple()
        )
        embed.set_image(
            url="https://media.giphy.com/media/xT9IguC6bxYHsGIRb2/giphy.gif")
        await ctx.send(embed=embed)

    @command(aliases=["table", "flip", "tableflip"])
    async def throw(self, ctx: Context) -> None:
        """Throw the table."""
        embed = discord.Embed(
            title="Table Throw!",
            description=f"{ctx.author.mention} threw the table! :boom:",
            color=discord.Color.blurple()
        )
        embed.set_image(
            url="https://media.giphy.com/media/pzFB1KY4wob0jpbuPa/giphy.gif"
        )
        await ctx.send(embed=embed)

    @command(aliases=["cookies", "cook"])
    @cooldown(1, 30, BucketType.user)
    async def cookie(self, ctx: Context, member: discord.Member) -> None:
        """Give a User a cookie."""
        num = random.randint(1, 4)

        author = "You're a" if ctx.author == member else f"{member.mention} is"
        actor = f" from {ctx.author.mention}" if ctx.author != member else ""

        if num == 1:
            embed = discord.Embed(
                title="Cookie Giver!",
                description=textwrap.dedent(
                    f"""
                    {author} Lucky Guy! You got a **Huge Cookie**{actor}!
                    **You got +10 points!**
                    """
                ),
                color=discord.Color.blurple()
            )
            embed.set_image(
                url="https://media.giphy.com/media/7GYHmjk6vlqY8/giphy.gif")
        else:
            embed = discord.Embed(
                title="Cookie Giver!",
                description=textwrap.dedent(
                    f"""
                    {author} got a cookie{actor}! ➡ :cookie: :cookie: :cookie:
                    *You got +{num} points!**"
                    """
                ),
                color=discord.Color.blurple()
            )
        await ctx.send(embed=embed)
        # TODO : Add points after db integration
        # TODO: Adding points here should increase their rank in leaderboard.

    @cookie.error
    async def cookie_error(self, ctx: Context, error: Exception) -> None:
        if isinstance(error, BadArgument):
            embed = discord.Embed(
                title="❌ERROR",
                description="You can only get a cookie **Once Every 2 Hours**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


# TODO: kiss, hug, pat => commands to be added cuddle hug insult kiss lick nom pat poke slap stare highfive bite
#  greet punch handholding tickle kill hold pats wave boop


def setup(bot: Bot) -> None:
    bot.add_cog(Fun(bot))
