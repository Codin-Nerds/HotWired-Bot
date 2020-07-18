import typing as t

from bot.config import devs

from discord import Color, Embed, Member
from discord.ext.commands import Context, NoPrivateMessage


def is_bot_dev(ctx: Context) -> bool:
    return ctx.author.id in devs


async def is_sudo(ctx: Context) -> t.Union[bool, None]:
    if ctx.author.id in devs:
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


def is_guild_owner(ctx: Context) -> bool:
    return ctx.guild.is_owner(ctx.author)
