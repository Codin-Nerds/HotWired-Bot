import discord
from discord.ext import commands, tasks 

class Stuff(commands.Cog):
    def __init__(self, client):
        self.client = client


       
    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog Stuff is working.')
    
    
    @commands.command()
    async def test(self, ctx):
        await ctx.send('test')

    @commands.command()
    async def clear(self, ctx, amount = 2):
        await ctx.channel.purge(limit = amount)

    @commands.command()
    async def credits(self, ctx):
        await ctx.send('`Created by Thecoder3281f#6650 under the guidance of Lucas#6947\'s videos`')

    @commands.command()
    async def invite_me(self, ctx):
        await ctx.send('Use this link to invite me to your server: https://discord.com/api/oauth2/authorize?client_id=707412967708426251&permissions=8&scope=bot')

    @commands.command()
    async def suggestion(self, ctx,*, text):
        await ctx.send('Suggestion is pending.')
        suggestions = open(r"Suggestions.txt", "a")
        suggestions.write('\n')
        suggestions.write(text)
        suggestions.close()




def setup(client):
    client.add_cog(Stuff(client))

