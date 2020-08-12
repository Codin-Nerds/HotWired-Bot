from random import choice

import aiohttp
from discord import Color, Embed
from discord.ext.commands import Bot, Cog, Context, is_nsfw, command


class Yandere(Cog):
    """Yande.re cog."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @command(aliases=["yan"])
    @is_nsfw()
    async def yandere(self, ctx: Context, tag: str = "yandere") -> None:
        """Search Yande.re for NSFW pics."""
        async with self.session.get(f"https://yande.re/post.json?limit=20&tags={tag}") as response:
            url = await response.json()

        try:
            image = choice(url)
        except IndexError:
            return await ctx.send("This tag doesn't exist... We couldn't find anything.")

        image_url = image['sample_url']

        embed = Embed(color=Color.blue())
        embed.title = f"Requested by {ctx.author.name}"
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)
