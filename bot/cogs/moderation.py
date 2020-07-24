import asyncio
import textwrap
import typing as t
from collections import Counter
from datetime import datetime

import discord
from discord import Color, Embed, Member, NotFound, Role
from discord.errors import Forbidden
from discord.ext.commands import (Cog, Context, Greedy, NoPrivateMessage,
                                  command, has_permissions)

from bot.core.bot import Bot
from bot.core.converters import ActionReason, ProcessedMember
from bot.core.decorators import follow_roles
from bot.utils.formats import Plural


class Moderation(Cog):
    """This cog provides moderation commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    @has_permissions(kick_members=True)
    @follow_roles()
    async def kick(self, ctx: Context, member: Member, *, reason: ActionReason = "No specific reason.") -> None:
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
    async def ban(self, ctx: Context, member: ProcessedMember, *, reason: ActionReason = "No specific reason.") -> None:
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
    async def multiban(self, ctx: Context, members: Greedy[ProcessedMember], *, reason: ActionReason = None) -> None:
        """Bans multiple members from the server."""
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"

        total_members = len(members)
        if total_members == 0:
            return await ctx.send("No members to ban.")

        confirm = await ctx.prompt(f"This will ban **{Plural(total_members):member}**. Are you sure?", reacquire=False)
        if not confirm:
            return await ctx.send("Aborting.")

        failed = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                failed += 1

        await ctx.send(f"Banned {total_members - failed}/{total_members} members.")

    @command()
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, *, user: ProcessedMember) -> None:
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
    async def clear(self, ctx: Context, amount: int) -> None:
        """Clear specified number of messages."""
        await ctx.channel.purge(limit=amount + 1)

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
