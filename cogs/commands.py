import datetime
import textwrap
import typing as t
import codecs
import os
import pathlib

from discord import Color, Embed, Member
from discord.ext.commands import Bot, Cog, Context, command
from .utils import constants


class Commands(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(ignore_extra=True)
    async def code(self, ctx: Context) -> None:
        """Return Stats about bot's code."""
        total = 0
        file_amount = 0
        list_of_files = []
        for p, subdirs, files in os.walk("."):
            for name in files:
                if name.endswith(".py"):
                    file_lines = 0
                    file_amount += 1
                    with codecs.open("./" + str(pathlib.PurePath(p, name)), "r", "utf-8") as f:
                        for i, l in enumerate(f):
                            if l.strip().startswith("#") or len(l.strip()) == 0:  # skip commented lines.
                                pass
                            else:
                                total += 1
                                file_lines += 1
                    final_path = p + os.path.sep + name
                    list_of_files.append(final_path.split("." + os.path.sep)[-1] + f" : {file_lines} lines")

        embed = Embed(colour=Color.dark_orange())
        # embed.add_field(name=f"{self.bot.user.name}'s structure", value="\n".join(list_of_files))
        # embed.set_footer(text=f"I am made of {total} lines of Python, spread across {file_amount} files !")
        embed.add_field(name="**Code Data**", value=f"I am made of {total} lines of Python, spread across {file_amount} files !")
        if ctx.author.id in constants.owner_ids:
            await ctx.send("```" + "\n".join(list_of_files) + "```")
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

        return await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Commands(bot))
