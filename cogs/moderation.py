import asyncio

import discord
from cogs.utils.embedHandler import failure, info, success
from discord.ext import commands


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


def setup(bot):
    bot.add_cog(Moderation(bot))
