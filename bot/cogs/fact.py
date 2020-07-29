import os 
import Discord 
import randfacts


@command()
    async def randomfact(self, ctx: Context) -> None:
        """Get a randaom fact"""
        randomfact = randfacts.GetFact
        await ctx.send(embed=Embed(
            title="Did you Know?",
            description=randomfact["text"],
            color=0x690E8
                               
       

