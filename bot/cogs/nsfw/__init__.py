from bot.core.bot import Bot

from .nekos import Neko
from .nsfw import Nsfw


def setup(bot: Bot) -> None:
    """Load the nsfw cogs."""
    bot.add_cog(Neko(bot))
    bot.add_cog(Nsfw(bot))
