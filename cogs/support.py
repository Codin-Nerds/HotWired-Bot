import discord
from discord.ext import commands

class Support(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command()
    async def invite(self, ctx):
      """
      Invite link for Bot
      """
      await ctx.send('Invite Me to Your server ! **THE INVITE LINK IS** : https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=980675863&scope=bot')
      
    @commands.command(name='support')
    async def support(self, ctx):
        """
        Get an invite link to the bots support server.
        """

        await ctx.send(f'If you have any problems with the bot or if you have any suggestions/feedback be sure to join the support server using this link : https://discord.gg/CgH6Sj6')
        
def setup(client):
    client.add_cog(Support(client))

