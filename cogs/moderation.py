import asyncio
from collections import Counter
from cogs.utils.embedHandler import failure, info, success

import discord
from discord.ext import commands

# Converters

def can_execute_action(ctx, user, target):
    return user.id == ctx.bot.owner_id or \
           user == ctx.guild.owner or \
           user.top_role > target.top_role

class MemberNotFound(Exception):
    pass

async def resolve_member(guild, member_id):
    member = guild.get_member(member_id)
    if member is None:
        if guild.chunked:
            raise MemberNotFound()
        try:
            member = await guild.fetch_member(member_id)
        except discord.NotFound:
            raise MemberNotFound()
    return member

# TODO : Clean everything up
class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No specific reason"):
        """Kick a User."""
        embed1 = discord.Embed(title="Infraction information", color=discord.Color.red())
        embed1.add_field(name="Type", value="Kick")
        embed1.add_field(name="Reason", value=reason)
        embed1.set_thumbnail(url=member.avatar_url)
        embed1.set_author(name=member.name, url=member.avatar_url)
        embed1.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)

        await ctx.send(embed=embed1)
        await member.send(embed=embed1)
        await member.kick(reason=reason)

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Stated."):
        """Ban a User."""

        embed1 = discord.Embed(title="Infraction information", color=discord.Color.red())
        embed1.add_field(name="Type", value="Ban")
        embed1.add_field(name="Reason", value=reason)
        embed1.set_thumbnail(url=member.avatar_url)
        embed1.set_author(name=member.name, url=member.avatar_url)
        embed1.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)

        await ctx.send(embed=embed1)
        await member.send(embed=embed1)
        await member.ban(reason=reason)

    class ActionReason(commands.Converter):
        async def convert(self, ctx, argument):
            ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

            if len(ret) > 512:
                reason_max = 512 - len(ret) + len(argument)
                raise commands.BadArgument(f'Reason is too long ({len(argument)}/{reason_max})')
            return ret


    class MemberID(commands.Converter):
        async def convert(self, ctx, argument):
            try:
                m = await commands.MemberConverter().convert(ctx, argument)
            except commands.BadArgument:
                try:
                    member_id = int(argument, base=10)
                    m = await resolve_member(ctx.guild, member_id)
                except ValueError:
                    raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
                except MemberNotFound:
                    # hackban case
                    return type('_Hackban', (), {'id': member_id, '__str__': lambda s: f'Member ID {s.id}'})()

            if not can_execute_action(ctx, ctx.author, m):
                raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
            return m

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def multiban(self, ctx, members: commands.Greedy[MemberID], *, reason: ActionReason = None):
        """
        Bans multiple members from the server.
        
        This only works through banning via ID.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Ban Members permission.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        total_members = len(members)
        if total_members == 0:
            return await ctx.send('Missing members to ban.')

        confirm = await ctx.prompt(f'This will ban **{plural(total_members):member}**. Are you sure?', reacquire=False)
        if not confirm:
            return await ctx.send('Aborting.')

        failed = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                failed += 1

        await ctx.send(f'Banned {total_members - failed}/{total_members} members.')

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(ctx, *, member):
        """Unban a User."""
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if(user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned **{user.name}#{user.discriminator}**')
                return

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Clear specified number of messages."""

        if amount is not None:
            await ctx.channel.purge(limit=amount+1)
            await ctx.send('**Messages cleared** ' + ctx.message.author.mention)
            await asyncio.sleep(2.5)
            await ctx.channel.purge(limit=1)
        else:
            await ctx.send('please specify the number of messages to clear')

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def promote(self, ctx, member: discord.Member, role: discord.Role):
        """Promote member to role."""
        if role >= ctx.author.top_role:
            await ctx.send(embed=failure("Role needs to be below you in hierarchy."))
            return
        elif role in member.roles:
            await ctx.send(embed=failure(f"{member.mention} already has role {role.mention}!"))
            return

        await member.add_roles(role)

        await ctx.send(embed=success(f"{member.mention} is promoted to {role.mention}", ctx.me), delete_after=5)

        dm_embed = info(
            (
                f"You are now promoted to role **{role.name}** in our community.\n"
                f"`'With great power comes great responsibility'`\n"
                f"Be active and keep the community safe."
            ),
            ctx.me,
            "Congratulations!"
        )

        dm_embed.set_footer(text="Promotion Command.")
        await member.send(embed=dm_embed)

    async def _basic_cleanup_strategy(self, ctx, search):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me:
                await msg.delete()
                count += 1
        return {'Bot': count}

    async def _complex_cleanup_strategy(self, ctx, search):
        prefixes = tuple(self.client.get_guild_prefixes(ctx.guild))  # thanks startswith

        def check(m):
            return m.author == ctx.me or m.content.startswith(prefixes)

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel."""

        strategy = self._basic_cleanup_strategy

        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = self._complex_cleanup_strategy

        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']

        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'- **{author}**: {count}' for author, count in spammers)

        await ctx.send('\n'.join(messages), delete_after=10)


def setup(bot):
    bot.add_cog(Moderation(bot))
