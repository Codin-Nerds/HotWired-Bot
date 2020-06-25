from discord import Member
from discord.ext.commands import Context, NoPrivateMessage
from cogs.utils.constants import owner_ids


def owner(ctx: Context) -> bool:
    return ctx.author.id in owner_ids


async def has_greater_roles(ctx: Context, member: Member) -> bool:
    return member.top_role >= ctx.author.top_role


def cog_check(ctx: Context) -> bool:
    if ctx.guild is None:
        raise NoPrivateMessage
    return True


def is_owner(ctx: Context) -> bool:
    return ctx.guild.is_owner(ctx.author)
