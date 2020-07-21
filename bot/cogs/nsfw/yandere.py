#  Copyright (c) 2019.
#  MIT License
#
#  Copyright (c) 2019 YumeNetwork
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

# Source : https://github.com/Jintaku/Jintaku-Cogs-V3/


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
