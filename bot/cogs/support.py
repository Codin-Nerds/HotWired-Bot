import textwrap

from discord import Color, Embed
from discord.ext.commands import Cog, Context, command

from bot import config
from bot.core.bot import Bot


class Support(Cog):
    """Support is cool."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

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

    @command()
    async def support(self, ctx: Context) -> None:
        """Get an invite link to the bot's support server."""
        embed = Embed(
            title="Do you need support or want to give some feedback?",
            description=textwrap.dedent(
                "If you have any **problems with the bot** or "
                "if you have any **suggestions/feedback** be sure to use the support commands or join the Support Server!"
                f"\n❯❯ [Support Server]({config.discord_server})"
                f"\n❯❯ [Invite Link]({config.invite_link})"
            ),
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @command()
    async def contact(self, ctx: Context, *, message: str = "Contact Notification!") -> None:
        """Contact the developers for something important."""
        contact_channel = self.bot.get_channel(config.contact_channel)

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
    async def bug(self, ctx: Context, *, message: str = "Bug Report!") -> None:
        """Report a bug to the developers."""
        bug_report_channel = self.bot.get_channel(config.bug_report_channel)

        embed = Embed(
            title="Bug Report!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=f"{ctx.author.id} | {ctx.author.mention}"
        )
        await bug_report_channel.send(embed=embed)

    @command()
    async def support_msg(self, ctx: Context, *, message: str = "Support Required!") -> None:
        """Send a message to the support."""
        support_channel = self.bot.get_channel(config.support_channel)

        embed = Embed(
            title="Support!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=f"{ctx.author.id} | {ctx.author.mention}"
        )
        await support_channel.send(embed=embed)

        embed = Embed(
            title="Problem's still there?",
            description=textwrap.dedent(
                "If you still have **problems with the bot**"
                ", Join the Support Server now and our developers will happily help you"
                f"\n❯❯ [Support Server]({config.SUPPORT_SERVER})"
                f"\n❯❯ [Invite Link]({config.invite_link})"
            ),
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @command()
    async def suggestions(self, ctx: Context, *, message: str) -> None:
        """Give a new idea or send a suggestion to the developers."""
        suggestions_channel = self.bot.get_channel(config.suggestions_channel)

        embed = Embed(
            title="Suggestions!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=f"{ctx.author.id} | {ctx.author.mention}"
        )
        await suggestions_channel.send(embed=embed)

    @command()
    async def complaints(self, ctx: Context, *, message: str) -> None:
        """Send a complaint to the developers."""
        complaints_channel = self.bot.get_channel(config.complaints_channel)

        embed = Embed(
            title="Complaint!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=f"{ctx.author.id} | {ctx.author.mention}"
        )
        await complaints_channel.send(embed=embed)

        embed = Embed(
            title="Problem's still there?",
            description="If you still have **problems with the bot**"
            ", Join the Support Server now and our developers will happily help you!"
            f"\n❯❯ [Support Server]({config.SUPPORT_SERVER})"
            f"\n❯❯ [Invite Link]({config.invite_link})",
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Load the Support cog."""
    bot.add_cog(Support(bot))
