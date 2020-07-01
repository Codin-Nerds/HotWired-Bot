from discord.ext.commands import Bot

from .hangman import Hangman
from .games import Games


def setup(bot: Bot) -> None:
    """Load the games cogs."""
    bot.add_cog(Hangman(bot))
    bot.add_cog(Games(bot))
