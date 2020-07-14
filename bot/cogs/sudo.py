import traceback

from bot import config
from bot.core.bot import Bot
from bot.utils.checks import is_bot_dev

from discord import Color, Embed
from discord.ext.commands import Cog, Context, check, group


class Sudo(Cog):
    """This cog provides administrative stats about server and bot itself."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(hidden=True)
    async def sudo(self, ctx: Context) -> None:
        """Administrative information."""
        if ctx.invoked_subcommand is None:
            embed = Embed(
                description="Invalid sudo Command Passed!", color=Color.red()
            )
            await ctx.send(embed=embed)

    @sudo.command()
    @check(is_bot_dev)
    async def shutoff(self, ctx: Context) -> None:
        if ctx.author.id in config.devs:
            await ctx.message.add_reaction("✅")
            print("Shutting Down...")
            await self.bot.logout()

    @sudo.command(name="reload")
    @check(is_bot_dev)
    async def reload(self, ctx: Context, *, extension: str) -> None:
        """Reloads a module."""
        try:
            self.bot.unload_extension(f"cogs.{extension}")
            self.bot.load_extension(f"cogs.{extension}")
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}\n```")
        else:
            await ctx.send("\N{SQUARED OK}")


def setup(bot: Bot) -> None:
    bot.add_cog(Sudo(bot))
