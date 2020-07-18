import textwrap
import typing as t
from datetime import datetime

from discord import Color, Embed, Member, User
from discord.errors import Forbidden
from discord.ext.commands import (
    Cog, Context, NoPrivateMessage,
    RoleConverter, command, has_permissions
)

from bot.core.bot import Bot
from bot.core.converters import Duration, ProcessedMember, ProcessedUser
from bot.core.decorators import follow_roles


class Moderation(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    # region: Commands

    @command()
    @follow_roles()
    @has_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: ProcessedMember, *, reason: str = "No specific reason.") -> None:
        """Kick user from the server for given reason."""
        await self._apply_kick(ctx, member, reason)

    @command()
    @follow_roles()
    @has_permissions(administrator=True)
    async def ban(self, ctx: Context, user: ProcessedUser, *, reason: str = "No specific reason.") -> None:
        """"Permanently ban user from the server for given reason."""
        await self._apply_ban(ctx, user, reason)

    @command()
    @follow_roles()
    @has_permissions(ban_members=True)
    async def tempban(self, ctx: Context, user: ProcessedUser, duration: Duration, *, reason: str = "No specific reason.") -> None:
        """Temporarely ban user from the server for given reason."""
        await self._apply_ban()

    @command()
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, user: ProcessedUser) -> None:
        """Revoke users ban on the server."""
        await self._apply_unban(ctx, user)

    @command()
    @follow_roles()
    @has_permissions(manage_roles=True)
    async def promote(self, ctx: Context, member: ProcessedMember, role: RoleConverter, *, reason: str = "No specific reason.") -> None:
        """Promote user to any given role (less than yours)."""
        await self._apply_promotion()

    @command()
    @has_permissions(manage_messages=True)
    async def clean(self, ctx: Context, amount: int) -> None:
        """Clean specified amount of messages."""
        await self._apply_clean()

    @command()
    @has_permissions(manage_messages=True)
    async def cleanup(self, ctx: Context, amount: int) -> None:
        """Cleanup messages from bot."""
        await self._apply_cleanup()

    # endregion
    # region: Strike Execution (private) functions

    async def _apply_kick(self, ctx: Context, member: Member, reason: str) -> None:
        dm_sent = await self._send_DM(member, ctx, "Kicked", reason)
        await self._send_server_embed(member, ctx, "Kicked", reason)
        await ctx.send(dm_sent)

    async def _apply_ban(self, ctx: Context, user: User, reason: str) -> None:
        dm_sent = await self._send_DM(user, ctx, "Banned", reason)
        await self._send_server_embed(user, ctx, "Banned", reason)
        await ctx.send(dm_sent)

    async def _apply_unban(self, ctx: Context, user: User) -> None:
        dm_sent = await self._send_DM(user, ctx, "Unbanned", "", color=Color.green())
        await self._send_server_embed(user, ctx, "Unbanned", "", color=Color.green())
        await ctx.send(dm_sent)

    async def _apply_promotion(self) -> None:
        pass

    async def _apply_clean(self) -> None:
        pass

    async def _apply_cleanup(self) -> None:
        pass

    async def _send_DM(self, user: t.Union[Member, User], ctx: Context, action: str, reason: str, color: Color = Color.red()) -> bool:
        reason_string = f"{reason}\n" if reason else '\r'
        embed = Embed(
            title=f"You were {action}",
            description=textwrap.dedent(
                f"""
                {reason_string}
                *Server: {ctx.guild.name}*
                """
            ),
            color=color,
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        try:
            await user.send(embed=embed)
            return True
        except Forbidden:
            return False

    async def _send_server_embed(self, user: t.Union[Member, User], ctx: Context, action: str, reason: str, color: Color = Color.red()) -> None:
        reason_string = f"**Reason**: {reason}\n" if reason else '\r'
        embed = Embed(
            title=f"User {action}",
            description=textwrap.dedent(
                f"""
                {reason_string}
                **User**: {user.mention} (`{user.id}`)
                **Moderator**: {ctx.author.mention} (`{ctx.author.id}`)
                """
            ),
            color=color,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=user.avatar_url_as(format="png", size=256))
        await ctx.send(embed=embed)

    # endregion

    async def cog_check(self, ctx: Context) -> t.Optional[bool]:
        """Make sure these commands can't be executed from DMs."""
        if ctx.guild is None:
            raise NoPrivateMessage
        return True


def setup(bot: Bot) -> None:
    bot.add_cog(Moderation(bot))
