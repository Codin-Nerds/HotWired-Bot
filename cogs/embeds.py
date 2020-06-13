from collections import defaultdict

from discord import Embed
from discord.ext import Bot
from discord.ext.commands import Cog, Context, group


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
    async def description(self, ctx: Context, *, description: str):
        """Set Description for the Embed."""
        self.embeds[ctx.author].description = description
        await ctx.send("Embeds description updated.")

    @embed_group.command(aliases=['add_description'])
    async def append_description(self, ctx: Context, *, description: str):
        """Add text into Description of the Embed."""
        self.embeds[ctx.author].description += description
        await ctx.send("Embeds description appended.")

    @embed_group.command(aliases=['set_footer'])
    async def footer(self, ctx: Context, *, footer: str):
        """Set Footer for the Embed."""
        self.embeds[ctx.author].set_footer(text=footer)
        await ctx.send("Embeds footer updated.")

    def cog_check(self, ctx: Context) -> bool:
        """
        Only allow users with manage messages permission to invoke commands in this cog.

        This is needed because Embeds can be much longer in comparison to regular messages,
        therefore it would be very easy to spam things and clutter the chat.
        """
        return ctx.author.has_permissions(manage_messages=True)


def setup(bot: Bot) -> Bot:
    bot.add_cog(Embeds(bot))
