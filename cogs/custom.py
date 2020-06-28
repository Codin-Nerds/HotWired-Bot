import discord
from discord.ext import commands


class Custom(commands.Cog):
    """Create your own commands !"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def create(self, ctx, name: str, *, effect: str) -> None:
        """Create a custom command"""
        if " " in name:
            return await ctx.send("Well tried, but custom command names can't include spaces")

        if name in self.bot.all_commands:
            return await ctx.send("Sorry, but a bot command already exists with this name")
