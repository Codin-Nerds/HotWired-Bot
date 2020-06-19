from discord import Member
from discord.ext.commands import Context, NoPrivateMessage
from constants import owner_ids


def owner(ctx: Context) -> bool:
    if ctx.author.id not in owner_ids:
        return False
    return True


async def has_greater_roles(ctx: Context, member: Member) -> bool:
    if member.top_role >= ctx.author.top_role:
        return True
    else:
        return False


def cog_check(ctx: Context) -> bool:
    if ctx.guild is None:
        raise NoPrivateMessage
    return True


def is_owner(ctx: Context) -> bool:
    return ctx.guild.is_owner(ctx.author)
