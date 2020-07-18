import traceback

from bot.core.bot import Bot
from bot.utils.checks import is_bot_dev

from discord.ext.commands import Cog, Context, check, group


def uptime(date: str) -> str:
    days = date.days
    hours, r = divmod(date.seconds, 3600)
    minutes, seconds = divmod(r, 60)

    return f" Days: `{days}`, Hours: `{hours}`, Minutes: `{minutes}`, Seconds: `{seconds}`"


class Sudo(Cog):
    """This cog provides administrative stats about server and bot itself."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(hidden=True)
    async def sudo(self, ctx: Context) -> None:
        """Administrative information."""
        pass

    @sudo.command()
    @check(is_bot_dev)
    async def shutoff(self, ctx: Context) -> None:
        await ctx.message.add_reaction("✅")
        await self.bot.shutoff()

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
