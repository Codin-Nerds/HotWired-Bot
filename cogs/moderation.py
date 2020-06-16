import asyncio
import textwrap
import typing as t
from collections import Counter

import discord
from discord import Color, Embed
from discord.ext.commands import (
    BadArgument,
    Bot,
    Cog,
    Context,
    Converter,
    Greedy,
    MemberConverter,
    bot_has_permissions,
    command,
    guild_only,
    has_permissions,
)

from .utils.formats import Plural


class ActionReason(Converter):
    async def convert(self, ctx: Context, argument: str) -> str:
        ret = f"{ctx.author} (ID: {ctx.author.id}): {argument}"

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise BadArgument(f"Reason is too long ({len(argument)}/{reason_max})")
        return ret


class UserID(Converter):
    async def convert(self, ctx: Context, member_id: int) -> t.Union[str, type]:
        try:
            member = await MemberConverter.convert(ctx, member_id)
        except BadArgument:
            try:
                member = await resolve_user(ctx.guild, member_id)
            except ValueError:
                raise BadArgument(f"{member_id} is not a valid member or member ID.") from None
            except MemberNotFound:
                await ctx.guild.ban(discord.Object(id=member_id))

        if not can_execute_action(ctx, ctx.author, member):
            raise BadArgument("You cannot do this action on this user due to role hierarchy.")
        return member


def can_execute_action(ctx: Context, user: discord.User, target: discord.User) -> bool:
    return user.id == ctx.bot.owner_id or user == ctx.guild.owner or user.top_role > target.top_role


class MemberNotFound(Exception):
    pass


async def resolve_user(bot: Bot, member_id: int) -> discord.User:
    user = bot.get_member(member_id)
    if user is None:
        raise MemberNotFound()
    return user


# TODO : Clean everything up
class Moderation(Cog):
    """This cog provides moderation commands."""

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @command()
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: UserID, *, reason: str = "No specific reason.") -> None:
        """Kick a User."""
        embed = discord.Embed(title="Infraction information", color=discord.Color.red())
        embed.add_field(name="Type", value="Kick")
        embed.add_field(name="Reason", value=reason)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=member.name, url=member.avatar_url)
        embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)

        await ctx.send(embed=embed)
        await member.send(embed=embed)
        await member.kick(reason=reason)

    @command()
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban(self, ctx: Context, member: UserID, *, reason: str = "No Reason Stated.") -> None:
        """Ban a User."""
        embed = discord.Embed(title="Infraction information", color=discord.Color.red())
        embed.add_field(name="Type", value="Ban")
        embed.add_field(name="Reason", value=reason)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=member.name, url=member.avatar_url)
        embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)

        await ctx.send(embed=embed)
        await member.send(embed=embed)
        await member.ban(reason=reason)

    @command()
    @guild_only()
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def multiban(self, ctx: Context, members: Greedy[UserID], *, reason: ActionReason = None) -> None:
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
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, *, member: str) -> None:
        """Unban a User."""
        # TODO: Use custom converter for `member`
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        # TODO: There might be a better way to handle this
        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"Unbanned **{user.name}#{user.discriminator}**")
                return

    @command()
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear(self, ctx: Context, amount: int) -> None:
        """Clear specified number of messages."""
        # TODO: Check if this condition is necessary
        if amount is not None:
            await ctx.channel.purge(limit=amount + 1)

            # TODO: This message might be getting in the way,
            # purpose of cleaning is to remove messages, not add more of them
            await ctx.send("**Messages cleared** " + ctx.message.author.mention)
            await asyncio.sleep(2.5)
            await ctx.channel.purge(limit=1)
        else:
            await ctx.send("please specify the number of messages to clear")

    @command()
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_messages=True)
    async def promote(self, ctx: Context, member: discord.Member, role: discord.Role) -> None:
        """Promote member to role."""
        # TODO: A custom check can handle this
        if role >= ctx.author.top_role:
            embed = Embed(title="Error", description="Role needs to be below you in hierarchy.", color=Color.red(),)
            await ctx.send(embed=embed)
            return
        if role in member.roles:
            embed = Embed(title="Error", description=f"{member.mention} already had role {role.mention}!", color=Color.red(),)
            await ctx.send(embed=embed)
            return

        await member.add_roles(role)

        embed = Embed(title="Promotion!", description=f"{member.mention} has been promoted to {role.mention}!", color=Color.green(),)
        await ctx.send(embed=embed, delete_after=5)

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
        await dm_embed.set_footer(text=f"Server: {ctx.guild.name}")
        await member.send(embed=dm_embed)

    async def _basic_cleanup_strategy(self, ctx: Context, search: int) -> dict:
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me:
                await msg.delete()
                count += 1
        return {"Bot": count}

    async def _complex_cleanup_strategy(self, ctx: Context, search: int) -> Counter:
        prefixes = tuple(self.bot.get_guild_prefixes(ctx.guild))  # thanks startswith

        def check(member: discord.Bot) -> bool:
            return member.author == ctx.me or member.content.startswith(prefixes)

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @command()
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def cleanup(self, ctx: Context, search: int = 100) -> None:
        """Cleans up the bot's messages from the channel."""

        strategy = self._basic_cleanup_strategy

        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = self._complex_cleanup_strategy

        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [f"{deleted} message{' was' if deleted == 1 else 's were'} removed."]

        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"- **{author}**: {count}" for author, count in spammers)

        await ctx.send("\n".join(messages), delete_after=10)


def setup(bot: Bot) -> None:
    bot.add_cog(Moderation(bot))
