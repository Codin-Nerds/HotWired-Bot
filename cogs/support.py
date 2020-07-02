from discord import Color, Embed
from discord.ext.commands import Bot, Cog, Context, command

from .utils import constants


class Support(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def invite(self, ctx: Context) -> None:
        """Invite link for Bot."""
        embed = Embed(
            title="Inviting me to your Server?",
            description=f"❯❯ [Invite Link]({constants.invite_link})" f"\n❯❯ [Secondary Invite Link]({constants.admin_invite_link})",
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @command()
    async def support(self, ctx: Context) -> None:
        """Get an invite link to the bots support server."""
        embed = Embed(
            title="Need Support? OR Want to give Feedback?",
            description="If you have any **problems with the bot** or "
            "if you have any **suggestions/feedback** be sure to join the Support Server!"
            f"❯❯ [Support Server]({constants.discord_server})"
            f"❯❯ [Invite Link]({constants.invite_link})",
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @command()
    async def contact(self, ctx: Context, message: str = "Contact Notification!") -> None:
        """Contact the Developers for something important."""
        contact_channel = self.bot.get_channel(constants.contact_channel)

        embed = Embed(
            title="Contact Request!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=ctx.author.id
        )
        await contact_channel.send(embed=embed)

    @command()
    async def bug(self, ctx: Context, message: str = "Bug Report!") -> None:
        """Report the developers about a Bug."""
        bug_report_channel = self.bot.get_channel(constants.bug_report_channel)

        embed = Embed(
            title="Bug Report!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=ctx.author.id
        )
        await bug_report_channel.send(embed=embed)

    @command()
    async def support_msg(self, ctx: Context, message: str = "Support Required!") -> None:
        """Send a support message to the developers."""
        support_channel = self.bot.get_channel(constants.support_channel)

        embed = Embed(
            title="Support!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=ctx.author.id
        )
        await support_channel.send(embed=embed)

    @command()
    async def suggestions(self, ctx: Context, message: str) -> None:
        """Send a new idea or suggestion to the developers."""
        suggestions_channel = self.bot.get_channel(constants.suggestions_channel)

        embed = Embed(
            title="Suggestions!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=ctx.author.id
        )
        await suggestions_channel.send(embed=embed)

    @command()
    async def complaints(self, ctx: Context, message: str) -> None:
        """Send a complaint to the developers."""
        complaints_channel = self.bot.get_channel(constants.complaints_channel)

        embed = Embed(
            title="Complaint!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=ctx.author.id
        )
        await complaints_channel.send(embed=embed)

    @command()
    async def vent(self, ctx: Context, message: str = "Duh!") -> None:
        """Send a random to the developers."""
        venting_channel = self.bot.get_channel(constants.venting_channel)

        embed = Embed(
            title="Randomness!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=ctx.author.id
        )
        await venting_channel.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Support(bot))
