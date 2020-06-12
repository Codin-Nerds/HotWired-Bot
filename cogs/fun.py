import random

from cogs.utils.embedHandler import error_embed, info
import urllib
from cogs.utils.errors import *
from .utils.plainreq import get_req
from .endpoints.endpoints import nekos


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_agent = {"User-Agent": "HotWired"}
        self.dadjoke = {
            "User-Agent": "HotWired",
            "Accept": "text/plain",
        }

    @commands.command()
    async def cat(self, ctx):
        """Random cat images. Awww, so cute! Powered by random.cat"""
        async with self.bot.session.get(
                "https://aws.random.cat/meow", headers=self.user_agent
        ) as r:
            if r.status == 200:
                js = await r.json()
                em = discord.Embed(name="random.cat", colour=0x690E8)
                em.set_image(url=js["file"])
                await ctx.send(embed=em)
            else:
                raise ServiceError(
                    f"could not fetch cute cat" " :( (http {r.status})"
                )

    @commands.command()
    async def httpcat(self, ctx, http_id: int):
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
            raise commands.BadArgument("Specified HTTP code invalid")

    @commands.command()
    async def dog(self, ctx):
        """Random doggos just because!"""

        def decide_source():
            n = random.random()
            if n < 0.5:
                return "https://random.dog/woof"
            elif n > 0.5:
                return "https://dog.ceo/api/breeds/image/random"

        async with self.bot.session.get(
                decide_source(), headers=self.user_agent
        ) as shibe_get:
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
                raise ServiceError(
                    f"could not fetch pupper :(" " (http {shibe_get.status})"
                )

    @commands.command()
    async def lizard(self, ctx):
        """Shows a random lizard picture"""
        async with self.bot.session.get(
                "https://nekos.life/api/lizard", headers=self.user_agent
        ) as lizr:
            if lizr.status == 200:
                img = await lizr.json()
                liz_em = discord.Embed(colour=0x690E8)
                liz_em.set_image(url=img["url"])
                await ctx.send(embed=liz_em)
            else:
                raise ServiceError(
                    f"something went boom" " (http {lizr.status})"
                )

    @commands.command()
    async def why(self, ctx):
        """Why _____?"""
        async with self.bot.session.get(
                "https://nekos.life/api/why", headers=self.user_agent
        ) as why:
            if why.status == 200:
                why_js = await why.json()
                why_em = discord.Embed(
                    title=f"{ctx.author.name} wonders...",
                    description=why_js["why"],
                    colour=0x690E8,
                )
                await ctx.send(embed=why_em)
            else:
                raise ServiceError(
                    f"something went boom " "(http {why.status})"
                )

    @commands.command(aliases=["rhash", "robothash", "rh", "rohash"])
    async def robohash(self, ctx, *, meme: str):
        """text => robot image thing"""
        try:
            e = discord.Embed(colour=0x690E8)
            meme = urllib.parse.quote_plus(meme)
            e.set_image(url=f"https://robohash.org/{meme}.png")
            await ctx.send(embed=e)
        except Exception as e:
            raise ServiceError(f"something broke: {e!s}")

    async def get_answer(self, ans: str):
        if ans == "yes":
            return "Yes."
        elif ans == "no":
            return "NOPE"
        elif ans == "maybe":
            return "maaaaaaybe?"
        else:
            raise commands.BadArgument("internal error: invalid answer lmaoo")

    @commands.command(aliases=["shouldi", "ask"])
    async def yesno(self, ctx, *, question: str):
        """Why not make your decisions with a bot?"""
        async with ctx.bot.session.get(
                "https://yesno.wtf/api", headers=self.user_agent
        ) as meme:
            if meme.status == 200:
                mj = await meme.json()
                ans = await self.get_answer(mj["answer"])
                em = discord.Embed(
                    title=ans,
                    description="And the answer to" f" {question} is this",
                    colour=0x690E8,
                )
                em.set_image(url=mj["image"])
                await ctx.send(embed=em)
            else:
                raise ServiceError(f"oof (http {meme.status})")

    @commands.command(aliases=["dadjoke", "awdad", "dadpls", "shitjoke", "badjoke"])
    async def joke(self, ctx):
        """Dad joke simulator 3017, basically"""
        async with ctx.bot.session.get(
                "https://icanhazdadjoke.com", headers=self.dadjoke
        ) as jok:
            if jok.status == 200:
                res = await jok.text()
                res = res.encode("utf-8").decode("utf-8")
                await ctx.send(f"`{res}`")
            else:
                raise ServiceError(f"rip dad (http {jok.status})")

    @commands.command(aliases=["bofh", "techproblem"])
    async def excuse(self, ctx):
        """Bastard Operator from Hell excuses.
        Source: http://pages.cs.wisc.edu/~ballard/bofh
        """
        async with self.bot.session.get(
                "http://pages.cs.wisc.edu" "/~ballard/bofh/excuses"
        ) as r:
            data = await r.text()
            lines = data.split("\n")
            line = random.choice(lines)
            await ctx.send(f"`{line}`")

    @commands.command()
    async def neko(self, ctx):
        """Shows a neko"""
        async with get_req(ctx.bot.session, nekos["sfw"]) as neko:
            if neko.status == 200:
                img = await neko.json()
                neko_em = discord.Embed(colour=0x690E8)
                neko_em.set_image(url=img["neko"])
                await ctx.send(embed=neko_em)
            else:
                raise ServiceError(f"ERROR CODE: {neko.status})")


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
