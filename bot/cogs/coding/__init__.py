from bot.core.bot import Bot

from .coding import Coding


def setup(bot: Bot) -> None:
    """Load the Games cog."""
    bot.add_cog(Coding(bot))
