from bot.core.bot import Bot

from discord.ext.commands import Cog, Context, command

from bot.utils.pagify import pagify

from pyfiglet import Figlet, FigletFont

import ascii as asc

import random


def box(text: str) -> str:
    return f"```\n{text}\n```"


class AsciiArt(Cog):
    """Ascii art generator."""

    def __init__(self, bot: Bot) -> None:
        """Init."""
        self.bot = bot

    @command()
    async def figletfonts(self, ctx: Context) -> None:
        """List all Figlet fonts."""
        await ctx.send("List of supported fonts:")
        out = FigletFont.getFonts()

        for page in pagify(', '.join(out), shorten_by=24):
            await ctx.send(box(page))

    @command()
    async def figlet(self, ctx: Context, text: str, font=None) -> None:
        """Convert text to ascii art."""
        if font is None:
            font = 'slant'

        if font == 'random':
            fonts = FigletFont.getFonts()
            font = random.choice(fonts)

        f = Figlet(font=font)
        out = f.renderText(text)

        for page in pagify(out, shorten_by=24):
            await ctx.send(box(page))

    @command()
    async def figletrandom(self, ctx: Context, text: str) -> None:
        """Convert text to ascii art using random font."""
        font = random.choice(FigletFont.getFonts())

        f = Figlet(font=font)
        out = f.renderText(text)

        for page in pagify(out, shorten_by=24):
            await ctx.send(box(page))

        await ctx.send(f"Font: {font}")

    @command()
    async def img2txt(self, ctx: Context, url: str = None, columns=30) -> None:
        """Convert image as URL to ascii."""
        if url is None:
            await ctx.send("Specify an URL!")
            return

        output = asc.loadFromUrl(url, columns=columns, color=False)

        for page in pagify(output, shorten_by=24):
            await ctx.send(box(page))


def setup(bot: Bot) -> None:
    bot.add_cog(AsciiArt(bot))
