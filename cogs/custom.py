import discord
from discord.ext import commands

from cogs.utils.embedHandler import info, error_embed

import time
from utils.covidscrape import get_covid_data

import datetime

class Custom(commands.Cog):
  
  def __init__(self, client):
    self.client = client

  # Commands
  @commands.command()
  async def hello(self, ctx):
    await ctx.send(f'Hey there Buddy!')
  
  @commands.command()
  @commands.has_permissions(manage_messages=True)
  async def ping(self, ctx):
    """Shows bot ping."""
    start = time.perf_counter()
    message = await ctx.send(embed=info("Pong!", ctx.me))
    end = time.perf_counter()
    duration = (end - start) * 1000
    await message.edit(embed=info(f":ping_pong: {duration:.2f}ms", ctx.me, "Pong!"))
    
  @commands.command(name='support')
  async def support(self, ctx):
    """
    Get an invite link to the bots support server.
    """

    await ctx.send(f'If you have any problems with the bot or if you have any suggestions/feedback be sure to join the support server using this link : https://discord.gg/CgH6Sj6')


  @commands.command(aliases=['asking'])
  async def howtoask(self, ctx):
    """
    How to ask a Question
    """
    embed = info(f"**1 ❯** Pick the appropriate channel\n**2 ❯** Post your question mentioning all the details\n**3 ❯** Ping the appropriate helper role or someone for your question\n**4 ❯** Patiently wait for a helper to respond", ctx.me, "How To Ask a Question?")
    img_url = "https://media.giphy.com/media/3ojqPGJAHWqC1VQPDk/giphy.gif"
    embed.set_image(url=img_url)
    await ctx.send('**A S K I N G   A   Q U E S T I O N ❓**')
    await ctx.send(embed=embed)

  @commands.command(aliases=['thank', 'ty'])
  async def thanks(self, ctx, member : discord.Member, *, reason = None):
    """
    Thank a User
    """
    if ctx.author == member:
      embed = error_embed(f"{ctx.author.mention} **You Cannot Thank Yourself!**", "WARNING!")
      await ctx.send(embed=embed)
    else:
      if reason != None:
        embed = info(f"{member.mention} was Thanked By {ctx.author.mention} \n**MESSAGE** : {reason}", ctx.me, "THANKS")
        img_url = "https://media.giphy.com/media/6tHy8UAbv3zgs/giphy.gif"
        embed.set_image(url=img_url)
      else :
        embed = info(f"{member.mention} was Thanked By {ctx.author.mention} !", ctx.me, "THANKS")
        img_url = "https://media.giphy.com/media/osjgQPWRx3cac/giphy.gif"
        embed.set_image(url=img_url)
      await ctx.send(embed=embed)

  @commands.command()
  async def covid(self, ctx, *, country=None):
    """
    Get the Covid19 Data
    """
    if country == None:
      await ctx.send(f"**GLOBAL DATA**")
      await ctx.send(f"New Confirmed : {get_covid_data()['NewConfirmed']}")
      await ctx.send(f"Total Confirmed : {get_covid_data()['TotalConfirmed']}")
      await ctx.send(f"New Deaths : {get_covid_data()['NewDeaths']}")
      await ctx.send(f"Total Deaths : {get_covid_data()['TotalDeaths']}")
      await ctx.send(f"New Recovered : {get_covid_data()['NewRecovered']}")
      await ctx.send(f"Total Recovered : {get_covid_data()['TotalRecovered']}")
    
    else:
      data = get_covid_data(country)
      if data == False:
        await ctx.send('**Invalid Country**')
      else:
        await ctx.send(f"**Country : {data['Country']}**")
        await ctx.send(f"New Confirmed : {data['NewConfirmed']}")
        await ctx.send(f"Total Confirmed : {data['TotalConfirmed']}")
        await ctx.send(f"New Deaths : {data['NewDeaths']}")
        await ctx.send(f"Total Deaths : {data['TotalDeaths']}")
        await ctx.send(f"New Recovered : {data['NewRecovered']}")
        await ctx.send(f"Total Recovered : {data['TotalRecovered']}")

def setup(client):
  client.add_cog(Custom(client))
