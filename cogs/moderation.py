import asyncio
import textwrap
import typing as t
from collections import Counter
from contextlib import suppress
from datetime import datetime
from functools import wraps

import discord
from discord import Color, Embed, Guild, Member, NotFound, Role, User, TextChannel
from discord.errors import Forbidden
from discord.ext.commands import BadArgument, Bot, Cog, Context, Converter, Greedy, NoPrivateMessage, UserConverter, command, has_permissions

from .utils.formats import Plural


class MemberNotFound(NotFound):
    pass


async def get_member(guild: Guild, user: User) -> Member:
    member = guild.get_member(user.id)
    if not member:
        try:
            member = await guild.fetch_member(user.id)
        except NotFound:
            raise MemberNotFound(f"No member with ID: {user.id} on guild {guild.id}")
    return member


class ActionReason(Converter):
    """Make sure reason length is within 512 characters."""

    async def convert(self, ctx: Context, argument: str) -> str:
        """Add ID to the reason and make sure it's withing length."""
        reason = f"[ID: {ctx.author.id}]: {argument}"
        if len(reason) > 512:
            reason_max = 512 - len(reason) + len(argument)
            raise BadArgument(f"Reason is too long ({len(argument)}/{reason_max})")
        return argument


class UserID(UserConverter):
    """
    Try to convert any accepted string into `Member` or `User`.

    When possible try to convert user into `Member` but if not, use `User` instead.
    """

    async def convert(self, ctx: Context, argument: str) -> Member:
        """Convert the `argument` into `Member` or `User`."""
        with suppress(BadArgument):
            # Try to use UserConverter first
            user = await super().convert(ctx, argument)
            try:
                return await get_member(ctx.guild, user)
            except MemberNotFound:
                return user

        # If UserConverter failed, try to fetch user as ID
        try:
            user = await ctx.bot.fetch_user(int(argument))
            try:
                return await get_member(ctx.guild, user)
            except MemberNotFound:
                return user
        except ValueError:
            raise BadArgument(f"{argument} is not a valid user or user ID")


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
                    member = await get_member(ctx.guild, user)
                except MemberNotFound:
                    # Skip checks in case of bad member
                    await func(self, ctx, *args, **kwargs)
                    return
            elif isinstance(user, Member):
                member = user
            else:
                raise ValueError("Specified argument is not `Member` or `User`")

            actor = ctx.author
            # Run the function in case actor has higher role then member, or is a guild owner
            if actor == ctx.guild.owner or member.top_role <= actor.top_role:
                await func(self, ctx, *args, **kwargs)
            else:
                embed = Embed(
                    title="You can't target this user",
                    description=textwrap.dedent(
                        f"""
                        {member.mention} has higher top role that yours.

                        **❯❯ You can only target users with lower top role.**
                        """
                    ),
                    color=discord.Color.red(),
                )
                await ctx.send(f"Sorry, {actor.mention}", embed=embed)

        return inner

    return wrap


class Moderation(Cog):
    """This cog provides moderation commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    @has_permissions(kick_members=True)
    @follow_roles()
    async def kick(self, ctx: Context, member: Member, *, reason: str = "No specific reason.") -> None:
        """Kick a User."""
        if not isinstance(member, Member):
            embed = Embed(
                title="You can't kick this user",
                description=textwrap.dedent(
                    f"""
                    {member.mention} (`{member.id}`) doesn't seem to be a member of this server.

                    **❯❯ You can only kick server members.**
                    """
                ),
                color=discord.Color.red(),
            )
            await ctx.send(f"Sorry {ctx.author.mention}", embed=embed)
            return

        server_embed = discord.Embed(
            title="User Kicked",
            description=textwrap.dedent(
                f"""
                **Reason**: {reason}
                **User**: {member.mention} (`{member.id}`)
                **Moderator**: {ctx.author.mention} (`{ctx.author.id}`)
                """
            ),
            color=discord.Color.orange(),
            timestamp=datetime.utcnow(),
        )
        server_embed.set_thumbnail(url=member.avatar_url_as(format="png", size=256))

        dm_embed = discord.Embed(
            title="You were Kicked",
            description=textwrap.dedent(
                f"""
                {reason}

                *Server: {ctx.guild.name}*
                """
            ),
            color=discord.Color.red(),
            timestamp=datetime.utcnow(),
        )
        dm_embed.set_thumbnail(url=ctx.guild.icon_url)

        await ctx.send(embed=server_embed)
        await member.send(embed=dm_embed)
        await member.kick(reason=reason)

    @command()
    @has_permissions(ban_members=True)
    @follow_roles()
    async def ban(self, ctx: Context, member: UserID, *, reason: str = "No specific reason.") -> None:
        """Ban a User."""
        server_embed = discord.Embed(
            title="User Banned",
            description=textwrap.dedent(
                f"""
                **Reason**: {reason}
                **User**: {member.mention} (`{member.id}`)
                **Moderator**: {ctx.author.mention} (`{ctx.author.id}`)
                """
            ),
            color=discord.Color.orange(),
            timestamp=datetime.utcnow(),
        )
        server_embed.set_thumbnail(url=member.avatar_url_as(format="png", size=256))

        dm_embed = discord.Embed(
            title="You were Banned",
            description=textwrap.dedent(
                f"""
                {reason}

                *Server: {ctx.guild.name}*
                """
            ),
            color=discord.Color.red(),
            timestamp=datetime.utcnow(),
        )
        dm_embed.set_thumbnail(url=ctx.guild.icon_url)

        await ctx.send(embed=server_embed)
        await member.send(embed=dm_embed)
        await member.ban(reason=reason)

    @command()
    @has_permissions(ban_members=True)
    async def multiban(self, ctx: Context, members: Greedy[UserID], *, reason: str = None) -> None:
        """Bans multiple members from the server."""
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"

        total_members = len(members)
        if total_members == 0:
            await ctx.send("No members to ban.")
            return

        confirm = await ctx.prompt(f"This will ban **{Plural(total_members):member}**. Are you sure?", reacquire=False)
        if not confirm:
            await ctx.send("Aborting.")
            return

        failed = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                failed += 1

        await ctx.send(f"Banned {total_members - failed}/{total_members} members.")

    @command()
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, *, user: UserID) -> None:
        """Unban a User."""
        try:
            await ctx.guild.unban(user)

            embed = discord.Embed(
                title="User Unbanned",
                description=textwrap.dedent(
                    f"""
                    **User**: {user.mention} (`{user.id}`)
                    **Moderator**: {ctx.author.mention} (`{ctx.author.id}`)
                    """
                ),
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
            embed.set_thumbnail(url=user.avatar_url_as(format="png", size=256))
            await ctx.send(embed=embed)
        except NotFound:
            embed = discord.Embed(
                title="Ban not Found!",
                description=textwrap.dedent(
                    f"""
                    There are no active bans on discord for {user.mention}.
                    He isn't banned here.
                    """
                ),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

    @command()
    @has_permissions(manage_messages=True)
    async def clear(self, ctx: Context, amount: int, target: User = None) -> None:
        """Clear specified number of messages."""
        if target is None:
            await ctx.message.channel.purge(limit=amount)
        else:
            await ctx.message.channel.purge(limit=amount, check=lambda message: message.author == target)

        embed = Embed(
            description=textwrap.dedent(
                f"""
                **Messages Cleared!**
                **Amount**: {amount}
                """
            ),
            color=discord.Color.orange(),
        )
        message = await ctx.send(ctx.author.mention, embed=embed)
        await asyncio.sleep(2.5)
        await message.delete()

    @command()
    @has_permissions(manage_messages=True)
    async def shift(self, ctx, count: int, target: TextChannel, copy: bool = False) -> None:
        """Copy or Move specified messages amount to specified channel"""
        messages = []
        async for message in ctx.message.channel.history(limit=count):
            embed = Embed(description=message.content, color=Color.green())
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            embed.timestamp = message.created_at
            messages.append(embed)

            if not copy:
                await message.delete()

        await target.send(f'Message source : {ctx.message.channel.mention}.')

        for embed in reversed(messages):
            await target.send(embed=embed)

    @command()
    @has_permissions(manage_messages=True)
    async def dm(self, ctx: Context, members: Greedy[Member], *, message: str) -> None:
        """Dm a List of Specified User from Your Guild."""
        embed = Embed(
            title="Notice!",
            description=message,
            color=Color.dark_magenta()
        )
        embed.set_footer(text=f"From {ctx.guild.name}", icon_url=ctx.guild.icon_url)

        for member in members:
            await member.send(embed=embed)

    @command()
    @has_permissions(administrator=True)
    async def dmall(self, ctx: Context, *, message: str) -> None:
        """Dm all Users from Your Guild."""
        embed = Embed(
            title="Notice!",
            description=message,
            color=Color.dark_magenta()
        )
        embed.set_footer(text=f"From {ctx.guild.name}", icon_url=ctx.guild.icon_url)

        for member in ctx.guild.members:
            with suppress(Forbidden):
                await member.send(embed=embed)

    @command()
    @has_permissions(manage_roles=True)
    async def lock(self, ctx, channels: Greedy[TextChannel] = None, reason: str = 'Not Specified') -> None:
        """Disable @everyone's permission to send message on given channel or current channel if not specified."""
        if channels is None:
            channels = [ctx.channel]
        for c in channels:
            await c.set_permissions(c.guild.default_role, send_messages=False,
                                    reason=f"Reason: {reason} | Requested by {ctx.author}.")
            await c.send("🔒 Locked down this channel.")
        if not channels == [ctx.channel]:
            await ctx.send(f"Locked down {len(channels)} channel{'s' if len(channels) > 1 else ''}.")

    @command()
    @has_permissions(manage_roles=True)
    async def unlock(self, ctx, channels: Greedy[TextChannel] = None, reason: str = 'Not specified') -> None:
        """Reset @everyone's permission to send message on given channel or current channel if not specified."""
        if channels is None:
            channels = [ctx.channel]
        for c in channels:
            await c.set_permissions(c.guild.default_role, send_messages=None,
                                    reason=f"Reason: {reason} | Requested by {ctx.author}.")
        await ctx.send(f"Unlocked {len(channels)} channel{'s' if len(channels) > 1 else ''}.")

    @command()
    @has_permissions(manage_channels=True)
    async def slowmode(self, ctx, channels: Greedy[TextChannel] = None, seconds: int = 10, reason: str = "Not specified") -> None:
        """Set channel's slowmode delay, default = 10s."""
        if not (0 <= seconds <= 21600):
            await ctx.send(":x: The duration is extreme or very low.")
            return

        if channels is None:
            channels = ctx.channel

        for c in channels:
            await c.edit(reason=f"Reason: {reason} | Requested by {ctx.author}.", slowmode_delay=seconds)
        if seconds != 0:
            await ctx.send(f"✅ Set {len(channels)} channel{'s' if len(channels) > 1 else ''} with {seconds}sec slowmode.")
        else:
            await ctx.send(f"✅ Disabled slowmode for {len(channels)} channel{'s' if len(channels) > 1 else ''}.")

    @command()
    @has_permissions(manage_roles=True)
    async def promote(self, ctx: Context, member: Member, *, role: Role) -> None:
        """Promote member to role."""
        if role >= ctx.author.top_role:
            embed = Embed(
                title="Insufficient permissions",
                description="You can give someone role which is higher in the role hierarchy than your top role.",
                color=Color.red(),
            )
            await ctx.send(embed=embed)
            return
        if role in member.roles:
            embed = Embed(title="Error", description=f"{member.mention} already has the {role.mention} role!", color=Color.red())
            await ctx.send(embed=embed)
            return

        try:
            await member.add_roles(role)
        except Forbidden:
            embed = Embed(
                title="Insufficient permission",
                description=textwrap.dedent(
                    f"""
                    Sorry, I don't have sufficient permission to promote to this role.

                    **My Top Role**: {ctx.me.top_role.mention}
                    **Requested Role**: {role.mention}
                    """
                ),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        embed = Embed(
            title="Promotion!",
            description=textwrap.dedent(
                f"""
                {member.mention} has been promoted to {role.mention}!
                :tada: Congratulations! :tada:
                """
            ),
            color=Color.green(),
        )
        await ctx.send(embed=embed)

        dm_embed = Embed(
            title="Congratulations!",
            description=textwrap.dedent(
                f"""
                You have been promoted to **{role.name}** in our community.
                `'With great power comes great responsibility'`
                Be active and keep the community safe
                """
            ),
            color=Color.green(),
        )
        dm_embed.set_footer(text=f"Server: {ctx.guild.name}", icon_url=ctx.guild.icon_url)
        await member.send(embed=dm_embed)

    async def _basic_cleanup_strategy(self, ctx: Context, amount: int) -> dict:
        count = 0
        async for msg in ctx.history(limit=amount, before=ctx.message):
            if msg.author == ctx.me:
                await msg.delete()
                count += 1
        return {ctx.me: count}

    async def _complex_cleanup_strategy(self, ctx: Context, amount: int) -> Counter:
        prefixes = tuple(await self.bot.get_prefix(ctx.message))

        def check(bot: Bot) -> bool:
            return bot.author == ctx.me or bot.content.startswith(prefixes)

        deleted = await ctx.channel.purge(limit=amount, check=check, before=ctx.message)
        return Counter(m.author for m in deleted)

    @command()
    @has_permissions(manage_messages=True)
    async def cleanup(self, ctx: Context, amount: int = 100) -> None:
        """Cleans up the bots messages from the channel."""
        strategy = self._basic_cleanup_strategy

        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = self._complex_cleanup_strategy

        spammers = await strategy(ctx, amount)
        deleted = sum(spammers.values())

        if deleted:
            authors = ""
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            for author, count in spammers:
                authors += f"• {author.mention}: {count}\n"

            embed = Embed(
                title="Message Cleanup",
                description=textwrap.dedent(
                    f"""
                    {deleted} messages {' was' if deleted == 1 else 's were'} removed.

                    {authors}
                    """
                ),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, delete_after=10)

    async def cog_check(self, ctx: Context) -> t.Union[None, bool]:
        """Make sure these commands can't be executed from DMs."""
        if ctx.guild is None:
            raise NoPrivateMessage
        return True


def setup(bot: Bot) -> None:
    bot.add_cog(Moderation(bot))
