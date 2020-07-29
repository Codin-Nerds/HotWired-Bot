import os 
import Discord 
import randfacts

from discord.ext.commands import Cog, Context, command

from bot import config
from bot.core.bot import Bot

class Facts(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        
        @command()
    async def randomfact(self, ctx: Context) -> None:
        """Get a randaom fact"""
        randomfact = randfacts.GetFact
        await ctx.send(embed=Embed(
            title="Did You Know?",
            description=randomfact["text"],
            color=0x690E8
            
def setup(bot: Bot) -> None:
    bot.add_cog(Facts(bot))




       

