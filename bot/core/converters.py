import re
import typing as t
from ast import literal_eval
from contextlib import suppress

from discord import Member, NotFound, User
from discord.ext.commands import (
    BadArgument, Context, Converter,
    MemberConverter, UserConverter
)

from bot.utils.errors import MemberNotFound, UserNotFound
from dateutil.relativedelta import relativedelta


def _obtain_user_id(argument: str) -> t.Optional[int]:
    """Get user ID from mention or directly from string."""
    mention_match = re.match(r'<@!?([0-9]+)>$', argument)
    id_match = re.match(r'([0-9]{15,21})$', argument)

    if mention_match is None and id_match is None:
        return None
    if mention_match is not None:
        return int(mention_match.group(1))
    if id_match is not None:
        return int(id_match.group(1))


class ActionReason(Converter):
    """Make sure reason length is within 512 characters."""

    async def convert(self, ctx: Context, argument: str) -> str:
        """Add ID to the reason and make sure it's withing length."""
        if argument != "":
            reason = f"[ID: {ctx.author.id}]: {argument}"
            if len(reason) > 512:
                reason_max = 512 - len(reason) + len(argument)
                raise BadArgument(f"Reason is too long ({len(argument)}/{reason_max})")
        else:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        return reason


class Unicode(Converter):
    """Convert raw input into unicode formatted string."""

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


class TimeDelta(Converter):
    """Convert given duration string into relativedelta."""

    time_getter = re.compile(
        r"((?P<years>\d+?) ?(y|yr|yrs|years|year) ?)?"
        r"((?P<months>\d+?) ?(mo|mon|months|month) ?)?"
        r"((?P<weeks>\d+?) ?(w|wk|weeks|week) ?)?"
        r"((?P<days>\d+?) ?(d|days|day) ?)?"
        r"((?P<hours>\d+?) ?(h|hr|hrs|hours|hour) ?)?"
        r"((?P<minutes>\d+?) ?(m|min|mins|minutes|minute) ?)?"
        r"((?P<seconds>\d+?) ?(s|sec|secs|seconds|second))?",
        re.IGNORECASE
    )

    async def convert(self, ctx: Context, duration: str) -> relativedelta:
        """
        Convert a string `duration` to relativedelta.

        Accepted inputs for `duration` (in order):
        * years: `y`, `yr`, `yrs`, `years`, `year`
        * months: `mo`, `mon`, `months`, `month`
        * weeks: `w`, `wk`, `weeks`, `week`
        * days: `d`, `days`, `day`
        * hours: `h`, `hr`, `hrs`, `hours`, `hour`
        * minutes: `m`, `min`, `mins`, `minutes`, `minute`
        * seconds: `s`, `sec`, `secs`, `seconds` `second`
        These inputs are case insensitive.
        """
        time_delta = self.time_getter.fullmatch(duration)
        if not time_delta:
            raise BadArgument("Invalid duration.")

        duration_dict = {unit: int(amount) for unit, amount in time_delta.groupdict(default=0).items()}
        return relativedelta(**duration_dict)


class CodeBlock(Converter):
    """
    Convert given wrapped string in codeblock into a tuple of language and the wrapped string
    """

    codeblock_parser = re.compile(r"\`\`\`(.*\n)?((?:[^\`]*\n*)+)\`\`\`")
    inline_code_parser = re.compile(r"\`(.*\n*)\`")

    async def convert(self, ctx: Context, codeblock: str) -> t.Tuple[t.Optional[str], str]:
        """
        Convert a string `codeblock` into a tuple which consists of:
        * language (f.e.: `py` or `None` for no language)
        * wrapped_text (the text inside of the codeblock)

        The converter converts:
        * full codeblocks (```text```, ```py\ntext```, ```\ntext```)
        * inline codeblocks (`text`)

        In case no codeblock was found, original string is returned
        """
        codeblock_match = self.codeblock_parser.fullmatch(codeblock)
        if codeblock_match:
            lang = codeblock_match.group(1)
            code = codeblock_match.group(2)
            if not code:
                code = lang
                lang = None
            if code[-1] == "\n":
                code = code[:-1]
            return (lang, code)

        inline_match = self.inline_code_parser.fullmatch(codeblock)
        if inline_match:
            return (None, inline_match.group(1))

        return codeblock


class ProcessedUser(UserConverter):
    """
    Try to convert any accepted string into `User`
    Lookup Strategy:
    [Default UserConverter strategy]
    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name#discrim
    4. Lookup by name
    [Added functionality]
    5. Lookup by API
    """

    async def convert(self, ctx: Context, argument: str) -> User:
        # Follow general MemberConverter lookup strategy
        with suppress(BadArgument):
            return await super().convert(ctx, argument)

        # Try to look user up using API
        ID = _obtain_user_id(argument)
        if ID is None:
            raise UserNotFound(f"No user found from `{argument}`")
        try:
            return await ctx.bot.fetch_user(ID)
        except NotFound:
            raise UserNotFound(f"No user with ID: {ID} found")


class ProcessedMember(MemberConverter):
    """
    Try to convert any accepted string into `Member`
    Lookup Strategy:
    [Default MemberConverter strategy]
    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name#discrim
    4. Lookup by name
    5. Lookup by nickname
    [Added functionality]
    6. Lookup by API
    """

    async def convert(self, ctx: Context, argument: str) -> Member:
        # Follow general MemberConverter lookup strategy
        with suppress(BadArgument):
            return await super().convert(ctx, argument)

        # Try to look user up using API
        ID = _obtain_user_id(argument)
        if ID is None:
            raise MemberNotFound(f"No member found on guild {ctx.guild.id} from `{argument}`")
        try:
            return await ctx.guild.fetch_member(ID)
        except NotFound:
            raise MemberNotFound(f"No member with ID: {ID} found on guild {ctx.guild.id}")
