from random import choice

import discord
import requests
from discord.ext import commands


async def make_embed(img: str, provider: str, author: discord.User):
    em = discord.Embed(color=discord.Colour.red())
    em.title = provider + " requested by " + author.name
    em.set_image(url=img)
    return em


class NSFW(commands.Cog):
    conf = {}
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
    
    @commands.command(aliases=["yan"])
    @commands.is_nsfw()
    @commands.guild_only()
    async def yandere(self, ctx, tag: str = "yandere"):
        url = requests.get(f"https://yande.re/post.json?limit=20&tags={tag}")
        url = url.json()
        try:
            image = choice(url)
        except IndexError:
            return await ctx.send("This tag doesn't exist... We couldn't find anything.")
        image_url = image['sample_url']
        em = await make_embed(image_url, "Yandere", ctx.author)
        
        msg: discord.Message = await ctx.send(embed=em)
        await msg.add_reaction("heart")
    
    @yandere.error
    async def yandere_error(self, ctx, error):
        if isinstance(error, commands.NSFWChannelRequired):
            return


def setup(bot):
    bot.add_cog(NSFW(bot))
