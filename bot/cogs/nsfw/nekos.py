import aiohttp

from random import choice

import nekos

from discord import Color, Embed, User
from discord.ext.commands import Cog, Context, Bot, group, is_nsfw

from bot import config


class Neko(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def get(self, url: str, author: User) -> Embed:
        """Gets pictures from Neko API."""
        base = 'https://api.nekos.dev/api/v3/'

        async with aiohttp.ClientSession() as session:
            async with session.get(base + url) as response:
                req = await response.json()

        embed = Embed(color=Color.red())
        embed.title = f"Requested by {author.name}"
        embed.set_image(url=req['data']['response']["url"])
        return embed

    @group()
    async def neko(self, ctx: Context) -> None:
        """Neko Commands Group."""
        pass

    @neko.command()
    async def nekos(self, ctx: Context) -> None:
        """Gets Neko pics from API."""
        async with ctx.typing():
            sources = ["images/sfw/img/neko", "images/sfw/gif/neko"]
            source = choice(sources)

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def nsfw(self, ctx: Context) -> None:
        """Gets NSFW Neko pics from API"""
        sources = ["images/nsfw/gif/neko", "images/nsfw/img/neko_lewd", "images/nsfw/img/neko_ero"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    async def waifu(self, ctx: Context) -> None:
        """Gets Waifu pics from API."""
        async with ctx.typing():
            source = "images/sfw/img/waifu"

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    async def kitsune(self, ctx: Context) -> None:
        """gets Kitsune pics from API."""
        async with ctx.typing():
            source = "images/sfw/img/kitsune"

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def lewd(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""

        sources = ["images/nsfw/img/classic_lewd", "images/nsfw/img/neko_lewd", "images/nsfw/img/neko_ero"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def blowjob(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/blow_job", "images/nsfw/img/blowjob_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def furry(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/yiff", "images/nsfw/img/yiff_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def pussy(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/pussy_wank", "images/nsfw/gif/pussy", "images/nsfw/img/pussy_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def feet(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/feet", "images/nsfw/img/feet_lewd", "images/nsfw/img/feet_ero"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def yuri(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/yuri", "images/nsfw/img/yuri_lewd", "images/nsfw/img/yuri_ero"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def solo(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/girls_solo", "images/nsfw/img/solo_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def cum(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/cum", "images/nsfw/img/cum_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def cunni(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        source = "images/nsfw/gif/kuni"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def bdsm(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        source = "images/nsfw/img/bdsm_lewd"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def trap(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/img/trap_lewd", "images/nsfw/img/futanari_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def femdom(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        source = "images/nsfw/img/femdom_lewd"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def image(self, ctx: Context, image_type: str = None) -> None:
        """
        Send a random image. It can be NSFW.

        Image Categories:
        ```
        "feet", "yuri", "trap", "futanari", "hololewd", "lewdkemo",
        "solog", "feetg", "cum", "erokemo", "les", "wallpaper",
        "lewdk", "ngif", "tickle", "lewd", "feed", "gecg",
        "eroyuri", "eron", "cum_jpg", "bj", "nsfw_neko_gif", "solo",
        "kemonomimi", "nsfw_avatar", "gasm", "poke", "anal", "slap",
        "hentai", "avatar", "erofeet", "holo", "keta", "blowjob",
        "pussy", "tits", "holoero", "lizard", "pussy_jpg", "pwankg",
        "classic", "kuni", "waifu", "pat", "8ball", "kiss",
        "femdom", "neko", "spank", "cuddle", "erok", "fox_girl",
        "boobs", "random_hentai_gif", "smallboobs", "hug", "ero", "smug",
        "goose", "baka", "woof"
        ```
        """
        if image_type is None:
            await ctx.send(f"Possible types are : ```{', '.join(config.nsfw_possible)}```")
        try:
            embed = Embed(
                color=0x690E8
            )
            embed.set_image(url=nekos.img(image_type))
            await ctx.send(embed=embed)
        except nekos.errors.InvalidArgument:
            await ctx.send(f"Invalid type! Possible types are : ```{', '.join(config.nsfw_possible)}```")
        except nekos.errors.NothingFound:
            await ctx.send("Sorry, No Images Found.")
