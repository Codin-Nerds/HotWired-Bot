import random

import discord
from cogs.utils.embedHandler import error_embed, info
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def slap(self, ctx, member: discord.Member):
      """
      Slap a User
      """
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
      """
      Punch a User
      """
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
      """
      Shoot a User
      """
      embed = info(f"{member.mention} shot by {ctx.author.mention}  :gun: :boom:", ctx.me, "Boom! Bam! He's Dead!")
      embed.set_image(url="https://media.giphy.com/media/xT9IguC6bxYHsGIRb2/giphy.gif")
      await ctx.send(embed=embed)

    @commands.command(aliases=["table", "flip"])
    async def throw(self, ctx):
      """
      Throw the table
      """
      embed = info(f"{ctx.author.mention} :boom:", ctx.me, "Table Throw!")
      embed.set_image(url="https://media.giphy.com/media/pzFB1KY4wob0jpbuPa/giphy.gif")
      await ctx.send(embed=embed)

    @commands.command(aliases=['cookies', 'cook'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def cookie(self, ctx, member: discord.Member = None):
      """
      Give a User a cookie
      """
      if member == None:
        member = ctx.author

      num = random.randint(1, 4)

      if num == 1:
        if ctx.author == member:
          embed = info(f"You're a Lucky Guy! {member.mention} You got a **Huge Cookie**!\n**You got +10 points!**", ctx.me, "Cookie Giver!")
          img_url = "https://media.giphy.com/media/7GYHmjk6vlqY8/giphy.gif"
          embed.set_image(url=img_url)
          await ctx.send(embed=embed)
        else :
          embed = info(f"{member.mention} is a Lucky Guy! You got a **Huge Cookie**! from {ctx.author.mention}\n**You got +10 points!**", ctx.me, "Cookie Giver!")
          img_url = "https://media.giphy.com/media/7GYHmjk6vlqY8/giphy.gif"
          embed.set_image(url=img_url)
          await ctx.send(embed=embed)
      else:
        if ctx.author == member:
          embed = info(f"You got a Cookie! {member.mention} ➡ :cookie: :cookie: :cookie: \n**You got +{num} points!**", ctx.me, "Cookie Giver!")
          await ctx.send(embed=embed)
        else :
          embed = info(f"{member.mention} got a cookie from {ctx.author.mention}➡ :cookie: :cookie: :cookie: \n**You got +{num} points!**", ctx.me, "Cookie Giver!")
          await ctx.send(embed=embed)

    @cookie.error
    async def cookie_error(self, ctx, error):
      if isinstance(error, commands.BadArgument):
        embed = error_embed("You Can get a Cookie Every **2 Hours Once**", "❌ERROR")
        await ctx.send(embed=embed)
# kiss, hug, pat => commands to be added
# cuddle hug insult kiss lick nom pat poke slap stare highfive bite greet punch handholding tickle kill hold pats wave boop

def setup(bot):
    bot.add_cog(Fun(bot))
