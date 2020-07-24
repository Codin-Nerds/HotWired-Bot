import textwrap

from discord import Color, Embed
from discord.ext.commands import Cog, Context, command

from bot.core.bot import Bot


class Support(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def invite(self, ctx: Context) -> None:
        """Invite link for Bot."""
        embed = Embed(
            title="Inviting me to your Server?",
            description=f"❯❯ [Invite Link]({self.bot.invite_link})" f"\n❯❯ [Secondary Invite Link]({self.bot.admin_invite_link})",
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @command()
    async def support(self, ctx: Context) -> None:
        """Get an invite link to the bots support server."""
        embed = Embed(
            title="Need Support? OR Want to give Feedback?",
            description=textwrap.dedent(
                "If you have any **problems with the bot** or "
                "if you have any **suggestions/feedback** be sure to use the support commands or join the Support Server!"
                f"\n❯❯ [Support Server]({self.bot.discord_server})"
                f"\n❯❯ [Invite Link]({self.bot.invite_link})"
            ),
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @command()
    async def contact(self, ctx: Context, *, message: str = "Contact Notification!") -> None:
        """Contact the Developers for something important."""
        embed = Embed(
            title="Contact Request!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=ctx.author.id
        )
        await self.bot.contact_channel.send(embed=embed)

    @command()
    async def bug(self, ctx: Context, *, message: str = "Bug Report!") -> None:
        """Report the developers about a Bug."""
        bug_report_channel = self.bot.get_channel(self.bot.bug_report_channel)

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
        """Send a support message to the developers."""
        embed = Embed(
            title="Support!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=f"{ctx.author.id} | {ctx.author.mention}"
        )
        await self.bot.support_channel.send(embed=embed)

        embed = Embed(
            title="Problem's still there?",
            description=textwrap.dedent(
                "If you still have **problems with the bot**"
                ", Join the Support Server now and our developers will happily help you"
                f"\n❯❯ [Support Server]({self.bot.SUPPORT_SERVER})"
                f"\n❯❯ [Invite Link]({self.bot.invite_link})"
            ),
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @command()
    async def suggestions(self, ctx: Context, *, message: str) -> None:
        """Send a new idea or suggestion to the developers."""
        embed = Embed(
            title="Suggestions!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=f"{ctx.author.id} | {ctx.author.mention}"
        )
        await self.bot.suggestions_channel.send(embed=embed)

    @command()
    async def complaints(self, ctx: Context, *, message: str) -> None:
        """Send a complaint to the developers."""
        embed = Embed(
            title="Complaint!",
            description=message,
            color=Color.dark_blue()
        )
        embed.add_field(
            name="Author",
            value=f"{ctx.author.id} | {ctx.author.mention}"
        )
        await self.bot.complaints_channel.send(embed=embed)

        embed = Embed(
            title="Problem's still there?",
            description="If you still have **problems with the bot**"
            ", Join the Support Server now and our developers will happily help you!"
            f"\n❯❯ [Support Server]({self.bot.SUPPORT_SERVER})"
            f"\n❯❯ [Invite Link]({self.bot.invite_link})",
            color=Color.dark_green(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Support(bot))
