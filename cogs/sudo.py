import datetime
import platform

import psutil

import discord
import GPUtil
from discord.ext import commands
from tabulate import tabulate


class Sudo(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.process = psutil.Process()
        self.startTime = datetime.datetime.utcnow()

    def getUptime(self):
        now = datetime.datetime.utcnow()
        delta = now - self.startTime
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            return f"{days} days, {hours} hr, {minutes} mins, and {seconds} secs"
        else:
            return f"{hours} hr, {minutes} mins, and {seconds} secs"

    def is_owner(ctx):
        return ctx.author.id == 688275913535914014

    @commands.group(hidden=True)
    @commands.check(is_owner)
    async def sudo(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sudo command passed...')

    @sudo.command()
    async def stats(self, ctx):
        ramUsage = self.process.memory_full_info().uss / 1024**2
        cpuUsage = self.process.cpu_percent() / psutil.cpu_count()
        implementation = platform.python_implementation()
        general = f"""
                                    • Servers: **{len(self.client.guilds)}**
                                    • Commands: **{len(self.client.commands)}**
                                    • members: **{len(set(self.client.get_all_members()))}**
                            """

        process = f"""• Memory Usage: **{ramUsage:.2f}MiB**
                                    • CPU Usage: **{cpuUsage:.2f}%**
                                    • Uptime: **{self.getUptime()}**
                                    • Threads: {self.process.num_threads()}
                            """
        system = f"""• Python: **{platform.python_version()} with {implementation}**
                                • discord.py: **{discord.__version__}**
                            """

        embed = discord.Embed(title="BOT STATISTICS", color=discord.Color.red())

        embed.add_field(name="**❯❯ General**", value=general, inline=True)
        embed.add_field(name="**❯❯ System**", value=system, inline=True)
        embed.add_field(name="**❯❯ Process**", value=process, inline=False)

        embed.set_author(name=f"{self.client.user.name}'s Stats", icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"MIT License - {self.client.user.name}, {datetime.datetime.utcnow().year}. Made by TheOriginalDude#0585.")

        await ctx.send(embed=embed)

    @sudo.command(aliases=['sinfo'])
    async def sysinfo(self, ctx):
        uname = platform.uname()

        system = f"""
                                    • System: **{uname.system}**
                                    • Node Name: **{uname.node}**
                            """

        version = f"""• Release: **{uname.release}**
                                    • Version: **{uname.version}**
                            """
        hardware = f"""
                                • Machine: **{uname.machine}**
                                • Processor: **{uname.processor}**
                            """

        embed = discord.Embed(title="BOT SYSTEM INFO", color=discord.Color.red())

        embed.add_field(name="**❯❯ System**", value=system, inline=True)
        embed.add_field(name="**❯❯ Hardware**", value=hardware, inline=True)
        embed.add_field(name="**❯❯ Version**", value=version, inline=False)

        embed.set_author(name=f"{self.client.user.name}'s System Data", icon_url=self.client.user.avatar_url)

        await ctx.send(embed=embed)

    @sudo.command(aliases=['binfo'])
    async def bootinfo(self, ctx):
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.datetime.fromtimestamp(boot_time_timestamp)

        boot = f"""
                                • Boot Date: **{bt.year}/{bt.month}/{bt.day}**
                                • Boot Time: **{bt.hour}:{bt.minute}:{bt.second}**
                            """

        embed = discord.Embed(title="BOT BOOT INFO", color=discord.Color.red())

        embed.add_field(name="**❯❯ Boot**", value=boot, inline=True)

        embed.set_author(name=f"{self.client.user.name}'s Boot Data", icon_url=self.client.user.avatar_url)

        await ctx.send(embed=embed)

    @sudo.command(aliases=['cinfo'])
    async def cpuinfo(self, ctx):
        cpufreq = psutil.cpu_freq()

        cores = f"""
        • Physical cores: **{psutil.cpu_count(logical=False)}**
        • Total cores: **{psutil.cpu_count(logical=True)}**
        """

        frequency = f"""
        • Max Frequency: **{cpufreq.max:.2f}Mhz**
        • Min Frequency: **{cpufreq.min:.2f}Mhz**
        • Current Frequency: **{cpufreq.current:.2f}Mhz**
        """

        cpu_usage = "• CPU Usage Per Core:"

        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            cpu_usage += f"\n\t• Core **{i + 1}** : **{percentage}%**"

        cpu_usage += f"\n• Total CPU Usage: **{psutil.cpu_percent()}%**"

        embed = discord.Embed(title="BOT CPU INFO", color=discord.Color.red())

        embed.add_field(name="**❯❯ Cores**", value=cores, inline=False)
        embed.add_field(name="**❯❯ Frequency**", value=frequency, inline=False)
        embed.add_field(name="**❯❯ CPU Usage**", value=cpu_usage, inline=False)

        embed.set_author(name=f"{self.client.user.name}'s CPU Info", icon_url=self.client.user.avatar_url)

        await ctx.send(embed=embed)

    @sudo.command(aliases=['memusg', 'meminfo', 'minfo', 'memusage'])
    async def memoryinfo(self, ctx):

        def get_size(bytes, suffix="B"):
            factor = 1024
            for unit in ["", "K", "M", "G", "T", "P"]:
                if bytes < factor:
                    return f"{bytes:.2f}{unit}{suffix}"
                bytes /= factor

        # get the memory details
        svmem = psutil.virtual_memory()

        # get the swap memory details (if exists)
        swap = psutil.swap_memory()

        virtual_memory = f"""
        • Total: **{get_size(svmem.total)}**
        • Available: **{get_size(svmem.available)}**
        • Used: **{get_size(svmem.used)}**
        • Percentage: **{svmem.percent}%**
        """
        swap_memory = f"""
        • Total: **{get_size(swap.total)}**
        • Free: **{get_size(swap.free)}**
        • Used: **{get_size(swap.used)}**
        • Percentage: **{swap.percent}%**
        """

        embed = discord.Embed(title="BOT MEMORY INFO", color=discord.Color.red())

        embed.add_field(name="**❯❯ Virtual Memory**", value=virtual_memory, inline=False)
        embed.add_field(name="**❯❯ Swap Memory**", value=swap_memory, inline=False)

        embed.set_author(name=f"{self.client.user.name}'s Memory Info", icon_url=self.client.user.avatar_url)

        await ctx.send(embed=embed)

    @sudo.command(aliases=['dusage', 'dusg', 'dinfo'])
    async def diskusage(self, ctx):

        def get_size(bytes, suffix="B"):
            factor = 1024
            for unit in ["", "K", "M", "G", "T", "P"]:
                if bytes < factor:
                    return f"{bytes:.2f}{unit}{suffix}"
                bytes /= factor

        ctr = 1
        # get all disk partitions
        partitions = psutil.disk_partitions()
        for partition in partitions:
            embed = discord.Embed(title="BOT DISK STATS", color=discord.Color.red())
            diskinfo = f"**Partitions and Usage #{ctr}:**"
            diskinfo += f"\n**Device: {partition.device}**"
            diskinfo += f"\n• Mountpoint: **{partition.mountpoint}**"
            diskinfo += f"\n• File system type: **{partition.fstype}**"

            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)

            except PermissionError:
                continue

            diskinfo += f"\n• Total Size: **{get_size(partition_usage.total)}**"
            diskinfo += f"\n• Used: **{get_size(partition_usage.used)}**"
            diskinfo += f"\n• Free: **{get_size(partition_usage.free)}**"
            diskinfo += f"\n• Percentage: **{partition_usage.percent}%**"

            embed.add_field(name="**❯❯ Disk Stats**", value=diskinfo, inline=False)

            ctr += 1
            await ctx.send(embed=embed)

        # get IO statistics since boot
        disk_io = psutil.disk_io_counters()

        diskio_stats = f"""
            • Total read: **{get_size(disk_io.read_bytes)}**
            • Total write: **{get_size(disk_io.write_bytes)}**
        """

        embed = discord.Embed(title="BOT DISK IO STATS", color=discord.Color.red())

        embed.add_field(name="**❯❯ Disk IO Stats**", value=diskio_stats, inline=False)

        embed.set_author(name=f"{self.client.user.name}'s Disk Info", icon_url=self.client.user.avatar_url)

        await ctx.send(embed=embed)

    @sudo.command()
    async def netstat(self, ctx):

        def get_size(bytes, suffix="B"):
            factor = 1024
            for unit in ["", "K", "M", "G", "T", "P"]:
                if bytes < factor:
                    return f"{bytes:.2f}{unit}{suffix}"
                bytes /= factor

        net_interfaces = ""

        # get all network interfaces (virtual and physical)
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                net_interfaces += f"\n**Interface: {interface_name}**"

                if str(address.family) == 'AddressFamily.AF_INET':
                    net_interfaces += f"\n• IP Address: **{address.address}**"
                    net_interfaces += f"\n• Netmask: **{address.netmask}"
                    net_interfaces += f"\n• Broadcast IP: **{address.broadcast}**\n"

                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    net_interfaces += f"\n• MAC Address: **{address.address}**"
                    net_interfaces += f"\n• Netmask: **{address.netmask}**"
                    net_interfaces += f"\n• Broadcast MAC: **{address.broadcast}**\n"

        # get IO statistics since boot
        net_io = psutil.net_io_counters()

        netio_stats = f"""
            • Total Bytes Sent: **{get_size(net_io.bytes_sent)}**
            • Total Bytes Received: **{get_size(net_io.bytes_recv)}**
        """

        embed = discord.Embed(title="BOT NET STATS", color=discord.Color.red())

        embed.add_field(name="**❯❯ Net Interface Stats**", value=net_interfaces, inline=False)
        embed.add_field(name="**❯❯ Net IO Stats**", value=netio_stats, inline=False)

        embed.set_author(name=f"{self.client.user.name}'s Network Info", icon_url=self.client.user.avatar_url)

        await ctx.send(embed=embed)

    @sudo.command()
    async def gpuinfo(self, ctx):

        await ctx.send("**" + "="*15 + "GPU Details" + "="*15 + "**")
        gpus = GPUtil.getGPUs()

        list_gpus = []

        for gpu in gpus:
            # get the GPU id
            gpu_id = gpu.id

            # name of GPU
            gpu_name = f"({gpu_id}){gpu.name}"

            # get % percentage of GPU usage of that GPU
            gpu_load = f"{gpu.load*100}%"

            # get free memory in MB format
            gpu_free_memory = f"{gpu.memoryFree}MB"

            # get used memory
            gpu_used_memory = f"{gpu.memoryUsed}MB"

            # get total memory
            gpu_total_memory = f"{gpu.memoryTotal}MB"

            # get GPU temperature in Celsius
            gpu_temperature = f"{gpu.temperature} °C"

            gpu_uuid = gpu.uuid
            list_gpus.append((
                    gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
                    gpu_total_memory, gpu_temperature, gpu_uuid
            ))

        await ctx.send(tabulate(list_gpus, headers=("name", "load", "free memory", "used memory", "total memory","temperature", "uuid")))

        await ctx.send("**" + "="*41 + "**")


def setup(client):
    client.add_cog(Sudo(client))
