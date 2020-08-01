import typing as t
from ast import literal_eval
from contextlib import suppress

from discord import Guild, Member, NotFound, User
from discord.ext.commands import BadArgument, Context, Converter, UserConverter

from bot.utils.errors import MemberNotFound


class ActionReason(Converter):
    """Make sure reason length is within 512 characters."""

    async def convert(self, ctx: Context, argument: str) -> str:
        """Add ID to the reason and make sure it's withing length."""
        reason = f"[ID: {ctx.author.id}]: {argument}"
        if len(reason) > 512:
            reason_max = 512 - len(reason) + len(argument)
            raise BadArgument(f"Reason is too long ({len(argument)}/{reason_max})")
        return argument


class Unicode(Converter):
    """Convert raw input into unicode formatted string"""

    def process_unicode(self, message: str) -> str:
        """
        This accepts any string with raw unicode and converts it into proper unicode.

        It uses literal eval to process the string safely and turn it into proper unicode.
        """

        # Only process individual lines to avoid EOL in expression
        lines = message.split("\n")
        for index, line in enumerate(lines):
            try:
                # Replace ''' which would exit the string
                # even though it won't be allowed by literal_eval, it is still better
                # to replace it as it will properly evaluate even strings with that.
                line = line.replace("'''", "`<ESCAPE STRING>`")
                line = literal_eval(f"'''{line}'''")
                line = line.replace("`<ESCAPE STRING>`", "'''")
                lines[index] = line
            except SyntaxError as e:
                print(line)
                print(f"String deemed unsafe -> {e}")

        return "\n".join(lines)

    def outside_delimeter(self, string: str, delimeter: str, operation: t.Callable) -> str:
        """Apply given operation to text outside of delimeted section"""
        splitted = string.split(delimeter)
        for index, string_part in enumerate(splitted):
            # Not inside of a delimeted section
            if index % 2 == 0:
                splitted[index] = operation(string_part)

        return delimeter.join(splitted)

    async def convert(self, ctx: Context, message: str) -> str:
        # don't replace unicode characters within code blocks
        operation = lambda x: self.outside_delimeter(x, "`", self.process_unicode)
        return self.outside_delimeter(message, "```", operation)


class ProcessedUser(UserConverter):
    """
    Try to convert any accepted string into `Member` or `User`.

    When possible try to convert user into `Member` but if not, use `User` instead.
    """

    async def get_member(guild: Guild, user: User) -> Member:
        member = guild.get_member(user.id)
        if not member:
            try:
                member = await guild.fetch_member(user.id)
            except NotFound:
                raise MemberNotFound(f"No member with ID: {user.id} on guild {guild.id}")
        return member

    async def convert(self, ctx: Context, argument: str) -> Member:
        """Convert the `argument` into `Member` or `User`."""
        with suppress(BadArgument):
            # Try to use UserConverter first
            user = await super().convert(ctx, argument)
            try:
                return await self.get_member(ctx.guild, user)
            except MemberNotFound:
                return user

        # If UserConverter failed, try to fetch user as ID
        try:
            user = await ctx.bot.fetch_user(int(argument))
            try:
                return await self.get_member(ctx.guild, user)
            except MemberNotFound:
                return user
        except ValueError:
            raise BadArgument(f"{argument} is not a valid user or user ID")


ProcessedMember = t.Union[Member, ProcessedUser]
