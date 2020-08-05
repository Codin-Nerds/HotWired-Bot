from bot.core.bot import Bot

from .games import Games
from .hangman import Hangman
# from .tic_tac_toe import TicTacToe
from .trivia import Trivia


def setup(bot: Bot) -> None:
    """Load the games cogs."""
    bot.add_cog(Hangman(bot))
    bot.add_cog(Games(bot))
    # bot.add_cog(TicTacToe(bot))
    bot.add_cog(Trivia(bot))
