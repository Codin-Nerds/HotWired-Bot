from discord import Embed, Color
from discord.ext.commands import command, Cog, Bot, Context
from googletrans import Translator, config

translator = Translator()


class Translator(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(aliases=["lcode"])
    async def lang_code(self, ctx: Context, *, language: str) -> None:
        def get_key(val: str) -> str:
            for key, value in config.LANGUAGES.items():
                if val == value:
                    return key
            return "Language Not found!"

        code = get_key(language)
        if code == "Language Not found!":
            embed = Embed(description="Language Not Found!", color=Color.red())
        else:
            embed = Embed(title="Language Code", description=f"Language : **{language}**\nCode : **{code}**", color=Color.blurple())
        await ctx.send(embed=embed)

    @command(aliases=["linfo"])
    async def getinfo(self, ctx: Context, *, sentence: str) -> None:
        detection = translator.detect(sentence)

        embed = Embed(title="Sentence Info", color=Color.dark_orange())
        embed.add_field(name="Language Code", value=detection.lang, inline=False)
        embed.add_field(name="Confidence", value=detection.confidence, inline=False)
        embed.add_field(name="Language", value=config.LANGUAGES[detection.lang], inline=False)
        await ctx.send(embed=embed)

    @command()
    async def translate(self, ctx: Context, source_language: str = "en", destination_language: str = "en", *, sentence: str = "Hello World") -> None:
        translation = translator.translate(sentence, dest=destination_language, src=source_language)
        embed = Embed(
            title="Translation",
            description=f"Sentence : **{sentence}**\nTranslation : **{translation.text}**\nType : **{translation.src} > {translation.dest}**",
            color=Color.gold(),
        )
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Translator(bot))
