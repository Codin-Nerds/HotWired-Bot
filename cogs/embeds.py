import typing as t
from collections import defaultdict

from discord import Embed, Member
from discord.ext import Bot
from discord.ext.commands import Cog, ColourConverter, Context, group


class Embeds(Cog):
    """A Cog which provides the ability to build a custom embed."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        # Provide an empty embed for every member (key)
        self.embeds = defaultdict(lambda: Embed())

    @group(invoke_without_command=True, name='embed', aliases=['embedset'])
    async def embed_group(self, ctx: Context) -> None:
        """Commands for configuring the Embed messages."""
        ctx.send("This command is not meant to be used on its own!")

    @embed_group.command(aliases=['set_title'])
    async def title(self, ctx: Context, *, title: str) -> None:
        """Set Title for the Embed."""
        self.embeds[ctx.author].title = title
        await ctx.send("Embeds title updated.")

    @embed_group.command(aliases=['set_description'])
    async def description(self, ctx: Context, *, description: str) -> None:
        """Set Description for the Embed."""
        self.embeds[ctx.author].description = description
        await ctx.send("Embeds description updated.")

    @embed_group.command(aliases=['add_description'])
    async def append_description(self, ctx: Context, *, description: str) -> None:
        """Add text into Description of the Embed."""
        self.embeds[ctx.author].description += description
        await ctx.send("Embeds description appended.")

    @embed_group.command(aliases=['set_footer'])
    async def footer(self, ctx: Context, *, footer: str) -> None:
        """Set Footer for the Embed."""
        self.embeds[ctx.author].set_footer(text=footer)
        await ctx.send("Embeds footer updated.")

    @embed_group.command(aliases=['set_image'])
    async def image(self, ctx: Context, url: str) -> None:
        """Set image for the Embed."""
        self.embeds[ctx.author].set_image(url=url)
        await ctx.send("Embeds image updated.")

    @embed_group.command(aliases=['set_color'])
    async def color(self, ctx: Context, color: ColourConverter) -> None:
        """
        Set color for the Embed.

        `color` can be HEX color code or some of the standard colors (red, blue, ...).
        """
        self.embeds[ctx.author].colour = color
        await ctx.send("Embeds color updated.")

    @embed_group.command(aliases=['authorname', 'set_author', 'set_authorname'])
    async def author(self, ctx: Context, author_name: str) -> None:
        """Set authors name for the Embed."""
        self.embeds[ctx.author].set_author(
            name=author_name,
            url=self.embeds[ctx.author].author.url,
            icon_url=self.embeds[ctx.author].author.icon_url
        )
        await ctx.send("Embeds author updated.")

    @embed_group.command(aliases=['set_author_url', 'authorurl', 'set_authorurl'])
    async def author_url(self, ctx: Context, author_url: str) -> None:
        """Set authors URL for Embed."""
        self.embeds[ctx.author].set_url(
            name=self.embeds[ctx.author].author.name,
            url=author_url,
            icon_url=self.embeds[ctx.author].author.icon_url
        )
        await ctx.send("Embeds author URL updated.")

    @embed_group.command()
    async def author_icon(self, ctx: Context, author_icon: t.Union[Member, str]) -> None:
        """
        Set authors icon in the Embed.

        `author_icon` can either be URL to the image or you can mention a user to get his avatar
        """
        if not isinstance(author_icon, str):
            author_icon = author_icon.avatar_url_as(format="png")

        self.embeds[ctx.author].set_author(
            name=self.embeds[ctx.author].author.name,
            url=self.embeds[ctx.author].author.url,
            icon_url=author_icon
        )

    def cog_check(self, ctx: Context) -> bool:
        """
        Only allow users with manage messages permission to invoke commands in this cog.

        This is needed because Embeds can be much longer in comparison to regular messages,
        therefore it would be very easy to spam things and clutter the chat.
        """
        return ctx.author.has_permissions(manage_messages=True)


def setup(bot: Bot) -> Bot:
    bot.add_cog(Embeds(bot))
