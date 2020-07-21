import datetime
import json
import textwrap
import typing as t
from collections import Counter

from bot import config
from bot.core.bot import Bot

from discord import ActivityType, Color, Embed, Guild, Member, Status, User
from discord.ext.commands import Cog, Context, command

STATUSES = {
    Status.online: "ONLINE <:online:346921745279746048>",
    Status.idle: "IDLE <:away:346921747330891780>",
    Status.dnd: "DND <:dnd:346921781786836992>",
    Status.offline: "OFFLINE <:offline:346921814435430400>",
}


class Commands(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def changeprefix(self, ctx: Context, prefix: str) -> None:
        """Changes the prefix for the bot."""
        with open("bot/assets/prefixes.json", "r") as file:
            prefixes = json.load(file)

        prefixes[str(ctx.guild.id)] = prefix

        with open("bot/assets/prefixes.json", "w") as file:
            json.dump(prefixes, file, indent=4)

        await ctx.send(f"Prefix changed to **{prefix}**")

    @command()
    async def resetprefix(self, ctx: Context, prefix: str) -> None:
        """Resets the prefix of the bot to original one."""
        with open("bot/assets/prefixes.json", "r") as file:
            prefixes = json.load(file)

        prefixes[str(ctx.guild.id)] = config.COMMAND_PREFIX

        with open("bot/assets/prefixes.json", "w") as file:
            json.dump(prefixes, file, indent=4)

        await ctx.send(f"Prefix changed to **{prefix}**")

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
                {STATUSES[Status.online]} {member_by_status["online"]}
                {STATUSES[Status.idle]} {member_by_status["idle"]}
                {STATUSES[Status.dnd]} {member_by_status["dnd"]}
                {STATUSES[Status.offline]} {member_by_status["offline"]}
            """
        embed = Embed(title="Member count", description=ctx.guild.member_count, color=Color.dark_purple())
        embed.add_field(name="**❯❯ Member Status**", value=status)
        embed.add_field(name="**❯❯ Member Type**", value=type)
        embed.set_author(name=f"SERVER : {ctx.guild.name}")

        await ctx.send(embed=embed)

    @command(aliases=["server"])
    async def serverinfo(self, ctx: Context) -> None:
        """Get information about the server."""
        await ctx.send(embed=self.get_server_embed(ctx.guild))

    @command(aliases=["user"])
    async def userinfo(self, ctx: Context, user: t.Optional[t.Union[Member, User]] = None) -> None:
        """
        Get information about you, or a specified member.

        `user`: The user to get information from. Can be a Mention, Name or ID.
        """
        if not user:
            user = ctx.author

        await ctx.send(embed=self.get_user_embed(user))

    def get_user_embed(self, user: t.Union[User, Member]) -> Embed:
        """Create an embed with detailed info about given user"""
        embed = Embed(
            title=f"{user}'s stats and information.",
            color=Color.blue()
        )

        created_time = datetime.datetime.strftime(user.created_at, "%A %d %B %Y at %H:%M")

        user_info = textwrap.dedent(
            f"""
            Mention: {user.mention}
            Date Created: {created_time}
            ID: {user.id}
            """
        )

        if isinstance(user, Member):
            member_info = []

            if user.nick:
                member_info.append(f"Nickname: {user.nick}")

            joined_time = datetime.datetime.strftime(user.joined_at, "%A %d %B %Y at %H:%M")
            member_info.append(f"Joined server: {joined_time}")

            member_info.append("")

            try:
                member_info.append(f"Status: {STATUSES[user.status]}")
            except KeyError:
                member_info.append("Status: N/A")

            if user.status == Status.offline:
                member_info.append("Device: :no_entry:")
            elif user.is_on_mobile():
                member_info.append("Device: Phone :iphone:")
            else:
                member_info.append("Device: PC :desktop:")

            if not user.activity:
                member_info.append("Activity: N/A")
            elif user.activity.type != ActivityType.custom:
                member_info.append(f"Activity: {user.activity.type.name} {user.activity.name}")
            else:
                member_info.append(f"Activity: {user.activity.name}")

            member_info.append("")

            roles = " ".join(role.mention for role in user.roles[1:])
            member_info.append(f"Top Role: {user.top_role.mention}")
            member_info.append(f"All Roles: {roles}")
        else:
            member_info = ["No server related info, this user is not a member of this server."]

        embed.add_field(
            name="❯❯ General information",
            value=user_info,
            inline=False
        )

        embed.add_field(
            name="❯❯ Server-related information",
            value="\n".join(member_info),
            inline=False
        )

        embed.set_thumbnail(url=user.avatar_url_as(format="png"))

        return embed

    def get_server_embed(self, guild: Guild) -> Embed:
        embed = Embed(
            title="Serer's stats and information.",
            description=guild.description if guild.description else None,
            color=Color.gold()
        )

        embed.add_field(
            name="❯❯ General information",
            value=textwrap.dedent(
                f"""
                Name: {guild.name}
                Created at: {datetime.datetime.strftime(guild.created_at, "%A %d %B %Y at %H:%M")}
                Members: {guild.member_count}
                Owner: {guild.owner}
                Nitro Tier: {guild.premium_tier} | Boosters: {guild.premium_subscription_count}

                File Size: {round(guild.filesize_limit / 1048576)} MB
                Bitrate: {round(guild.bitrate_limit / 1000)} kbps
                Emoji: {guild.emoji_limit}
                """
            ),
        )
        embed.add_field(
            name="❯❯ Channels",
            value=textwrap.dedent(
                f"""
                Text channels: {len(guild.text_channels)}
                Voice channels: {len(guild.voice_channels)}
                AFK timeout: {round(guild.afk_timeout / 60)}m | AFK channel: {guild.afk_channel}
                """
            ),
            inline=False,
        )

        embed.set_thumbnail(url=guild.icon_url)
        embed.set_footer(text=f"ID: {guild.id}")

        return embed


def setup(bot: Bot) -> None:
    bot.add_cog(Commands(bot))
