import datetime
import textwrap
import typing as t
from collections import Counter

from discord import Color, Embed, Member
from discord.ext.commands import Bot, Cog, Context, command

from bot import constants

from .utils.embed_handler import status_embed


class Commands(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    # TODO : add number of bots, humans, dnd users, idle users, online users, and offline users, maybe device type too
    @command()
    async def members(self, ctx: Context) -> None:
        """Returns the number of members in a server."""
        member_by_status = Counter(str(m.status) for m in ctx.guild.members)
        bots = len([member for member in ctx.guild.members if member.bot])
        type = f"""
                Humans: {ctx.guild.member_count - bots}
                Bots: {bots}
            """
        status = f"""
                <:online:346921745279746048> {member_by_status["online"]}
                <:away:346921747330891780> {member_by_status["idle"]}
                <:dnd:346921781786836992> {member_by_status["dnd"]}
                <:offline:346921814435430400> {member_by_status["offline"]}
            """
        embed = Embed(title="Member count", description=ctx.guild.member_count, color=Color.dark_purple())
        embed.add_field(name="**❯❯ Member Status**", value=status)
        embed.add_field(name="**❯❯ Member Type**", value=type)
        embed.set_author(name=f"SERVER : {ctx.guild.name}")

        await ctx.send(embed=embed)

    @command()
    async def status(self, ctx: Context, member: t.Optional[Member] = None) -> None:
        """Returns the status of a member."""
        if member is None:
            member = ctx.author

        if member.id in constants.owner_ids:
            embed = status_embed(member, description="None")
        else:
            embed = status_embed(member)

        await ctx.send(embed=embed)

    @command(aliases=["server"])
    async def serverinfo(self, ctx: Context) -> None:
        """Get information about the server."""

        embed = Embed(colour=Color.gold())
        embed.title = f"{ctx.guild.name}'s stats and information."
        embed.description = ctx.guild.description if ctx.guild.description else None
        embed.add_field(
            name="__**General information:**__",
            value=textwrap.dedent(
                f"""
                **Owner:** {ctx.guild.owner}
                **Created at:** {datetime.datetime.strftime(ctx.guild.created_at, "%A %d %B %Y at %H:%M")}
                **Members:** {ctx.guild.member_count}
                **Nitro Tier:** {ctx.guild.premium_tier} | **Boosters:** {ctx.guild.premium_subscription_count}
                **File Size:** {round(ctx.guild.filesize_limit / 1048576)} MB
                **Bitrate:** {round(ctx.guild.bitrate_limit / 1000)} kbps
                **Emoji:** {ctx.guild.emoji_limit}
                """
            ),
        )

        embed.add_field(
            name="__**Channels:**__",
            value=textwrap.dedent(
                f"""
                **AFK timeout:** {int(ctx.guild.afk_timeout / 60)}m | **AFK channel:** {ctx.guild.afk_channel}
                **Text channels:** {len(ctx.guild.text_channels)} | **Voice channels:** {len(ctx.guild.voice_channels)}
                """
            ),
            inline=False,
        )

        embed.set_footer(text=f"ID: {ctx.guild.id}")

        await ctx.send(embed=embed)
        return

    @command(aliases=["user"])
    async def userinfo(self, ctx: Context, *, member: t.Optional[Member] = None) -> None:
        """
        Get information about you, or a specified member.

        `member`: The member to get information from. Can be a Mention, Name or ID.
        """

        if not member:
            member = ctx.author

        embed = Embed(colour=Color.gold())
        embed.title = f"{member}'s stats and information."
        embed.add_field(
            name="__**General information:**__",
            value=textwrap.dedent(
                f"""
                **Discord Name:** {member}
                **Created at:** {datetime.datetime.strftime(member.created_at, "%A %d %B %Y at %H:%M")}
                """
            ),
            inline=False,
        )

        embed.add_field(
            name="__**Server-related information:**__",
            value=textwrap.dedent(
                f"""
                **Nickname:** {member.nick}
                **Joined server:** {datetime.datetime.strftime(member.joined_at, "%A %d %B %Y at %H:%M")}
                **Top role:** {member.top_role.mention}
                """
            ),
            inline=False,
        )

        embed.set_thumbnail(url=member.avatar_url_as(format="png"))
        embed.set_footer(text=f"ID: {member.id}")

        await ctx.send(embed=embed)
        return


def setup(bot: Bot) -> None:
    bot.add_cog(Commands(bot))
