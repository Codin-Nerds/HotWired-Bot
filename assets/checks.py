from discord import Member, Embed, Color
from discord.ext.commands import Context, NoPrivateMessage
from cogs.utils.constants import owner_ids

import typing as t
from cogs.utils import constants


def owner(ctx: Context) -> bool:
    return ctx.author.id in owner_ids


async def is_sudo(ctx: Context) -> t.Union[bool, None]:
    if ctx.author.id in constants.devs:
        return True
    else:
        embed = Embed(description="Make your Own sandwich Mortal!.", color=Color.red())
        await ctx.send(embed=embed)


async def has_greater_roles(ctx: Context, member: Member) -> bool:
    return member.top_role >= ctx.author.top_role


def cog_check(ctx: Context) -> bool:
    if ctx.guild is None:
        raise NoPrivateMessage
    return True


def is_owner(ctx: Context) -> bool:
    return ctx.guild.is_owner(ctx.author)
