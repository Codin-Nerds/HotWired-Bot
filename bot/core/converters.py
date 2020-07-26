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
    """Convert raw input into unicode formatted string."""

    @staticmethod
    def process_unicode(message: str) -> str:
        """
        Accept any string with raw unicode and convert it into proper unicode.

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
            except SyntaxError as error:
                print(line)
                print(f"String deemed unsafe -> {error}")

        return "\n".join(lines)

    @staticmethod
    def outside_delimeter(string: str, delimeter: str, operation: t.Callable) -> str:
        """Apply given operation to text outside of delimeted section."""
        splitted = string.split(delimeter)
        for index, string_part in enumerate(splitted):
            # Not inside of a delimeted section
            if index % 2 == 0:
                splitted[index] = operation(string_part)

        return delimeter.join(splitted)

    async def convert(self, ctx: Context, argument: str) -> str:
        """Do the conversion."""
        # don't replace unicode characters within code blocks
        return self.outside_delimeter(
            argument,
            "```",
            lambda x: self.outside_delimeter(x, "`", self.process_unicode),
        )


class ProcessedUser(UserConverter):
    """
    Try to convert any accepted string into `Member` or `User`.

    When possible try to convert user into `Member` but if not, use `User` instead.
    """

    @staticmethod
    async def get_member(guild: Guild, user: User) -> Member:
        """Get a member from a guild."""
        try:
            return guild.get_member(user.id) or await guild.fetch_member(user.id)
        except NotFound:
            raise MemberNotFound(f"No member with ID: {user.id} on guild {guild.id}")

    async def convert(self, ctx: Context, argument: str) -> Member:
        """Convert the `argument` into `Member` or `User`."""
        # Try to use UserConverter first
        user = await super().convert(ctx, argument)
        try:
            return await self.get_member(ctx.guild, user)
        except MemberNotFound:
            return user


ProcessedMember = t.Union[Member, ProcessedUser]
