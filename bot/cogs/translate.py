from aiogoogletrans import Translator as GoogleTranslator
from discord import Color, Embed
from discord.ext.commands import Cog, Context, command

from bot.core.bot import Bot

translator = GoogleTranslator()


class Translator(Cog):
    """Translation is so cool."""

    def __init__(self, bot: Bot) -> None:
        """Initialize the translator."""
        self.bot = bot

    @command(aliases=["linfo"])
    async def getinfo(self, ctx: Context, *, sentence: str) -> None:
        """Get info about a sentence."""
        detection = await translator.detect(sentence)

        embed = Embed(title="Sentence Info", color=Color.dark_orange())
        embed.add_field(
            name="Language Code", value=detection.lang, inline=False
        )
        embed.add_field(
            name="Confidence", value=detection.confidence, inline=False
        )
        await ctx.send(embed=embed)

    @command()
    async def translate(
            self,
            ctx: Context,
            source_language: str = "en",
            destination_language: str = "en",
            *,
            sentence: str = "Hello World",
    ) -> None:
        """Translate a sentence."""
        translation = await translator.translate(
            sentence, dest=destination_language, src=source_language
        )
        embed = Embed(
            title="Translation",
            description=f"Sentence : **{sentence}**\nTranslation : **{translation.text}**\nType : **{translation.src} > {translation.dest}**",
            color=Color.gold(),
        )
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Add translation to the bot."""
    bot.add_cog(Translator(bot))
