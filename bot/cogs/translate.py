from aiogoogletrans import Translator

from bot.core.bot import Bot

from discord import Color, Embed
from discord.ext.commands import Cog, Context, command

translator = Translator()


class Translator(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(aliases=["linfo"])
    async def getinfo(self, ctx: Context, *, sentence: str) -> None:
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
    bot.add_cog(Translator(bot))
