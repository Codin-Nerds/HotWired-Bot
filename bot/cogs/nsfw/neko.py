import requests

from random import choice

from discord import Color, Embed, User
from discord.ext.commands import Cog, Context, Bot, group, is_nsfw


class NSFW(Cog):
    conf = {}

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.config = bot.config

    async def get(self, url: str, author: User) -> Embed:
        base = 'https://api.nekos.dev/api/v3/'

        req = requests.get(base + url)
        req = req.json()

        embed = Embed(color=Color.red())
        embed.title = f"Requested by {author.name}"
        embed.set_image(url=req['data']['response']["url"])
        return embed

    @group()
    async def neko(self, ctx: Context) -> None:
        """Query nekos-life."""
        pass

    @neko.command()
    async def neko(self, ctx: Context) -> None:
        async with ctx.typing():
            sources = ["images/sfw/img/neko", "images/sfw/gif/neko"]
            source = choice(sources)

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def nsfw(self, ctx: Context) -> None:
        sources = ["images/nsfw/gif/neko", "images/nsfw/img/neko_lewd", "images/nsfw/img/neko_ero"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    async def waifu(self, ctx: Context) -> None:
        async with ctx.typing():
            source = "images/sfw/img/waifu"

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    async def kitsune(self, ctx: Context) -> None:
        async with ctx.typing():
            source = "images/sfw/img/kitsune"

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def lewd(self, ctx: Context) -> None:
        sources = ["images/nsfw/img/classic_lewd", "images/nsfw/img/neko_lewd", "images/nsfw/img/neko_ero"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def blowjob(self, ctx: Context) -> None:
        sources = ["images/nsfw/gif/blow_job", "images/nsfw/img/blowjob_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw
    async def furry(self, ctx: Context) -> None:
        sources = ["images/nsfw/gif/yiff", "images/nsfw/img/yiff_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def pussy(self, ctx: Context) -> None:
        sources = ["images/nsfw/gif/pussy_wank", "images/nsfw/gif/pussy", "images/nsfw/img/pussy_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def feet(self, ctx: Context) -> None:
        sources = ["images/nsfw/gif/feet", "images/nsfw/img/feet_lewd", "images/nsfw/img/feet_ero"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw
    async def yuri(self, ctx: Context) -> None:
        sources = ["images/nsfw/gif/yuri", "images/nsfw/img/yuri_lewd", "images/nsfw/img/yuri_ero"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw
    async def solo(self, ctx: Context) -> None:
        sources = ["images/nsfw/gif/girls_solo", "images/nsfw/img/solo_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw
    async def cum(self, ctx: Context) -> None:
        sources = ["images/nsfw/gif/cum", "images/nsfw/img/cum_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw
    async def cunni(self, ctx: Context) -> None:
        source = "images/nsfw/gif/kuni"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw
    async def bdsm(self, ctx: Context) -> None:
        source = "images/nsfw/img/bdsm_lewd"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw
    async def trap(self, ctx: Context) -> None:
        sources = ["images/nsfw/img/trap_lewd", "images/nsfw/img/futanari_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw
    async def femdom(self, ctx: Context) -> None:
        source = "images/nsfw/img/femdom_lewd"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(NSFW(bot))
