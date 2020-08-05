import requests

from random import choice

from discord import Color, Embed
from discord.ext.commands import Bot, Cog, Context, is_nsfw, command


class Yandere(Cog):
    conf = {}

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(aliases=["yan"])
    @is_nsfw()
    async def yandere(self, ctx: Context, tag: str = "yandere") -> None:
        """Searches Yande.re for NSFW pics."""
        url = requests.get(f"https://yande.re/post.json?limit=20&tags={tag}")
        url = url.json()

        try:
            image = choice(url)
        except IndexError:
            return await ctx.send("This tag doesn't exist... We couldn't find anything.")

        image_url = image['sample_url']

        embed = Embed(color=Color.blue())
        embed.title = f"Requested by {ctx.author.name}"
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)
