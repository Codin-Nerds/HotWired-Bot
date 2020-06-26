"""MIT License

Copyright (c) 2020 Faholan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

from inspect import Parameter
from typing import Coroutine, Function, Optional

import discord
from discord.ext import commands, menus
import discord.utils

from .utils import constants

class HelpSource(menus.ListPageSource):
    def __init__(self, signature: Function, filter_commands: Coroutine, prefix: str, author: discord.User, cogs: dict) -> None:
        self.get_command_signature = signature
        self.filter_commands = filter_commands
        self.prefix = prefix
        self.menu_author = author
        super().__init__([(cog, cogs[cog]) for cog in cogs], per_page = 1)

    async def format_page(self, menu: menus.MenuPages, cog_tuple: tuple) -> discord.Embed:
        cog, commands = cog_tuple
        embed = discord.Embed(
            title=f"Help for {cog.qualified_name if cog else 'unclassified commands'}",
            description=(
                'Command syntax : `<Those arguments are required>`. `[Those aren\'t]`\n'
                f'[Everything to know about my glorious self]({constants.invite_link} "Invite link")\n'
                f'The prefix for this channel is `{self.prefix}`\n{cog.description if cog else ""}'
            ),
            colour=0xffff00,
        )
        embed.set_author(
            name=self.menu_author.display_name,
            icon_url=str(self.menu_author.avatar_url),
        )
        for command in await self.filter_commands(commands):
            embed.add_field(
                name=f"{self.prefix}{self.get_command_signature(command)}",
                value=command.help,
                inline=False,
            )
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed

class Help(commands.HelpCommand):
    def get_command_signature(self, command: commands.Command) -> str:
        basis = f"{command.qualified_name}"
        for arg in command.clean_params.values():
            if arg.kind in (Parameter.VAR_KEYWORD, Parameter.VAR_POSITIONAL):
                basis += f" [{arg.name}]"
            elif arg.annotation == Optional:
                basis += f" [{arg.name} = None]"
            elif isinstance(arg.annotation, commands.converter._Greedy):
                basis += f" [{arg.name} = (...)]"
            elif arg.default == Parameter.empty:
                basis += f" <{arg.name}>"
            else:
                basis += f" [{arg.name} = {arg.default}]"
        return basis

    async def send_bot_help(self, mapping: dict) -> None:
        ctx = self.context
        pages = menus.MenuPages(
            source = HelpSource(
                self.get_command_signature,
                self.filter_commands,
                ctx.prefix,
                ctx.author,
                sorted(mapping, key=lambda cog: cog.qualified_name if cog else "ZZ")
            ),
            clear_reactions_after=True,
        )
        await pages.start(ctx)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        ctx = self.context
        prefix = ctx.prefix
        embed = discord.Embed(
            title=cog.qualified_name,
            description=(
                f"Command syntax : `<Those arguments are required>`. `[Those aren't]`\n"
                f"The prefix for this channel is `{prefix}`\n{cog.description}"
            ),
            colour=ctx.bot.colors["blue"],
        )
        embed.set_author(name=str(ctx.message.author), icon_url=str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        for command in await self.filter_commands(cog.get_commands()):
            embed.add_field(
                name=f"{prefix}{self.get_command_signature(command)}",
                value=command.help,
                inline=False,
            )
        embed.set_footer(
            text=f"Are you interested in {cog.qualified_name} ?",
            icon_url=str(ctx.bot.user.avatar_url),
        )
        await ctx.send(embed=embed)

    async def send_command_help(self, command: commands.Command) -> None:
        ctx = self.context
        prefix = ctx.prefix
        embed = discord.Embed(
            title=f"{prefix}{self.get_command_signature(command)}",
            description=f"Command syntax : `<Those arguments are required>`. `[Those aren't]`\n{command.help}",
            colour=ctx.bot.colors["blue"],
        )
        if command.aliases:
            embed.add_field(name="Aliases :", value= "\n".join(command.aliases))
        embed.set_author(
            name=str(ctx.message.author),
            icon_url=str(ctx.message.author.avatar_url),
        )
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        if command.hidden:
            embed.set_footer(
                text=f"Wow, you found {command.name} !",
                icon_url=str(ctx.bot.user.avatar_url),
            )
        else:
            embed.set_footer(
                text=f"Are you interested in {command.name} ?",
                icon_url=str(ctx.bot.user.avatar_url),
            )
        await ctx.send(embed=embed)

    async def send_group_help(self, group: commands.Group) -> None:
        ctx = self.context
        prefix = ctx.prefix
        embed = discord.Embed(
            title = f"Help for group {prefix}{self.get_command_signature(group)}",
            description=(
                "Command syntax : `<Those arguments are required>`. `[Those aren't]`\n"
                f"{group.help}"
            ),
            colour=ctx.bot.colors["blue"],
        )
        for command in await self.filter_commands(group.commands, sort=True):
            embed.add_field(
                name=f"{prefix}{self.get_command_signature(command)}",
                value=command.help,
                inline=False,
            )
        embed.set_author(
            name=str(ctx.message.author),
            icon_url=str(ctx.message.author.avatar_url),
            )
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        if group.hidden:
            embed.set_footer(
                text=f"Wow, you found {group.name} !",
                icon_url=str(ctx.bot.user.avatar_url),
            )
        else:
            embed.set_footer(
                text=f"Are you interested in {group.name} ?",
                icon_url=str(ctx.bot.user.avatar_url),
            )
        await ctx.send(embed=embed)

def setup(bot: commands.Bot) -> None:
    bot.old_help_command = bot.help_command
    bot.help_command = Help(verify_checks = False, command_attrs = {'hidden':True})

def teardown(bot: commands.Bot) -> None:
    bot.help_command = bot.old_help_command
