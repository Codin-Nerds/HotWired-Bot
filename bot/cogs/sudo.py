import datetime
import os
import platform
import textwrap
import time
import traceback
import typing as t

from discord import (Activity, ActivityType, Color, Embed, Game,
                     InvalidArgument, Status)
from discord import __version__ as discord_version
from discord.ext.commands import Cog, Context, check, group

from bot.core.bot import Bot
from bot.config import devs


def uptime(date: str) -> str:
    days = date.days
    hours, r = divmod(date.seconds, 3600)
    minutes, seconds = divmod(r, 60)

    return f" Days: `{days}`, Hours: `{hours}`, Minutes: `{minutes}`, Seconds: `{seconds}`"


class Sudo(Cog):
    """This cog provides administrative stats about server and bot itself."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    def get_uptime(self) -> str:
        """Get formatted server uptime."""
        now = datetime.datetime.utcnow()
        delta = now - self.startTime
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            return f"{days} days, {hours} hr, {minutes} mins, and {seconds} secs"
        else:
            return f"{hours} hr, {minutes} mins, and {seconds} secs"

    @staticmethod
    async def is_owner(ctx: Context) -> t.Union[bool, None]:
        if ctx.author.id in devs:
            return True
        else:
            embed = Embed(description="This is an owner-only command, you cannot invoke this.", color=Color.red())
            await ctx.send(embed=embed)

    @group(hidden=True)
    @check(is_owner)
    async def sudo(self, ctx: Context) -> None:
        """Administrative information."""
        pass

    @sudo.command()
    @check(is_owner)
    async def shutoff(self, ctx: Context) -> None:
        await ctx.message.add_reaction("✅")
        await self.bot.shutoff()

    @sudo.command()
    @check(is_owner)
    async def load(self, ctx: Context, *, extension: str) -> None:
        """Loads a cog."""
        try:
            self.bot.load_extension(f"cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @sudo.command(name="reload")
    @check(is_owner)
    async def _reload(self, ctx: Context, *, extension: str) -> None:
        """Reloads a module."""
        try:
            self.bot.unload_extension(f"cogs.{extension}")
            self.bot.load_extension(f"cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @sudo.command()
    @check(is_owner)
    async def unload(self, ctx: Context, *, extension: str) -> None:
        """Unloads a module."""
        try:
            self.bot.unload_extension(f"cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @sudo.command()
    @check(is_owner)
    async def restart(self, ctx: Context) -> None:
        """Restart The bot."""
        await ctx.message.add_reaction("✅")
        await self.bot.logout()
        time.sleep(2)
        os.system("pipenv run start")
        # os.system("python3.8 -m pipenv run start")

    @sudo.command()
    @check(is_owner)
    async def botstatus(self, ctx: Context, status: str, status_info: t.Literal["playing", "watching", "listening"]) -> None:
        """
        Change the status of the bot
        `botstatus playing <new status>` - Change playing status
        `botstatus watching <new status>` - Change watching status
        `botstatus listening <new status>` - Change listening status
        """
        statuses = ["playing", "watching", "listening"]
        if status.lower() not in statuses:
            await ctx.send("Invalid status type!")

        if status.lower() == "playing":
            try:
                await self.bot.change_presence(
                    activity=Game(type=0, name=status_info),
                    status=Status.online
                )
                await ctx.send(f"Successfully changed playing status to **{status_info}**")
            except InvalidArgument as e:
                await ctx.send(e)
            except Exception as e:
                await ctx.send(e)

        elif status.lower() == "watching":
            try:
                await self.bot.change_presence(
                    activity=Activity(
                        type=ActivityType.watching,
                        name=status_info
                    )
                )
                await ctx.send(f"Successfully changed watching status to **{status_info}**")
            except InvalidArgument as e:
                await ctx.send(e)
            except Exception as e:
                await ctx.send(e)

        elif status.lower() == "listening":
            try:
                await self.bot.change_presence(
                    activity=Activity(
                        type=ActivityType.listening,
                        name=status_info
                    )
                )
                await ctx.send(f"Successfully changed listening status to **{status_info}**")
            except InvalidArgument as e:
                await ctx.send(e)
            except Exception as e:
                await ctx.send(e)

    @sudo.command()
    @check(is_owner)
    async def stats(self, ctx: Context) -> None:
        """Show full bot stats."""
        implementation = platform.python_implementation()

        general = textwrap.dedent(
            f"""
            • Servers: **{len(self.bot.guilds)}**
            • Commands: **{len(self.bot.commands)}**
            • members: **{len(set(self.bot.get_all_members()))}**
            • Uptime: **{uptime(datetime.datetime.now() - self.start_time)}**
            """
        )
        system = textwrap.dedent(
            f"""
            • Python: **{platform.python_version()} with {implementation}**
            • discord.py: **{discord_version}**
            """
        )

        embed = Embed(title="BOT STATISTICS", color=Color.red())
        embed.add_field(name="**❯❯ General**", value=general, inline=True)
        embed.add_field(name="**❯❯ System**", value=system, inline=True)
        embed.set_author(name=f"{self.bot.user.name}'s Stats", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="Made by The-Codin-Hole Team.")

        await ctx.send(embed=embed)

    @sudo.command(aliases=["sinfo"])
    @check(is_owner)
    async def sysinfo(self, ctx: Context) -> None:
        """Get system information (show info about the server this bot runs on)."""
        uname = platform.uname()

        system = textwrap.dedent(
            f"""
            • System: **{uname.system}**
            • Node Name: **{uname.node}**
            """
        )
        version = textwrap.dedent(
            f"""
            • Release: **{uname.release}**
            • Version: **{uname.version}**
            """
        )
        hardware = textwrap.dedent(
            f"""
            • Machine: **{uname.machine}**
            • Processor: **{uname.processor}**
            """
        )

        embed = Embed(title="BOT SYSTEM INFO", color=Color.red())
        embed.add_field(name="**❯❯ System**", value=system, inline=True)
        embed.add_field(name="**❯❯ Hardware**", value=hardware, inline=True)
        embed.add_field(name="**❯❯ Version**", value=version, inline=False)
        embed.set_author(
            name=f"{self.bot.user.name}'s System Data", icon_url=self.bot.user.avatar_url,
        )

        await ctx.send(embed=embed)

    """
    Command below is temporarily disabled as it carries code
    that does not work.
    It is to be solved in #61
    """
    # @sudo.command(aliases=['slist', 'serverlist'])
    # @check(is_owner)
    # async def guildlist(self, ctx: Context, page: int = 1) -> None:
    #     """List the guilds I am in."""
    #     guild_list = []

    #     for guild in self.bot.guilds:
    #         guild_list.append(guild)

    #     guild_count = len(self.bot.guilds)
    #     items_per_page = 10
    #     pages = math.ceil(guild_count / items_per_page)

    #     start = (page - 1) * items_per_page
    #     end = start + items_per_page

    #     guilds_list = ''
    #     for guild in guild_list[start:end]:
    #         guilds_list += f'**{guild.name}** ({guild.id})\n**Joined:** {humanize.naturaltime(guild.get_member(self.bot.user.id).joined_at)}\n>'
    #         guilds_list += "=====================================\n"

    #     embed = Embed(color=Color.greyple(), title="Total Guilds", description=guilds_list)
    #     embed.set_footer(text=f"Currently showing: {page} out of {pages}")

    #     await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Sudo(bot))
