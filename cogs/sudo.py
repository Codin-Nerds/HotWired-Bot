import datetime
import os
import platform
import textwrap
import traceback

import GPUtil

from discord import Color, Embed
from discord import __version__ as discord_version
from discord.ext.commands import Bot, Cog, Context, check, group

import psutil

from .utils import constants
from assets.checks import is_bot_dev


class Sudo(Cog):
    """This cog provides administrative stats about server and bot itself."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.process = psutil.Process()
        self.startTime = datetime.datetime.utcnow()

    @staticmethod
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
            return (
                f"{days} days, {hours} hr, {minutes} mins, and {seconds} secs"
            )
        else:
            return f"{hours} hr, {minutes} mins, and {seconds} secs"

    @group(hidden=True)
    async def sudo(self, ctx: Context) -> None:
        """Administrative information."""
        if ctx.invoked_subcommand is None:
            embed = Embed(
                description="Invalid sudo Command Passed!", color=Color.red()
            )
            await ctx.send(embed=embed)

    @sudo.command()
    async def shutoff(self, ctx: Context) -> None:
        if ctx.author.id in constants.devs:
            await ctx.message.add_reaction("✅")
            print("Shutting Down...")
            await self.bot.logout()

    @sudo.command()
    @check(is_bot_dev)
    async def load(self, ctx: Context, *, extension: str) -> None:
        """Loads a cog."""
        try:
            self.bot.load_extension(f"cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")

    @sudo.command(name="reload")
    @check(is_bot_dev)
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
    @check(is_bot_dev)
    async def restart(self, ctx: Context) -> None:
        """Restart The bot."""
        await self.bot.logout()
        os.system("python main.py")

    @sudo.command()
    async def stats(self, ctx: Context) -> None:
        """Show full bot stats."""
        ram_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        implementation = platform.python_implementation()

        general = textwrap.dedent(
            f"""
            • Servers: **{len(self.bot.guilds)}**
            • Commands: **{len(self.bot.commands)}**
            • members: **{len(set(self.bot.get_all_members()))}**
            """
        )
        process = textwrap.dedent(
            f"""
            • Memory Usage: **{ram_usage:.2f}MiB**
            • CPU Usage: **{cpu_usage:.2f}%**
            • Uptime: **{self.get_uptime()}**
            • Threads: {self.process.num_threads()}
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
        embed.add_field(name="**❯❯ Process**", value=process, inline=False)
        embed.set_author(
            name=f"{self.bot.user.name}'s Stats",
            icon_url=self.bot.user.avatar_url,
        )
        embed.set_footer(
            text=f"MIT License - {self.bot.user.name}, {datetime.datetime.utcnow().year}. Made by TheOriginalDude#0585."
        )

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
            name=f"{self.bot.user.name}'s System Data",
            icon_url=self.bot.user.avatar_url,
        )

        await ctx.send(embed=embed)

    @sudo.command(aliases=["binfo"])
    async def bootinfo(self, ctx: Context) -> None:
        """Show boot times."""
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.datetime.fromtimestamp(boot_time_timestamp)

        boot = textwrap.dedent(
            f"""
            • Boot Date: **{bt.year}/{bt.month}/{bt.day}**
            • Boot Time: **{bt.hour}:{bt.minute}:{bt.second}**
            """
        )

        embed = Embed(title="BOT BOOT INFO", color=Color.red())
        embed.add_field(name="**❯❯ Boot**", value=boot, inline=True)
        embed.set_author(
            name=f"{self.bot.user.name}'s Boot Data",
            icon_url=self.bot.user.avatar_url,
        )

        await ctx.send(embed=embed)

    @sudo.command(aliases=["cinfo"])
    async def cpuinfo(self, ctx: Context) -> None:
        """Get detailed processor info."""
        cpufreq = psutil.cpu_freq()

        cores = textwrap.dedent(
            f"""
            • Physical cores: **{psutil.cpu_count(logical=False)}**
            • Total cores: **{psutil.cpu_count(logical=True)}**
            """
        )
        frequency = textwrap.dedent(
            f"""
            • Max Frequency: **{cpufreq.max:.2f}Mhz**
            • Min Frequency: **{cpufreq.min:.2f}Mhz**
            • Current Frequency: **{cpufreq.current:.2f}Mhz**
            """
        )

        cpu_usage = "• CPU Usage Per Core:"
        for i, percentage in enumerate(
            psutil.cpu_percent(percpu=True, interval=1)
        ):
            cpu_usage += f"\n\t• Core **{i + 1}** : **{percentage}%**"

        cpu_usage += f"\n• Total CPU Usage: **{psutil.cpu_percent()}%**"

        embed = Embed(title="BOT CPU INFO", color=Color.red())
        embed.add_field(name="**❯❯ Cores**", value=cores, inline=False)
        embed.add_field(name="**❯❯ Frequency**", value=frequency, inline=False)
        embed.add_field(name="**❯❯ CPU Usage**", value=cpu_usage, inline=False)
        embed.set_author(
            name=f"{self.bot.user.name}'s CPU Info",
            icon_url=self.bot.user.avatar_url,
        )

        await ctx.send(embed=embed)

    @sudo.command(aliases=["memusg", "meminfo", "minfo", "memusage"])
    async def memoryinfo(self, ctx: Context) -> None:
        """Show detailed RAM info."""
        # get the memory details
        svmem = psutil.virtual_memory()
        # get the swap memory details (if exists)
        swap = psutil.swap_memory()

        virtual_memory = textwrap.dedent(
            f"""
            • Total: **{self.get_size(svmem.total)}**
            • Available: **{self.get_size(svmem.available)}**
            • Used: **{self.get_size(svmem.used)}**
            • Percentage: **{svmem.percent}%**
            """
        )
        swap_memory = textwrap.dedent(
            f"""
            • Total: **{self.get_size(swap.total)}**
            • Free: **{self.get_size(swap.free)}**
            • Used: **{self.get_size(swap.used)}**
            • Percentage: **{swap.percent}%**
            """
        )

        embed = Embed(title="BOT MEMORY INFO", color=Color.red())
        embed.add_field(
            name="**❯❯ Virtual Memory**", value=virtual_memory, inline=False
        )
        embed.add_field(
            name="**❯❯ Swap Memory**", value=swap_memory, inline=False
        )
        embed.set_author(
            name=f"{self.bot.user.name}'s Memory Info",
            icon_url=self.bot.user.avatar_url,
        )

        await ctx.send(embed=embed)

    @sudo.command(aliases=["dusage", "dusg", "dinfo"])
    async def diskusage(self, ctx: Context) -> None:
        """Show detailed info about disk usage."""
        embed = Embed(title="BOT DISK STATS", color=Color.red())

        partitions = []
        for partition in psutil.disk_partitions():
            diskinfo = textwrap.dedent(
                f"""
                **Device: {partition.device}**
                • Mountpoint: **{partition.mountpoint}**
                • File system type: **{partition.fstype}**
                """
            )

            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)

                diskinfo += textwrap.dedent(
                    f"""
                    **❯❯ Disk Stats:**
                        • Total Size: **{self.get_size(partition_usage.total)}**
                        • Used: **{self.get_size(partition_usage.used)}**
                        • Free: **{self.get_size(partition_usage.free)}**
                        • Percentage: **{partition_usage.percent}%**
                    """
                )
            except PermissionError:
                diskinfo += "**❯❯ Disk Stats: N/A (Insufficient Permissions)**"

            partitions.append(diskinfo)

        for ctr, partition_info in enumerate(partitions):
            embed.add_field(
                name=f"**❯❯ Partition #{ctr}**",
                value=partition_info,
                inline=False,
            )
            # TODO: Make sure False inline doesn't cause problems here

        # get IO statistics since boot
        disk_io = psutil.disk_io_counters()

        diskio_stats = textwrap.dedent(
            f"""
            • Total read: **{self.get_size(disk_io.read_bytes)}**
            • Total write: **{self.get_size(disk_io.write_bytes)}**
            """
        )

        embed.add_field(
            name="**❯❯ Disk IO Stats**", value=diskio_stats, inline=False
        )
        embed.set_author(
            name=f"{self.bot.user.name}'s Disk Info",
            icon_url=self.bot.user.avatar_url,
        )

        await ctx.send(embed=embed)

    @sudo.command()
    async def netstat(self, ctx: Context) -> None:
        """Show detailed network information.."""
        net_interfaces = ""

        # get all network interfaces (virtual and physical)
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                net_interfaces += f"\n**Interface: {interface_name}**"

                if str(address.family) == "AddressFamily.AF_INET":
                    net_interfaces += textwrap.dedent(
                        f"""
                        • IP Address: **{address.address}**
                        • Netmask: **{address.netmask}
                        • Broadcast IP: **{address.broadcast}**\n
                        """
                    )

                elif str(address.family) == "AddressFamily.AF_PACKET":
                    net_interfaces += textwrap.dedent(
                        f"""
                        • MAC Address: **{address.address}**
                        • Netmask: **{address.netmask}**
                        • Broadcast MAC: **{address.broadcast}**\n
                        """
                    )

        # get IO statistics since boot
        net_io = psutil.net_io_counters()

        netio_stats = textwrap.dedent(
            f"""
            • Total Bytes Sent: **{self.get_size(net_io.bytes_sent)}**
            • Total Bytes Received: **{self.get_size(net_io.bytes_recv)}**
            """
        )

        embed = Embed(title="BOT NET STATS", color=Color.red())
        embed.add_field(
            name="**❯❯ Net Interface Stats**",
            value=net_interfaces,
            inline=False,
        )
        embed.add_field(
            name="**❯❯ Net IO Stats**", value=netio_stats, inline=False
        )
        embed.set_author(
            name=f"{self.bot.user.name}'s Network Info",
            icon_url=self.bot.user.avatar_url,
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
                name=f"**❯❯ GPU: {gpu.name}({gpu.id})**",
                value=gpu_details,
                inline=False,
            )

        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Sudo(bot))
