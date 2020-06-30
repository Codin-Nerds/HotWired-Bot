"""Help system.

This help is nearly perfect, with only one warning (access to a protected
class) and two info (not enough methods at line 16 and too many arguments at
line 19), under Flake8, Mypy, Pydocstyle and Pylint.
"""

from inspect import Parameter
from typing import Optional

import discord
from discord.ext import commands, menus
import discord.utils


class HelpSource(menus.ListPageSource):
    """The Help menu."""

    def __init__(
            self,
            signature,
            filter_commands,
            prefix,
            author,
            bot_id,
            perms,
            cogs):
        """Create the menu."""
        self.get_command_signature = signature
        self.filter_commands = filter_commands
        self.prefix = prefix
        self.menu_author = author
        self.bot_id = bot_id
        self.bot_perms = perms
        super().__init__(
            [(cog, cogs[cog]) for cog in sorted(
                cogs,
                key=lambda cog: cog.qualified_name if cog else "ZZ"
            )],
            per_page=1,
        )

    async def format_page(self, menu, cog_tuple):
        """Format the pages."""
        cog, command_list = cog_tuple
        link = discord.utils.oauth_url(
            str(self.bot_id),
            permissions=discord.Permissions(self.bot_perms),
        )
        embed = discord.Embed(
            title=(
                "Help for "
                f"{cog.qualified_name if cog else 'unclassified commands'}"
            ),
            description=(
                "Command syntax : `<Those arguments are required>`. `"
                '[Those aren\'t]`\n[Everything to know about my glorious self]'
                f'({link} "Invite link")'
                f"\nThe prefix for this channel is `{self.prefix}`\n"
                f"{cog.description if cog else ''}"
            ),
            color=0xffff00,
        )
        embed.set_author(
            name=self.menu_author.display_name,
            icon_url=str(self.menu_author.avatar_url),
        )
        for command in await self.filter_commands(command_list):
            embed.add_field(
                name=f"{self.prefix}{self.get_command_signature(command)}",
                value=command.help,
                inline=False,
            )
        embed.set_footer(
            text=f"Page {menu.current_page+1}/{self.get_max_pages()}"
        )
        return embed


class Help(commands.HelpCommand):
    """The Help cog."""

    def get_command_signature(self, command: commands.Command) -> str:
        """Retrieve the command's signature."""
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
        """Send the global help."""
        ctx = self.context
        pages = menus.MenuPages(
            source=HelpSource(
                self.get_command_signature,
                self.filter_commands,
                ctx.prefix,
                ctx.author,
                ctx.bot.user.id,
                ctx.bot.invite_permissions,
                mapping),
            clear_reactions_after=True,
        )
        await pages.start(ctx)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        """Send help for a cog."""
        ctx = self.context
        prefix = discord.utils.escape_markdown(
            await ctx.bot.get_m_prefix(ctx.message, False),
        )
        embed = discord.Embed(
            title=cog.qualified_name,
            description=(
                "Command syntax : `<Those arguments are required>`. "
                f"`[Those aren't]`\nThe prefix for this channel is `{prefix}`"
                f"\n{cog.description}"
            ),
            colour=ctx.bot.colors["blue"],
        )
        embed.set_author(
            name=str(ctx.message.author),
            icon_url=str(ctx.message.author.avatar_url),
        )
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
        """Send help for a command."""
        ctx = self.context
        prefix = discord.utils.escape_markdown(
            await ctx.bot.get_m_prefix(ctx.message, False),
        )
        embed = discord.Embed(
            title=f"{prefix}{self.get_command_signature(command)}",
            description=(
                "Command syntax : `<Those arguments are required>`. "
                f"`[Those aren't]`\n{command.help}"
            ),
            colour=ctx.bot.colors["blue"],
        )
        if command.aliases:
            embed.add_field(name="Aliases :", value="\n".join(command.aliases))
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
        """Send help for a group."""
        ctx = self.context
        prefix = discord.utils.escape_markdown(
            await ctx.bot.get_m_prefix(ctx.message, False),
        )
        embed = discord.Embed(
            title=(
                f"Help for group {prefix}"
                f"{self.get_command_signature(group)}"
            ),
            description=(
                "Command syntax : `<Those arguments are required>`. "
                f"`[Those aren't]`\n{group.help}"
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

    async def send_error_message(self, error: str) -> None:
        """Send an error message."""
        ctx = self.context
        await ctx.bot.httpcat(ctx, 404, error)


def setup(bot: commands.Bot) -> None:
    """Add the help command."""
    bot.old_help_command = bot.help_command
    bot.help_command = Help(
        verify_checks=False,
        command_attrs={'hidden': True},
    )


def teardown(bot: commands.Bot) -> None:
    """Remove the help command."""
    bot.help_command = bot.old_help_command
