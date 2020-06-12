from discord.ext import commands


class SafesearchFail(commands.CommandError):
    """Thrown when a query contains NSFW content."""
    pass


def setup(bot):
    pass
