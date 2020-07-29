import os 
import Discord 
import randfacts

@command(aliases=["fact"])
    async def serverinfo(self, ctx: Context) -> None:
        """Get a randaom fact"""
        await ctx.channel.send(randfacts.GetFact)
