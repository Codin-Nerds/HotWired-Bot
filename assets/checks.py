from discord import Member
from discord.ext.commands import Context, NoPrivateMessage
from cogs.utils.constants import devs


def is_bot_dev(ctx: Context) -> bool:
    return ctx.author.id in devs


async def has_greater_roles(ctx: Context, member: Member) -> bool:
    return member.top_role >= ctx.author.top_role


def cog_check(ctx: Context) -> bool:
    if ctx.guild is None:
        raise NoPrivateMessage
    return True


def is_guild_owner(ctx: Context) -> bool:
    return ctx.guild.is_owner(ctx.author)
