import datetime
import platform
import textwrap
import math
import typing as t
import traceback
import os
import copy
import humanize
import time

import GPUtil
from discord import Color, Embed, InvalidArgument, Activity, ActivityType, Game, Status, User, Member
from discord import __version__ as discord_version
from discord.ext.commands import Bot, Cog, Context, check, group

from .utils import constants


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

    def get_size(_bytes: int, suffix: str = "B") -> str:
        """Convert sizes."""
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if _bytes < factor:
                return f"{_bytes:.2f}{unit}{suffix}"

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

    @group(hidden=True)
    async def sudo(self, ctx: Context) -> None:
        """Administrative information."""
        pass

    async def is_owner(ctx: Context) -> t.Union[bool, None]:
        if ctx.author.id in constants.devs:
            return True
        else:
            embed = Embed(description="Learn to make your own sandwich Mortal!", color=Color.red())
            await ctx.send(embed=embed)

    @sudo.command()
    @check(is_owner)
    async def shutoff(self, ctx: Context) -> None:
        if ctx.author.id in constants.devs:
            await ctx.message.add_reaction("✅")
            print("Shutting Down!")
            await self.bot.logout()

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
        os.system("pipenv run start main.py")

    @sudo.command()
    @check(is_owner)
    async def createinv(self, ctx, channelid: int) -> None:
        channel = self.bot.get_channel(channelid)
        InviteURL = await channel.create_invite(max_uses=1)
        await ctx.send(InviteURL)

    @group(hidden=True)
    async def botstatus(self, ctx: Context) -> None:
        """
        Change the status of the bot

        `botstatus playing <new status>` - Change playing status
        `botstatus watching <new status>` - Change watching status
        `botstatus listening <new status>` - Change listening status
        """
        if ctx.invoked_subcommand is None:
            pass

    @botstatus.command()
    @check(is_owner)
    async def playing(self, ctx: Context, *, playing: str) -> None:
        """Change playing status."""
        try:
            await self.bot.change_presence(
                activity=Game(type=0, name=playing),
                status=Status.online
            )
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @botstatus.command()
    @check(is_owner)
    async def listening(self, ctx: Context, *, listening: str) -> None:
        """Change listening status."""
        try:
            await self.bot.change_presence(
                activity=Activity(
                    type=ActivityType.listening,
                    name=listening
                )
            )
            await ctx.send(f"Successfully changed listening status to **{listening}**")
        except InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @botstatus.command()
    @check(is_owner)
    async def watching(self, ctx: Context, *, watching: str) -> None:
        """Change watching status."""
        try:
            await self.bot.change_presence(
                activity=Activity(
                    type=ActivityType.watching,
                    name=watching
                )
            )
            await ctx.send(f"Successfully changed watching status to **{watching}**")
        except InvalidArgument as err:
            await ctx.send(err)
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

    @sudo.command(aliases=["sinfo"])
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

    @sudo.command()
    async def gpuinfo(self, ctx: Context) -> None:
        """Get detailed GPU info."""
        embed = Embed(title="BOT GPU INFO", color=Color.red())

        for gpu in GPUtil.getGPUs():
            gpu_details = textwrap.dedent(
                f"""
                • Load: {gpu.load*100}%
                • Temperature: {gpu.temperature} °C

                • Free Memory: {gpu.memoryFree}MB
                • Used Memory: {gpu.memoryUsed}MB
                • Total Memory: {gpu.memoryTotal}MB

                • UUID: {gpu.uuid}
                """
            )
            embed.add_field(
                name=f"**❯❯ GPU: {gpu.name}({gpu.id})**", value=gpu_details, inline=False,
            )

        await ctx.send(embed=embed)

    @sudo.command()
    @check(is_owner)
    async def cmduser(self, ctx: Context, user: t.Union[Member, User], *, command: str) -> None:
        """Run a command as another user."""
        msg = copy.copy(ctx.message)
        msg.author = user
        msg.content = ctx.prefix + command

        new_ctx = await self.bot.get_context(msg)
        await self.bot.invoke(new_ctx)

    @sudo.command()
    @check(is_owner)
    async def install(self, ctx: Context, package: str) -> None:
        "Install a package"
        async with ctx.typing():
            os.system(f"pip install {package}")
        await ctx.message.add_reaction("✅")

        await ctx.send(f"Installed {package}!")

    @sudo.command()
    @check(is_owner)
    async def update(self, ctx: Context, package: str) -> None:
        "Update a package"
        async with ctx.typing():
            os.system(f"pip install --upgraded {package}")
        await ctx.message.add_reaction("✅")

        await ctx.send(f"Updated {package}!")

    @sudo.command(aliases=['slist', 'serverlist'])
    async def guildlist(self, ctx: Context, page: int = 1) -> None:
        """List the guilds I am in."""
        guild_list = []

        for guild in self.bot.guilds:
            guild_list.append(guild)

        guild_count = len(self.bot.guilds)
        items_per_page = 10
        pages = math.ceil(guild_count / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        guilds_list = ''
        for guild in guild_list[start:end]:
            guilds_list += f'**{guild.name}** ({guild.id})\n**Joined:** {humanize.naturaltime(guild.get_member(self.bot.user.id).joined_at)}\n>'
            guilds_list += "=====================================\n"

        embed = Embed(color=Color.greyple(), title="Total Guilds", description=guilds_list)
        embed.set_footer(text=f"Currently showing: {page} out of {pages}")

        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Sudo(bot))
