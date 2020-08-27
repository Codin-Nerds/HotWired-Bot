from __future__ import annotations

import re
from typing import Callable, ClassVar, List, Optional, Pattern, Sequence, Tuple, Union, cast

import discord

from discord.ext import commands

_ID_RE = re.compile(r"([0-9]{15,21})$")
_USER_MENTION_RE = re.compile(r"<@!?([0-9]{15,21})>$")
_CHAN_MENTION_RE = re.compile(r"<#([0-9]{15,21})>$")
_ROLE_MENTION_RE = re.compile(r"<@&([0-9]{15,21})>$")


class MessagePredicate(Callable[[discord.Message], bool]):

    def __init__(self, predicate: Callable[["MessagePredicate", discord.Message], bool]) -> None:
        self._pred: Callable[["MessagePredicate", discord.Message], bool] = predicate
        self.result = None

    def __call__(self, message: discord.Message) -> bool:
        return self._pred(self, message)

    @classmethod
    def same_context(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        if ctx is not None:
            channel = channel or ctx.channel
            user = user or ctx.author

        return cls(
            lambda self, m: (user is None or user.id == m.author.id)
            and (channel is None or channel.id == m.channel.id)
        )

    @classmethod
    def cancelled(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        return cls(
            lambda self, m: (same_context(m) and m.content.lower() == f"{ctx.prefix}cancel")
        )

    @classmethod
    def yes_or_no(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            content = m.content.lower()
            if content in ("yes", "y"):
                self.result = True
            elif content in ("no", "n"):
                self.result = False
            else:
                return False
            return True

        return cls(predicate)

    @classmethod
    def valid_int(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            try:
                self.result = int(m.content)
            except ValueError:
                return False
            else:
                return True

        return cls(predicate)

    @classmethod
    def valid_float(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            try:
                self.result = float(m.content)
            except ValueError:
                return False
            else:
                return True

        return cls(predicate)

    @classmethod
    def positive(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            try:
                number = float(m.content)
            except ValueError:
                return False
            else:
                if number > 0:
                    self.result = number
                    return True
                else:
                    return False

        return cls(predicate)

    @classmethod
    def valid_role(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        guild = cls._get_guild(ctx, channel, cast(discord.Member, user))

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False

            role = self._find_role(guild, m.content)
            if role is None:
                return False

            self.result = role
            return True

        return cls(predicate)

    @classmethod
    def valid_member(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        guild = cls._get_guild(ctx, channel, cast(discord.Member, user))

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False

            match = _ID_RE.match(m.content) or _USER_MENTION_RE.match(m.content)
            if match:
                result = guild.get_member(int(match.group(1)))
            else:
                result = guild.get_member_named(m.content)

            if result is None:
                return False
            self.result = result
            return True

        return cls(predicate)

    @classmethod
    def valid_text_channel(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        guild = cls._get_guild(ctx, channel, cast(discord.Member, user))

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False

            match = _ID_RE.match(m.content) or _CHAN_MENTION_RE.match(m.content)
            if match:
                result = guild.get_channel(int(match.group(1)))
            else:
                result = discord.utils.get(guild.text_channels, name=m.content)

            if not isinstance(result, discord.TextChannel):
                return False
            self.result = result
            return True

        return cls(predicate)

    @classmethod
    def has_role(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        guild = cls._get_guild(ctx, channel, cast(discord.Member, user))
        if user is None:
            if ctx is None:
                raise TypeError(
                    "One of `user` or `ctx` must be supplied to `MessagePredicate.has_role`."
                )
            user = ctx.author

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False

            role = self._find_role(guild, m.content)
            if role is None or role not in user.roles:
                return False

            self.result = role
            return True

        return cls(predicate)

    @classmethod
    def equal_to(
        cls,
        value: str,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        return cls(lambda self, m: same_context(m) and m.content == value)

    @classmethod
    def lower_equal_to(
        cls,
        value: str,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        return cls(lambda self, m: same_context(m) and m.content.lower() == value)

    @classmethod
    def less(
        cls,
        value: Union[int, float],
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        valid_int = cls.valid_int(ctx, channel, user)
        valid_float = cls.valid_float(ctx, channel, user)
        return cls(lambda self, m: (valid_int(m) or valid_float(m)) and float(m.content) < value)

    @classmethod
    def greater(
        cls,
        value: Union[int, float],
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        valid_int = cls.valid_int(ctx, channel, user)
        valid_float = cls.valid_float(ctx, channel, user)
        return cls(lambda self, m: (valid_int(m) or valid_float(m)) and float(m.content) > value)

    @classmethod
    def length_less(
        cls,
        length: int,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        return cls(lambda self, m: same_context(m) and len(m.content) <= length)

    @classmethod
    def length_greater(
        cls,
        length: int,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)
        return cls(lambda self, m: same_context(m) and len(m.content) >= length)

    @classmethod
    def contained_in(
        cls,
        collection: Sequence[str],
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            try:
                self.result = collection.index(m.content)
            except ValueError:
                return False
            else:
                return True

        return cls(predicate)

    @classmethod
    def lower_contained_in(
        cls,
        collection: Sequence[str],
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            try:
                self.result = collection.index(m.content.lower())
            except ValueError:
                return False
            else:
                return True

        return cls(predicate)

    @classmethod
    def regex(
        cls,
        pattern: Union[Pattern[str], str],
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.TextChannel] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        same_context = cls.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False

            if isinstance(pattern, str):
                pattern_obj = re.compile(pattern)
            else:
                pattern_obj = pattern

            match = pattern_obj.search(m.content)
            if match:
                self.result = match
                return True
            return False

        return cls(predicate)

    @staticmethod
    def _find_role(guild: discord.Guild, argument: str) -> Optional[discord.Role]:
        match = _ID_RE.match(argument) or _ROLE_MENTION_RE.match(argument)
        if match:
            result = guild.get_role(int(match.group(1)))
        else:
            result = discord.utils.get(guild.roles, name=argument)
        return result

    @staticmethod
    def _get_guild(
        ctx: commands.Context, channel: discord.TextChannel, user: discord.Member
    ) -> discord.Guild:
        if ctx is not None:
            return ctx.guild
        elif channel is not None:
            return channel.guild
        elif user is not None:
            return user.guild


class ReactionPredicate(Callable[[discord.Reaction, discord.abc.User], bool]):

    YES_OR_NO_EMOJIS: ClassVar[Tuple[str, str]] = (
        "\N{WHITE HEAVY CHECK MARK}",
        "\N{NEGATIVE SQUARED CROSS MARK}",
    )
    """Tuple[str, str] : A tuple containing the tick emoji and cross emoji, in that order."""

    ALPHABET_EMOJIS: ClassVar[List[str]] = [
        chr(code)
        for code in range(
            ord("\N{REGIONAL INDICATOR SYMBOL LETTER A}"),
            ord("\N{REGIONAL INDICATOR SYMBOL LETTER Z}") + 1,
        )
    ]
    """List[str] : A list of all 26 alphabetical letter emojis."""

    NUMBER_EMOJIS: ClassVar[List[str]] = [
        chr(code) + "\N{COMBINING ENCLOSING KEYCAP}" for code in range(ord("0"), ord("9") + 1)
    ]
    """List[str] : A list of all single-digit number emojis, 0 through 9."""

    def __init__(
        self, predicate: Callable[["ReactionPredicate", discord.Reaction, discord.abc.User], bool]
    ) -> None:
        self._pred: Callable[
            ["ReactionPredicate", discord.Reaction, discord.abc.User], bool
        ] = predicate
        self.result = None

    def __call__(self, reaction: discord.Reaction, user: discord.abc.User) -> bool:
        return self._pred(self, reaction, user)

    # noinspection PyUnusedLocal
    @classmethod
    def same_context(
        cls, message: Optional[discord.Message] = None, user: Optional[discord.abc.User] = None
    ) -> "ReactionPredicate":
        # noinspection PyProtectedMember
        me_id = message._state.self_id
        return cls(
            lambda self, r, u: u.id != me_id
            and (message is None or r.message.id == message.id)
            and (user is None or u.id == user.id)
        )

    @classmethod
    def with_emojis(
        cls,
        emojis: Sequence[Union[str, discord.Emoji, discord.PartialEmoji]],
        message: Optional[discord.Message] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "ReactionPredicate":
        same_context = cls.same_context(message, user)

        def predicate(self: ReactionPredicate, r: discord.Reaction, u: discord.abc.User):
            if not same_context(r, u):
                return False

            try:
                self.result = emojis.index(r.emoji)
            except ValueError:
                return False
            else:
                return True

        return cls(predicate)

    @classmethod
    def yes_or_no(
        cls, message: Optional[discord.Message] = None, user: Optional[discord.abc.User] = None
    ) -> "ReactionPredicate":
        same_context = cls.same_context(message, user)

        def predicate(self: ReactionPredicate, r: discord.Reaction, u: discord.abc.User) -> bool:
            if not same_context(r, u):
                return False

            try:
                self.result = not bool(self.YES_OR_NO_EMOJIS.index(r.emoji))
            except ValueError:
                return False
            else:
                return True

        return cls(predicate)
