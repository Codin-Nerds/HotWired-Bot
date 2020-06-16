import datetime
import os
import platform
import sys
import textwrap
import traceback
import typing as t

from discord import Color, Embed, Member
from discord.ext.commands import Bot, Cog, Context, command


class Commands(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        # TODO: Get the dev-mode from config.py
        try:
            self.dev_mode = platform.system() != "Linux" and sys.argv[1] != "-d"
        except IndexError:
            self.dev_mode = True

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

        return await ctx.send(embed=embed)

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
                f"""**Nickname:** {member.nick}
                **Joined server:** {datetime.datetime.strftime(member.joined_at, "%A %d %B %Y at %H:%M")}
                **Top role:** {member.top_role.mention}
                """
            ),
            inline=False,
        )

        embed.set_thumbnail(url=member.avatar_url_as(format="png"))
        embed.set_footer(text=f"ID: {member.id}")

        return await ctx.send(embed=embed)

    @command(aliases=["cembed", "emb", "new"])
    async def create(self, ctx: Context, *, msg: str) -> None:
        """Create an embed."""
        # TODO: This command is WIP
        await ctx.send(msg)

    @command(hidden=True)
    async def load(self, ctx: Context, *, extension: str) -> None:
        """Loads a cog."""
        # TODO: Implement is_owner check here
        try:
            self.bot.load_extension(f"cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @command(name="reload", hidden=True)
    async def _reload(self, ctx: Context, *, extension: str) -> None:
        """Reloads a module."""
        # TODO: Implement is_owner check here
        try:
            self.bot.unload_extension(f"cogs.{extension}")
            self.bot.load_extension(f"cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @command(hidden=True)
    async def restart(self, ctx: Context) -> None:
        """Restart The bot."""
        # TODO: Implement is_owner check here
        await self.bot.logout()
        os.system("python main.py")  # TODO: This might get changed


def setup(bot: Bot) -> None:
    bot.add_cog(Commands(bot))
