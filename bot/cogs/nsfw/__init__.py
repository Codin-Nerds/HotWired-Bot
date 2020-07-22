from bot.core.bot import Bot

from .neko import Neko
from .yandere import Yandere


def setup(bot: Bot) -> None:
    """Load the nsfw cogs."""
    bot.add_cog(Neko(bot))
    bot.add_cog(Yandere(bot))
