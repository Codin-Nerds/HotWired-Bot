import os 
import Discord 
import randfacts

class Facts(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    # TODO: Remove this when error handler will be implemented
    async def send_error(self, ctx: Context, error: str) -> None:
        """Sends the Error of Any functions as an Embed."""
        help_message = f"Type `{config.COMMAND_PREFIX}help` for further assistance"
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name=f"Error: {error}", value=help_message)
        await ctx.send(embed=embed)


@command()
    async def randomfact(self, ctx: Context) -> None:
        """Get a randaom fact"""
        randomfact = randfacts.GetFact
        await ctx.send(embed=Embed(
            title="Did you Know?",
            description=randomfact["text"],
            color=0x690E8
                               
       

