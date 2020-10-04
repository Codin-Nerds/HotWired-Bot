from discord.ext import commands


class ArgumentError(commands.CommandError):
    pass


class ImageError(commands.CommandError):
    pass


class VoiceError(commands.CommandError):
    pass


class HTTPError(commands.CommandError):
    pass


class HTTPForbidden(commands.CommandError):
    pass


class HTTPNotFound(commands.CommandError):
    pass