from bot.config import devs

from discord import Member
from discord.ext.commands import Context, NoPrivateMessage


def is_bot_dev(ctx: Context) -> bool:
    """Check if user is a dev."""
    return ctx.author.id in devs


async def has_greater_roles(ctx: Context, member: Member) -> bool:
    """Check if member has a higher role than the bot."""
    return member.top_role >= ctx.author.top_role


def cog_check(ctx: Context) -> bool:
    """Make the bot work only in guild context."""
    if ctx.guild is None:
        raise NoPrivateMessage
    return True


def is_guild_owner(ctx: Context) -> bool:
    """Check if the user is the guild owner."""
    return ctx.guild.is_owner(ctx.author)
