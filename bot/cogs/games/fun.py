import os
import random
import textwrap
import urllib
from random import choice, randint
import io

import nekos
import aiohttp
import discord
from discord import Color, Embed, Member
from discord.ext.commands import (
    BadArgument,
    BucketType,
    Cog,
    Context,
    command,
    cooldown,
    is_nsfw,
)

from bot import config
from bot.core.bot import Bot

file = open(os.path.sep.join(("bot", "assets", "excuses.txt")), "r", encoding="utf-8")
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

    @command()
    async def joke(self, ctx: Context) -> None:
        """Send a random joke."""
        async with self.bot.session.get("https://mrwinson.me/api/jokes/random") as resp:
            if resp.status == 200:
                data = await resp.json()
                joke = data["joke"]
                embed = Embed(
                    description=joke,
                    color=Color.gold()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Something went boom! :( [CODE: {resp.status}]")

    @command()
    async def duck(self, ctx: Context) -> None:
        """Get a random picture of a duck."""
        async with self.bot.session.get("https://random-d.uk/api/v2/random") as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = Embed(
                    title="Random Duck!",
                    color=Color.gold()
                )
                embed.set_image(url=data["url"])
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Something went boom! :( [CODE: {resp.status}]")

    @command()
    async def koala(self, ctx: Context) -> None:
        """Get a random picture of a koala."""
        async with self.bot.session.get("https://some-random-api.ml/img/koala") as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = Embed(
                    title="Random Koala!",
                    color=Color.gold()
                )
                embed.set_image(url=data["link"])
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Something went boom! :( [CODE: {resp.status}]")

    @command()
    async def panda(self, ctx: Context) -> None:
        """Get a random picture of a panda."""
        async with self.bot.session.get("https://some-random-api.ml/img/panda",) as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = Embed(
                    title="Random Panda!",
                    color=Color.gold(),
                )
                embed.set_image(url=data["link"])
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Something went boom! :( [CODE: {resp.status}]")

    @command()
    async def catfact(self, ctx: Context) -> None:
        """Send a random cat fact."""
        # I advise you to use a background task to update the facts.
        # Example : https://github.com/Faholan/All-Hail-Chaos/blob/60b6ce944c66ccea6890019e6a196ac06f1eb55e/cogs/animals.py#L47
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cat-fact.herokuapp.com/facts") as response:
                self.all_facts = await response.json()

        fact = choice(self.all_facts["all"])
        await ctx.send(embed=Embed(
            title="Did you Know?",
            description=fact["text"],
            color=0x690E8
        ))

    @command()
    async def textcat(self, ctx: Context) -> None:
        """Send a random textcat."""
        try:
            embed = Embed(
                description=nekos.textcat(),
                color=0x690E8
            )
            await ctx.send(embed=embed)
        except nekos.errors.NothingFound:
            await ctx.send("Couldn't Fetch Textcat! :(")

    @command()
    async def whydoes(self, ctx: Context) -> None:
        """Send a random why."""
        try:
            embed = Embed(
                description=nekos.why(),
                color=0x690E8
            )
            await ctx.send(embed=embed)
        except nekos.errors.NothingFound:
            await ctx.send('Couldn\'t Fetch any "WHY!" :(')

    @command()
    async def fact(self, ctx: Context) -> None:
        """Send a random fact."""
        try:
            embed = Embed(
                description=nekos.fact(),
                color=0x690E8
            )
            await ctx.send(embed=embed)
        except nekos.errors.NothingFound:
            await ctx.send('Couldn\'t Fetch any "Fact" :(')

    @command()
    @is_nsfw()
    async def image(self, ctx: Context, img_type: str) -> None:
        """Sends a random image(sfw and nsfw)."""
        try:
            embed = Embed(color=0x690E8)
            embed.set_image(url=nekos.img(img_type))
            await ctx.send(embed=embed)
        except nekos.errors.InvalidArgument:
            await ctx.send(f"Invalid type! Possible types are : ```{', '.join(config.nsfw_possible)}```")
        except nekos.errors.NothingFound:
            await ctx.send("Sorry, No Images Found.")

    @command()
    async def chuck(self, ctx: Context) -> None:
        """Get a random Chuck Norris joke."""
        if randint(0, 1):
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.chucknorris.io/jokes/random") as r:
                    joke = await r.json()
                    await ctx.send(joke["value"])
                    return

        if ctx.guild:
            if not ctx.channel.is_nsfw():
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://api.icndb.com/jokes/random?exclude=[explicit]") as r:
                        joke = await r.json()
                        await ctx.send(joke["value"]["joke"])
                        return

        async with aiohttp.ClientSession() as session:
            async with session.get("http://api.icndb.com/jokes/random") as response:
                joke = await response.json()
                await ctx.send(joke["value"]["joke"].replace("&quote", '"'))

    @command()
    async def cat(self, ctx: Context) -> None:
        """Random cat images. Awww, so cute! Powered by random.cat."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/img/cat") as response:
                if response.status == 200:
                    json = await response.json()
                    embed = Embed(
                        name="random.cat",
                        colour=0x690E8
                    )
                    embed.set_image(url=json["link"])
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Couldn't Fetch cute cats :( [CODE: {response.status}]")

    @command()
    async def httpcat(self, ctx: Context, http_id: int) -> None:
        """http.cat images."""
        if http_id in config.http_codes:
            httpcat_em = Embed(
                name="http.cat",
                colour=0x690E8
            )
            httpcat_em.set_image(url=f"https://http.cat/{http_id}.jpg")

            await ctx.send(embed=httpcat_em)
        else:
            await ctx.send("Invalid HTTP Code Specified")

    @command()
    async def fox(self, ctx: Context) -> None:
        """Send a random fox picture."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://randomfox.ca/floof/") as response:
                picture = await response.json()
        embed = Embed(
            title="Fox",
            color=0x690E8
        )
        embed.set_image(url=picture["image"])
        await ctx.send(embed=embed)

    @command()
    async def dog(self, ctx: Context) -> None:
        """Random doggos just because."""
        def decide_source() -> str:
            number = random.randint(0, 1)
            if number:
                return "https://random.dog/woof"
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
                        shibe_em = Embed(colour=0x690E8)
                        shibe_em.set_image(url=shibe_url)
                        await ctx.send(embed=shibe_em)
                else:
                    await ctx.send(f"Couldn't Fetch cute doggos :( [status : {shibe_get.status}]")

    @command()
    async def lizard(self, ctx: Context) -> None:
        """Shows a random lizard picture."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/lizard", headers=self.user_agent) as lizr:
                if lizr.status == 200:
                    img = await lizr.json()
                    liz_em = Embed(colour=0x690E8)
                    liz_em.set_image(url=img["url"])
                    await ctx.send(embed=liz_em)
                else:
                    await ctx.send(f"Something went boom! :( [CODE: {lizr.status}]")

    @command(aliases=["leet"])
    async def leetify(self, ctx: Context, *, content: str) -> None:
        """Give each letter of a given message a different markdown style."""
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
                    why_em = Embed(
                        title=f"{ctx.author.name} wonders...",
                        description=why_js["why"],
                        colour=0x690E8
                    )
                    await ctx.send(embed=why_em)
                else:
                    await ctx.send(f"Something went Boom! [CODE : {why.status}]")

    @command(aliases=["rhash", "robothash", "rh", "rohash"])
    async def robohash(self, ctx: Context, *, meme: str) -> None:
        """Text => robot image thing."""
        try:
            embed = Embed(colour=0x690E8)
            meme = urllib.parse.quote_plus(meme)
            embed.set_image(url=f"https://robohash.org/{meme}.png")
            await ctx.send(embed=embed)
        except Exception as error:
            await ctx.send(f"Something Broke. LOL [{error}]")

    async def get_answer(self, ans: str) -> str:
        return_str = ""
        if ans == "yes":
            return_str = "Yes."
        elif ans == "no":
            return_str = "NOPE"
        elif ans == "maybe":
            return_str = "maaaaaaybe?"
        else:
            return_str = "Internal Error: Invalid answer LMAOO"

        return return_str

    @command(aliases=["shouldi", "ask"])
    async def yesno(self, ctx: Context, *, question: str) -> None:
        """Let the bot answer a yes/no question for you."""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://yesno.wtf/api", headers=self.user_agent) as meme:
                if meme.status == 200:
                    mj = await meme.json()
                    ans = await self.get_answer(mj["answer"])
                    em = Embed(
                        title=ans,
                        description=f"And the answer to {question} is this:",
                        colour=0x690E8
                    )
                    em.set_image(url=mj["image"])
                    await ctx.send(embed=em)
                else:
                    await ctx.send(f"OMFG! [STATUS : {meme.status}]")

    @command(aliases=["awdad", "dadpls", "shitjoke", "badjoke"])
    async def dadjoke(self, ctx: Context) -> None:
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
        """Bastard Operator from Hell excuses.

        Source: http://pages.cs.wisc.edu/~ballard/bofh
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("http://pages.cs.wisc.edu/~ballard/bofh/excuses") as r:
                data = await r.text()

        lines = data.split("\n")
        embed = Embed(
            title="Excuses",
            description=random.choice(lines),
            color=Color.gold()
        )

        await ctx.send(embed=embed)

    @command()
    async def inspireme(self, ctx: Context) -> None:
        """Fetch a random "inspirational message" from the bot."""
        try:
            async with self.bot.session.get("http://inspirobot.me/api?generate=true") as page:
                picture = await page.text(encoding="utf-8")
                embed = Embed()
                embed.set_image(url=picture)
                await ctx.send(embed=embed)

        except Exception:
            await ctx.send("Oops, there was a problem!")

    @command()
    async def slap(self, ctx: Context, member: discord.Member = None) -> None:
        """Slap a user."""
        if member == ctx.author.mention or member is None:
            embed = Embed(
                title="Slap In The Face!",
                description=f"{ctx.author.mention} got slapped him/her self LMAO!",
                color=Color.blurple()
            )
            embed.set_image(
                url="https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif"
            )
        else:
            embed = Embed(
                title="Slap In The Face!", description=f"{member.mention} got slapped in the face by {ctx.author.mention}!",
                color=Color.blurple()
            )
            embed.set_image(
                url="https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif"
            )
        await ctx.send(embed=embed)

    @command()
    async def punch(self, ctx: Context, member: discord.Member = None) -> None:
        """Punch a user."""
        img_links = [
            "https://media.giphy.com/media/13HXKG2HGN8aPK/giphy.gif",
            "https://media.giphy.com/media/dAknWZ0gEXL4A/giphy.gif",
        ]
        if member == ctx.author.mention or member is None:
            embed = Embed(
                title="Punch In The Face!",
                description=f"{ctx.author.mention} punched him/her self LMAO!",
                color=Color.blurple()
            )
            embed.set_image(url=random.choice(img_links))
        else:
            embed = Embed(
                title="Punch In The Face!", description=f"{member.mention} got punched in the face by {ctx.author.mention}!",
                color=Color.blurple()
            )
            embed.set_image(url=random.choice(img_links))
        await ctx.send(embed=embed)

    @command()
    async def shoot(self, ctx: Context, member: discord.Member) -> None:
        """Shoot a user."""
        embed = Embed(
            title="Boom! Bam! He's Dead!",
            description=f"{member.mention} shot by {ctx.author.mention} :gun: :boom:",
            color=Color.blurple()
        )
        embed.set_image(
            url="https://media.giphy.com/media/xT9IguC6bxYHsGIRb2/giphy.gif"
        )
        await ctx.send(embed=embed)

    @command(aliases=["table", "flip", "tableflip"])
    async def throw(self, ctx: Context) -> None:
        """Throw the table."""
        embed = Embed(
            title="Table Throw!",
            description=f"{ctx.author.mention} threw the table! :boom:",
            color=Color.blurple()
        )
        embed.set_image(
            url="https://media.giphy.com/media/pzFB1KY4wob0jpbuPa/giphy.gif"
        )
        await ctx.send(embed=embed)

    @command(aliases=["cookies", "cook"])
    @cooldown(1, 30, BucketType.user)
    async def cookie(self, ctx: Context, member: discord.Member) -> None:
        """Give a user a cookie."""
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
                color=Color.blurple()
            )
            embed.set_image(
                url="https://media.giphy.com/media/7GYHmjk6vlqY8/giphy.gif"
            )
        else:
            embed = Embed(
                title="Cookie Giver!",
                description=textwrap.dedent(
                    f"""
                    {author} got a cookie{actor}! ➡ :cookie: :cookie: :cookie:
                    *You got +{num} points!**"
                    """
                ),
                color=Color.blurple()
            )
        await ctx.send(embed=embed)
        # TODO : Add points after db integration
        # TODO: Adding points here should increase their rank in leaderboard.

    @cookie.error
    async def cookie_error(self, ctx: Context, error: Exception) -> None:
        """Manage errors from the cookie command."""
        if isinstance(error, BadArgument):
            embed = Embed(
                title="❌ERROR",
                description="You can only get a cookie **Once Every 2 Hours**.",
                color=Color.red()
            )
            await ctx.send(embed=embed)

    @command()
    @cooldown(1, 5, BucketType.user)
    async def tweet(self, ctx: Context, username: str, *, text: str) -> None:
        """Tweet as someone."""
        async with ctx.typing():
            base_url = "https://nekobot.xyz/api/imagegen?type=tweet"
            async with self.bot.session.get(f"{base_url}&username={username}&text={text}") as r:
                res = await r.json()

            embed = Embed(color=Color.dark_green())
            embed.set_image(url=res["message"])
        await ctx.send(embed=embed)

    @command()
    @cooldown(1, 5, BucketType.user)
    async def clyde(self, ctx: Context, *, text: str) -> None:
        """Make clyde say something."""
        async with ctx.typing():
            async with self.bot.session.get(f"https://nekobot.xyz/api/imagegen?type=clyde&text={text}") as r:
                res = await r.json()

            embed = discord.Embed(color=Color.dark_green())
            embed.set_image(url=res["message"])
        await ctx.send(embed=embed)

    @command()
    async def avatar(self, ctx: Context, member: Member) -> None:
        embed = discord.Embed(
            color=Color.blue(),
            title="→ Avatar"
        )
        embed.set_image(url=member.avatar_url_as(size=1024, format=None, static_format="png"))

        await ctx.send(embed=embed)

    @command()
    async def history(self, ctx: Context):
        async with self.bot.session.get('http://numbersapi.com/random/date?json') as r:
            res = await r.json()
            embed = discord.Embed(
                color=Color.blue(),
                title="→ Random History Date!",
                description=f"• Fact: {res['text']}"
                            f"\n• Year: {res['year']}"
            )

            await ctx.send(embed=embed)

    @command()
    async def howgay(self, ctx: Context, member: Member) -> None:
        embed = discord.Embed(
            color=Color.blue(),
            title="→ Howgay?"
        )
        embed.add_field(
            name="The account is...",
            value=f"{random.randint(1, 100)}% gay :gay_pride_flag: → {str(member.mention)}"
        )

        await ctx.send(embed=embed)

    @command()
    async def math(self, ctx: Context) -> None:
        async with self.bot.session.get('http://numbersapi.com/random/math?json') as r:
            res = await r.json()
            embed = discord.Embed(
                color=Color.blue(),
                title="→ Random Math Fact!",
                description=f"• Fact: {res['text']}"
                            f"\n• Number: {res['number']}"
            )
            await ctx.send(embed=embed)

    @command()
    async def advice(self, ctx: Context) -> None:
        async with self.bot.session.get('https://api.adviceslip.com/advice') as r:
            res = await r.json(content_type="text/html")
            embed = discord.Embed(
                color=Color.blue(),
                title="→ Random Advice!",
                description=f"• Advice: {res['slip']['advice']}"
            )

            await ctx.send(embed=embed)

    @command()
    async def bill(self, ctx):
        async with self.bot.session.get('https://belikebill.ga/billgen-API.php?default=1') as r:
            res = io.BytesIO(await r.read())
            bill_file = discord.File(res, filename="bill.jpg")

            await ctx.send(file=bill_file)

    @command()
    async def trumptweet(self, ctx: Context, *, text: str) -> None:
        async with self.bot.session.get(f"https://nekobot.xyz/api/imagegen?type=trumptweet&text={text}") as r:
            res = await r.json()
            embed = discord.Embed(
                color=Color.blue(),
                title="→ Trump Tweet"
            )
            embed.set_image(url=res["message"])

            await ctx.send(embed=embed)

    @command()
    async def vs(self, ctx: Context, member1: Member, member2: Member) -> None:
        member1 = member1.avatar_url_as(size=1024, format=None, static_format='png')
        member2 = member2.avatar_url_as(size=1024, format=None, static_format='png')
        async with self.bot.session.get(
                f"https://nekobot.xyz/api/imagegen?type=whowouldwin&user1={member1}&user2={member2}") as r:
            res = await r.json()
            embed = discord.Embed(
                color=Color.blue(),
                title="→ Who Would Win"
            )
            embed.set_image(url=res["message"])

            await ctx.send(embed=embed)

    @command()
    async def youtube(self, ctx: Context, *, comment: str) -> None:
        picture = ctx.author.avatar_url_as(size=1024, format=None, static_format='png')
        async with self.bot.session.get(f"https://some-random-api.ml/canvas/youtube-comment?avatar={picture}&username={ctx.author.name}&comment={comment}") as r:
            res = io.BytesIO(await r.read())
            youtube_file = discord.File(res, filename="youtube.jpg")
            embed = discord.Embed(
                color=Color.blue(),
                title="→ Youtube comment"
            )
            embed.set_image(url="attachment://youtube.jpg")

            await ctx.send(embed=embed, file=youtube_file)

    @command(brief="Wallpaper", description="Get yourself a wallpaper")
    @cooldown(1, 5, BucketType.user)
    @is_nsfw()
    async def wallpaper(self, ctx):
        """ Get yourself a (cool?) wallpaper """
        async with self.bot.session.get('https://nekos.life/api/v2/img/wallpaper') as r:
            r = await r.json()
        await ctx.send(embed=discord.Embed(color=Color.blue()).set_image(url=r['url']))


def setup(bot: Bot) -> None:
    """Load the Func cog."""
    bot.add_cog(Fun(bot))
