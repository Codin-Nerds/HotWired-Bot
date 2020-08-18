from bot.core.bot import Bot

from .comics import Comics
from .games import Games
from .hangman import Hangman
from .fun import Fun
from .tic_tac_toe import TicTacToe
from .trivia import Trivia


def setup(bot: Bot) -> None:
    """Load the Games cogs."""
    bot.add_cog(Hangman(bot))
    bot.add_cog(Games(bot))
    bot.add_cog(TicTacToe(Bot))
    bot.add_cog(Fun(bot))
    bot.add_cog(Comics(bot))
    bot.add_cog(Trivia(bot))
