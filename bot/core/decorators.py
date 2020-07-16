import textwrap
import typing as t
from functools import wraps

from discord import Embed, Member, User, Color
from discord.ext.commands import Cog, Context

from bot.core.converters import ProcessedMember
from bot.utils.errors import MemberNotFound
from loguru import logger


def follow_roles(argument: t.Union[str, int] = 0) -> t.Callable:
    """
    Make sure user can target someone accordingly to role hierarchy.

    `argument_number` states which argument corresponds to the selected user.
    it should point to `Member` or `User` on guild
    """

    def wrap(func: t.Callable) -> t.Callable:
        @wraps(func)
        async def inner(self: Cog, ctx: Context, *args, **kwargs) -> None:
            try:
                user = kwargs[argument]
            except KeyError:
                try:
                    user = args[argument]
                except (IndexError, TypeError):
                    raise ValueError(f"Specified argument '{argument}' not found.")

            if isinstance(user, User):
                try:
                    member = await ProcessedMember.get_member(ctx.guild, user)
                except MemberNotFound:
                    # Skip checks in case of bad member
                    logger.trace("Skipping follow_role check, provided user isn't a valid Member.")
                    await func(self, ctx, *args, **kwargs)
                    return
            elif isinstance(user, Member):
                member = user
            else:
                raise ValueError("Specified argument is not `Member` or `User`")

            actor = ctx.author
            # Run the function in case actor has higher role then member, or is a guild owner
            if actor == ctx.guild.owner or member.top_role <= actor.top_role:
                logger.trace(f"User <@{member.id}> on {member.guild.id} has passed follow_role check.")
                await func(self, ctx, *args, **kwargs)
            else:
                logger.trace(f"User <@{member}> on {member.guild.id} has failed follow_role check.")
                embed = Embed(
                    title="You can't target this user",
                    description=textwrap.dedent(
                        f"""
                        {member.mention} has higher top role that yours.

                        **❯❯ You can only target users with lower top role.**
                        """
                    ),
                    color=Color.red(),
                )
                await ctx.send(f"Sorry, {actor.mention}", embed=embed)

        return inner

    return wrap
