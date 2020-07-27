from bot.core.bot import Bot

from .games import Games
from .hangman import Hangman


def setup(bot: Bot) -> None:
    """Load the Games cogs."""
    bot.add_cog(Hangman(bot))
    bot.add_cog(Games(bot))
