from bot.core.bot import Bot

from .games import Games
from .hangman import Hangman
from .fun import Fun
from .comics import Comics


def setup(bot: Bot) -> None:
    """Load the games cogs."""
    bot.add_cog(Hangman(bot))
    bot.add_cog(Games(bot))
    bot.add_cog(Fun(bot))
    bot.add_cog(Comics(bot))
