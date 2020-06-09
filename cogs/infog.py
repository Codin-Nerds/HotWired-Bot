import discord
from discord.ext import commands


class Infog(commands.Cog):

  def __init__(self, client):
    self.client = client

  @commands.command()
  async def infog(self, ctx):
    await ctx.send("Info gathered")

def setup(client):
  client.add_cog(Infog(client))
