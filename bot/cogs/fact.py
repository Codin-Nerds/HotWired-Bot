import os 
import Discord 
import randfacts

@command
    async def randomfact(self, ctx: Context) -> None:
        """Get a randaom fact"""
        fact = randfacts.GetFact
        await ctx.channel.send(fact]
