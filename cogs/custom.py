import asyncio
from io import BytesIO
import re
from textwrap import dedent

import discord
from discord.ext import commands


class Custom(commands.Cog):
    """Create your own commands!"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.type_name = {"user": "member", "server": "guild"}
        self.type_dict = {"member": commands.MemberConverter, "channel": commands.TextChannelConverter, "role": commands.RoleConverter, "int": int}

    async def cog_check(self, ctx: commands.Context):
        if ctx.guild:
            return True
        raise commands.NoPrivateMessage("These commands are guild only")

    @commands.group(invoke_without_command=True)
    async def custom(self, ctx: commands.Context):
        pass #  TODO : add docstring, help and everything. Maybe a link in the web interface ?

    @custom.command()
    async def create(self, ctx: commands.Context) -> None:
        """Interactively create a custom command. Check the command custom for help."""
        def check(message: discord.Message) -> bool:
            return message.author == ctx.author and message.channel == ctx.channel

        await ctx.send("What will be the command's name ?")
        try:
            name = await self.bot.wait_for("message", check=check)
            name = name.content
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply. I'm aborting this")

        if " " in name:
            return await ctx.send(":x: Well tried, but custom command names can't include spaces")

        if name in self.bot.all_commands:
            return await ctx.send(":x: Sorry, but a bot command already exists with this name")

        async with self.bot.pool.acquire() as db:
            row = await db.fetchrow("SELECT * FROM public.custom WHERE name=$1 AND guild_id=$2", name, ctx.guild.id)
            if row:
                return await ctx.send(f"A custom command named {name} already exists")

        await ctx.send(f"So the name's {name}. What about the description (enter *) to skip this")
        try:
            description = await self.bot.wait_for("message", check=check)
            description = dscription.content
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply. I'm aborting this")

        if description == "*":
            description = None

        await ctx.send(
            "What arguments will this command take (separate them with spaces) ? You can annotate them "
            "using {name}:{type}\n"
            "The types currently supported are : int, Role, Member, User, str (the default type)"
        )

        try:
            args = await self.bot.wait_for("message", check=check)
            args = args.content.split(" ")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply. I'm aborting this")

        arguments = []

        for raw_arg in args:
            if raw_arg.count(":") > 1:
                return await ctx.send(f"An argument can contain only up to 1 time `:`. This is wrong : {raw_arg}")
            if raw_arg.count(":") == 1:
                raw_name, raw_type = raw_arg.split(":")
            else:
                raw_name = raw_arg
                raw_type = "str"

            if not re.fullmatch("[A-Za-z_][A-Za-z0-9_]+", raw_name):
                return await ctx.send(f"{raw_name} isn't a valid argument name")

            raw_type = self.type_name.get(raw_type.lower(), raw_type.lower())

            if raw_type not in self.type_dict:
                raw_type = "str"

            arguments.append([raw_name, raw_type])

        await ctx.send("Okay, now what will this command return ?")
        try:
            effect = await self.bot.wait_for("message", check=check)
            effect = effect.content
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply. I'm aborting this")

        if '"""' in effect:
            return await ctx.send(':x: Sorry but """ is forbidden.')

        async with self.bot.pool.acquire() as db:
            row = await db.fetchrow("SELECT * FROM public.custom WHERE guild_id=$1 AND name=$2", ctx.guild.id, name)
            if row:
                return await ctx.send(f":x: There is already a custom command named {name}")
            await db.execute("INSERT INTO public.custom VALUES ($1, $2, $3, $4, $5, $6)", ctx.guild.id, ctx.author.id, name, description, arguments, effect)

    @commands.Cog.listener("on_message")
    async def custom_invoke(self, message: discord.Message):
        """That heck invokes the custom commands"""
        prefix = ">>" #  TODO : check the guild's custom prefix
        if not message.content.startswith(prefix) or not message.guild:
            return

        async with self.bot.db.acquire() as db:
            command = await db.fetchrow("SELECT * FROM public.custom WHERE guild_id=$1 AND name=$2", message.guild.id, message.content[len(prefix):].split(" ")[0])
            if not command:
                return

        name = command["name"]
        effect = command["effect"]
        full_args = command["arguments"]
        arguments = ", ".join([arg[0] for arg in command["arguments"]])
        arguments_format = ", ".join([f"{arg[0]}={arg[0]}" for arg in command["arguments"]])

        to_compile = textwrap.dedent(
            f'''
            async def func(message, {arguments}):
                return """{effect}""".format(author=message.author, guild=message.guild, server=message.guild, message=message.content, {arguments_format})
            '''.strip("\n")
        )

        env = {}

        try:
            exec(to_compile, env)
        except Exception:
            return

        func = env["func"]

        kwargs = {}
        args = message.content.split(" ")[1:]
        arg_n = 0

        ctx = await self.bot.get_context(message)

        try:
            for name, raw_type in full_args:
                arg = args[arg_n]
                arg_n += 1
                converter = self.type_dict.get(raw_type, str)
                if converter in (str, int):
                    kwargs[name] = converter(arg)
                else:
                    kwargs[name] = await converter().convert(ctx, arg)
        except ValueError:
            return await message.channel.send(f"Couldn't convert {arg} to int")
        except IndexError:
            return await message.channel.send("You didn't provide enough arguments")
        except commands.BadArgument:
            return await message.channel.send(f"Couldn't convert {arg} into {raw_type.capitalize()}")

        try:
            await message.channel.send(await func(message, **kwargs))
        except Exception:
            try:
                owner = self.bot.get_user(command["owner_id"]) or await self.bot.fetch_user(command["owner_id"])
                await message.channel.send(f"The custom command raised an error. Please contact {owner.mention} about that issue")
            except discord.NotFound:
                await message.channel.send("The custom command raised an error")
