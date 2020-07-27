import datetime
import os
import platform
import textwrap
import time
import traceback
import typing as t

from discord import __version__ as discord_version

from bot.core.bot import Bot
from bot.config import devs

from discord import (
    Activity,
    ActivityType,
    Color,
    Embed,
    Game,
    InvalidArgument,
    Status
)
from discord.ext.commands import Cog, Context, group


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
            str = f"{days} days, {hours} hr, {minutes} mins, and {seconds} secs"
        else:
            str = f"{hours} hr, {minutes} mins, and {seconds} secs"

        return str

    @group(hidden=True)
    async def sudo(self, ctx: Context) -> None:
        """Administrative information."""
        pass

    @sudo.command()
    async def shutoff(self, ctx: Context) -> None:
        await ctx.message.add_reaction("✅")
        await self.bot.shutoff()

    @sudo.command()
    async def load(self, ctx: Context, *, extension: str) -> None:
        """Loads a cog."""
        try:
            self.bot.load_extension(f"bot.cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @sudo.command(name="reload")
    async def _reload(self, ctx: Context, *, extension: str) -> None:
        """Reloads a module."""
        try:
            self.bot.unload_extension(f"bot.cogs.{extension}")
            self.bot.load_extension(f"bot.cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @sudo.command()
    async def unload(self, ctx: Context, *, extension: str) -> None:
        """Unloads a module."""
        try:
            self.bot.unload_extension(f"bot.cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @sudo.command()
    async def restart(self, ctx: Context) -> None:
        """Restart The bot."""
        await ctx.message.add_reaction("✅")
        await self.bot.logout()
        time.sleep(2)
        os.system("pipenv run start")

    @sudo.command()
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

    async def cog_check(self, ctx: Context) -> t.Optional[bool]:
        if ctx.author.id in devs:
            return True
        else:
            embed = Embed(title="Make your Own sandwich Mortal!", color=Color.red())
            await ctx.send(embed=embed)
            return False


def setup(bot: Bot) -> None:
    bot.add_cog(Sudo(bot))
