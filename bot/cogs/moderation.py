import typing as t

from discord.ext.commands import (Cog, Context, NoPrivateMessage,
                                  RoleConverter, command, has_permissions)

from bot.core.bot import Bot
from bot.core.converters import Duration, ProcessedMember, ProcessedUser
from bot.core.decorators import follow_roles


class Moderation(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    # region: Commands

    @command()
    @follow_roles("member")
    @has_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: ProcessedMember, *, reason: str = "No specific reason.") -> None:
        """Kick user from the server for given reason."""
        await self._apply_kick()

    @command()
    @follow_roles("user")
    @has_permissions(administrator=True)
    async def ban(self, ctx: Context, user: ProcessedUser, *, reason: str = "No specific reason,") -> None:
        """"Permanently ban user from the server for given reason."""
        await self._apply_ban()

    @command()
    @follow_roles("user")
    @has_permissions(ban_members=True)
    async def tempban(self, ctx: Context, user: ProcessedUser, duration: Duration, *, reason: str = "No specific reason.") -> None:
        """Temporarely ban user from the server for given reason."""
        await self._apply_ban()

    @command()
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, user: ProcessedUser) -> None:
        """Revoke users ban on the server."""
        await self._apply_unban()

    @command()
    @follow_roles("member")
    @has_permissions(manage_roles=True)
    async def promote(self, ctx: Context, member: ProcessedMember, role: RoleConverter, *, reason: str = "No specific reason.") -> None:
        """Promote given user,"""
        await self._apply_promotion()

    @command()
    @has_permissions(manage_messages=True)
    async def clean(self, ctx: Context, amount: int) -> None:
        """Clean specified amount of messages."""
        await self._apply_clean()

    @command()
    @has_permissions(manage_messages=True)
    async def bot_cleanup(self, ctx: Context, amount: int) -> None:
        """Cleanup messages from bot."""
        await self._apply_bot_cleanup()

    # endregion
    # region: Strike Execution (private) functions

    async def _apply_kick(self) -> None:
        pass

    async def _apply_ban(self) -> None:
        pass

    async def _apply_unban(self) -> None:
        pass

    async def _apply_promotion(self) -> None:
        pass

    async def _apply_clean(self) -> None:
        pass

    async def _apply_bot_cleanup(self) -> None:
        pass

    # endregion

    async def cog_check(self, ctx: Context) -> t.Optional[bool]:
        """Make sure these commands can't be executed from DMs."""
        if ctx.guild is None:
            raise NoPrivateMessage
        return True


def setup(bot: Bot) -> None:
    bot.add_cog(Moderation(bot))
