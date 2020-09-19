import datetime
import textwrap
import typing as t
import humanize
from collections import Counter

from discord import ActivityType, Color, Embed, Guild, Member, Status, User, utils, VoiceRegion
from discord.ext.commands import Cog, Context, command, has_permissions
import discord

from bot.core.bot import Bot
from bot import config

STATUSES = {
    Status.online: "ONLINE",
    Status.idle: "IDLE",
    Status.dnd: "DND",
    Status.offline: "OFFLINE",
}


class Commands(Cog):
    """Common commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.features = {
            'VIP_REGIONS': 'Has VIP voice regions',
            'VANITY_URL': 'Can have vanity invite',
            'INVITE_SPLASH': 'Can have invite splash',
            'VERIFIED': 'Is verified server',
            'PARTNERED': 'Is partnered server',
            'MORE_EMOJI': 'Can have 50+ emoji',
            'DISCOVERABLE': 'Is discoverable',
            'FEATURABLE': 'Is featurable',
            'COMMERCE': 'Can have store channels',
            'PUBLIC': 'Is public',
            'NEWS': 'Can have news channels',
            'BANNER': 'Can have banner',
            'ANIMATED_ICON': 'Can have animated icon',
            'PUBLIC_DISABLED': 'Can not be public',
            'WELCOME_SCREEN_ENABLED': 'Can have welcome screen'
        }

    @command()
    @has_permissions(manage_guild=True)
    async def changeprefix(self, ctx: Context, prefix: str = None) -> None:
        """Changes the prefix for the bot."""
        if prefix:
            async with self.bot.pool.acquire(timeout=5) as database:
                ctx_id = self.bot.get_id(ctx)

                await database.execute(
                    "INSERT INTO public.prefixes VALUES ($1, $2) ON CONFLICT (ctx_id) DO UPDATE SET prefix=$2",
                    ctx_id,
                    prefix,
                )
                self.bot.prefix_dict[ctx_id] = prefix
                return await ctx.send(
                    f"Prefix changed to `{utils.escape_markdown(prefix)}`"
                )

        old_prefix = utils.escape_markdown(
            await self.bot.get_prefix(ctx.message, False)
        )
        await ctx.send(f"The prefix for this channel is `{old_prefix}`")

    @command()
    @has_permissions(manage_guild=True)
    async def resetprefix(self, ctx: Context) -> None:
        """Resets the prefix of the bot to original one."""
        prefix = config.COMMAND_PREFIX

        async with self.bot.pool.acquire(timeout=5) as database:
            ctx_id = self.bot.get_id(ctx)

            await database.execute(
                "INSERT INTO public.prefixes VALUES ($1, $2) ON CONFLICT (ctx_id) DO UPDATE SET prefix=$2",
                ctx_id,
                prefix,
            )
            self.bot.prefix_dict[ctx_id] = prefix
            return await ctx.send(
                f"Prefix changed to `{utils.escape_markdown(prefix)}`"
            )

    @command()
    async def icon(self, ctx: Context, *, guild: Guild = None) -> None:
        """
        Displays a servers icon.
        `guild`: The server of which to get the icon for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.icon:
            await ctx.send(
                description=f'The server `{guild}` does not have an icon.',
                color=Color.red()
            )
            return

        embed = Embed(
            title=f"{guild.name}'s icon",
            description=f'''
            [PNG]({guild.icon_url_as(format="png")})
            [JPEG]({guild.icon_url_as(format="jpeg")})
            [WEBP]({guild.icon_url_as(format="webp")})
            ''',
            color=Color.blue()
        )
        embed.set_image(url=str(guild.icon_url_as(format='png')))

        if guild.is_icon_animated():
            embed.description += f'\n[GIF]({guild.icon_url_as(format="gif")})'
            embed.set_image(url=str(guild.icon_url_as(size=1024, format='gif')))

        await ctx.send(embed=embed)

    @command()
    async def banner(self, ctx: Context, *, guild: Guild = None):
        """
        Displays a servers banner.
        `guild`: The server of which to get the banner for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.banner:
            await ctx.send(
                description=f'The server `{guild}` does not have an banner.',
                color=Color.red()
            )
            return

        embed = Embed(
            title=f"{guild.name}'s banner",
            description=f'''
            [PNG]({guild.banner_url_as(format="png")})
            [JPEG]({guild.banner_url_as(format="jpeg")})
            [WEBP]({guild.banner_url_as(format="webp")})''',
            colour=Color.blue(),
        )
        embed.set_image(url=str(guild.banner_url_as(format='png')))

        await ctx.send(embed=embed)
        return

    @command()
    async def splash(self, ctx: Context, *, guild: Guild = None):
        """
        Displays a servers splash.
        `guild`: The server of which to get the splash for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild

        if not guild.splash:
            await ctx.send(
                description=f'The server `{guild}` does not have an splash icon.',
                color=Color.red()
            )
            return

        embed = Embed(color=discord.Color.blurple(), title=f"{guild.name}'s splash")
        embed.description = f'''
            [PNG]({guild.splash_url_as(format="png")})
            [JPEG]({guild.splash_url_as(format="jpeg")})
            [WEBP]({guild.splash_url_as(format="webp")})
        '''
        embed.set_image(url=str(guild.splash_url_as(format='png')))

        return await ctx.send(embed=embed)

    @command()
    async def members(self, ctx: Context) -> None:
        """Get the number of members in the server."""
        member_by_status = Counter(str(m.status) for m in ctx.guild.members)
        bots = len([member for member in ctx.guild.members if member.bot])
        member_type = f"""
                Member: {ctx.guild.member_count - bots}
                Bots: {bots}
            """
        status = f"""
                {STATUSES[Status.online]}: **{member_by_status["online"]}**
                {STATUSES[Status.idle]}: **{member_by_status["idle"]}**
                {STATUSES[Status.dnd]}: **{member_by_status["dnd"]}**
                {STATUSES[Status.offline]}: **{member_by_status["offline"]}**
            """
        embed = Embed(title="Member count", description=ctx.guild.member_count, color=Color.dark_purple())
        embed.add_field(name="**❯❯ Member Status**", value=status)
        embed.add_field(name="**❯❯ Member Type**", value=member_type)
        embed.set_author(name=f"SERVER : {ctx.guild.name}")
        embed.set_footer(text="Powered by HotWired")

        await ctx.send(embed=embed)

    @command(aliases=["server"])
    async def serverinfo(self, ctx: Context, guild: Guild = None) -> None:
        """Get information about the server."""
        if not guild:
            guild = ctx.guild
        await ctx.send(embed=self.get_server_embed(guild))

    @command(aliases=["user"])
    async def userinfo(self, ctx: Context, user: t.Optional[t.Union[Member, User]] = None) -> None:
        """
        Get information about you, or a specified member.

        `user` can be a user Mention, Name, or ID.
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
            Created: {humanize.precisedelta(datetime.datetime.utcnow() - user.created_at, suppress=["seconds", "minutes"], format="%0.0f")} ago
            Bot: {str(user.bot).replace("True", "Yes").replace("False", "No")}
            """
        )

        if isinstance(user, Member):
            member_info = []

            if user.nick:
                member_info.append(f"Nickname: {user.nick}")

            joined_time = datetime.datetime.strftime(user.joined_at, "%A %d %B %Y at %H:%M")
            member_info.append(f"Joined server: {joined_time}")

            member_info.append("")

            roles = " ".join(role.mention for role in user.roles[1:])
            member_info.append(f"Top Role: {user.top_role.mention}")

            role_order = " < ".join(roles.reverse())
            member_info.append(f"All Roles: {role_order}")
        else:
            member_info = ["No server related info, this user is not a member of this server."]

        embed.add_field(
            name="❯❯ General information",
            value=user_info,
            inline=False
        )

        embed.add_field(
            name="❯❯ Server related information",
            value="\n".join(member_info),
            inline=False
        )

        status_info = []

        if not user.activity:
            status_info.append("Activity: N/A")
        elif user.activity.type != ActivityType.custom:
            status_info.append(f"Activity: {user.activity.type.name} {user.activity.name}")
        else:
            status_info.append(f"Activity: {user.activity.name}")

        try:
            status_info.append(f"Status: {STATUSES[user.status]}")
        except KeyError:
            status_info.append("Status: N/A")

        if user.status == Status.offline:
            status_info.append("Device: :no_entry:")
        elif user.is_on_mobile():
            status_info.append("Device: Phone :iphone:")
        else:
            status_info.append("Device: PC :desktop:")

        embed.add_field(
            name="❯❯ Status information",
            value="\n".join(status_info),
            inline=True
        )

        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"ID: {user.id}")

        return embed

    def get_server_embed(self, guild: Guild) -> Embed:
        """Get the information Embed from a guild."""

        region = guild.region.name.title().replace('Vip', 'VIP').replace('_', '-').replace('Us-', 'US-')

        if guild.region == VoiceRegion.hongkong:
            region = 'Hong Kong'

        if guild.region == VoiceRegion.southafrica:
            region = 'South Africa'

        features = []
        for feature, description in self.features.items():
            if feature in guild.features:
                features.append(f'✅ {description}')
            else:
                features.append(f'❌ {description}')

        embed = Embed(
            title="Server's stats and information.",
            description=guild.description if guild.description else None,
            color=Color.gold()
        )

        embed.add_field(
            name="❯❯ General information",
            value=textwrap.dedent(
                f"""
                Name: {guild.name}
                Created on: {datetime.datetime.strftime(guild.created_at, "%A %d %B %Y at %H:%M")}
                Created At: {humanize.precisedelta(datetime.utcnow() - guild.created_at, suppress=["seconds", "minutes"], format="%0.0f")} ago\n'
                Members: {guild.member_count}
                Owner: <@!{guild.owner.id}>
                """
            ),
        )

        embed.add_field(
            name="❯❯ Boost Info",
            value=textwrap.dedent(
                f"""
                Nitro Tier: {guild.premium_tier}
                Boosters: {guild.premium_subscription_count}

                File Size: {round(guild.filesize_limit / 1048576)} MB
                Bitrate: {round(guild.bitrate_limit / 1000)} kbps

                Emoji: {guild.emoji_limit}
                Normal emoji: {sum([1 for emoji in guild.emojis if not emoji.animated])}
                Animated emoji: {sum([1 for emoji in guild.emojis if emoji.animated])}')
                """
            ),
            inline=False,
        )

        embed.add_field(
            name="❯❯ Channels",
            value=textwrap.dedent(
                f"""
                Text channels: {len(guild.text_channels)}
                Voice channels: {len(guild.voice_channels)}
                Voice region: {region}
                AFK timeout: {round(guild.afk_timeout / 60)}m | AFK channel: {None if guild.afk_channel is None else guild.afk_channel}
                """
            ),
            inline=True,
        )

        embed.set_thumbnail(url=guild.icon_url)
        embed.set_footer(text=f"Guild ID: {guild.id}")

        return embed


def setup(bot: Bot) -> None:
    """Load the Commands cog"""
    bot.add_cog(Commands(bot))
