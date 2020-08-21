from bot.core.bot import Bot

from .comics import Comics
from .games import Games
from .fun import Fun
from .trivia import Trivia


def setup(bot: Bot) -> None:
    """Load the Games cogs."""
    bot.add_cog(Games(bot))
    bot.add_cog(Fun(bot))
    bot.add_cog(Comics(bot))
    bot.add_cog(Trivia(bot))
