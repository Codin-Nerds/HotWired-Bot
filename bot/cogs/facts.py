import os 
from discord import Embed, Color
import randfacts

from discord.ext.commands import Cog, Context, command

from bot import config
from bot.core.bot import Bot

class Facts(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        
    @command()
    async def randomfact(self, ctx: Context) -> None:
        """Get A Random fact"""
        randomfact = randfacts.GetFact
        await ctx.send(embed=Embed(
            title="Did You Know?",
            description=randomfact["text"],
            color=Color.blurple()
        ))
            
def setup(bot: Bot) -> None:
    bot.add_cog(Facts(bot))




       
