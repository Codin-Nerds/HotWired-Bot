from discord import Color, Embed
from discord.ext.commands import Bot, Cog, Context, command

from utils import config


class Support(Cog):
    def __init__(self, bot: Bot) -> None:
        bot.client = bot

    @command()
    async def invite(self, ctx: Context) -> None:
        """Invite link for Bot."""
        embed = Embed(
            title="Inviting me to your Server?",
            description=f"❯❯ [Invite Link]({config.invite_link})" f"\n❯❯ [Secondary Invite Link]({config.admin_invite_link})",
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @command(name="support")
    async def support(self, ctx: Context) -> None:
        """Get an invite link to the bots support server."""
        embed = Embed(
            title="Need Support? OR Want to give Feedback?",
            description="If you have any **problems with the bot** or "
            "if you have any **suggestions/feedback** be sure to join the Support Server!"
            f"❯❯ [Support Server]({config.discord_server})"
            f"❯❯ [Invite Link]({config.invite_link})",
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Support(bot))
