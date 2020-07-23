from discord.ext.commands import Cog, Context

from bot.core.bot import Bot
from bot.utils.sqlitefunc import enable_banlock, enable_kicklock, disable_banlock, disable_kicklock


class Lock(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def banlock(self, ctx: Context) -> None:
        """Enable locking to Ban all the new members joining the guild."""
        enable_banlock(ctx.guild.id)

        await ctx.send("Banlock successfully Enabled")

    def banunlock(self, ctx: Context) -> None:
        """Disable locking to Ban all the new members joining the guild."""
        disable_banlock(ctx.guild.id)

        await ctx.send("Banlock successfully Disabled")

    def kicklock(self, ctx: Context) -> None:
        """Enable locking to Kick all the new members joining the guild."""
        enable_kicklock(ctx.guild.id)

        await ctx.send("Kicklock successfully Enabled")

    def kickunlock(self, ctx: Context) -> None:
        """Disable locking to Kick all the new members joining the guild."""
        disable_kicklock(ctx.guild.id)

        await ctx.send("Kicklock successfully DIsabled")


def setup(bot: Bot) -> None:
    bot.add_cog(Lock(bot))
