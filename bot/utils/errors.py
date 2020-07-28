from discord import NotFound
from discord.ext import commands


class ServiceError(commands.CommandInvokeError):
    """Raised whenever a request to a service and returns a failure of some sort."""

    pass


class NSFWException(commands.CheckFailure):
    """Raised whenever a NSFW command is not executed in a NSFW channel."""

    pass


class MemberNotFound(NotFound):
    """Raised when search for Member has failed and no member was found."""

    pass


class UserNotFound(NotFound):
    """Raised when search for User has failed and no user was found."""

    pass
