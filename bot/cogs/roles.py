from discord import Role
from discord.ext.commands import Cog, Context, command, Greedy

from bot.core.bot import Bot


class Roles(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @command()
    async def autorole(self, ctx: Context, roles: Greedy[Role] = None) -> None:
        pass


def setup(bot: Bot) -> None:
    bot.add_cog(Roles(bot))
