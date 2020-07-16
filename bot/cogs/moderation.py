from bot.core.bot import Bot
from discord.ext.commands import Cog


class Moderation(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot


def setup(bot: Bot) -> None:
    bot.add_cog(Moderation(bot))
