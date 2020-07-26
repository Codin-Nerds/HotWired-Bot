from bot.core.bot import Bot

from .coding import Coding


def setup(bot: Bot) -> None:
    """Load the games cog."""
    bot.add_cog(Coding(bot))
