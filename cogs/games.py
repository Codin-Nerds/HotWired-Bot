import random

from discord import Embed, Color
from discord.ext import Bot
from discord.ext.commands import Cog, command, Context

POSITIVE_BALL8_RESPONSES = [
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
]
NEGATIVE_BALL8_RESPONSES = [
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]
UNSURE_BALL8_RESPONSES = [
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
]


class Games(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def roll(self, ctx: Context, min_limit: int = 1, max_limit: int = 10) -> None:
        """Roll a random number."""
        if max_limit - min_limit > 2:
            number = random.randint(min_limit, max_limit)
            embed = Embed(
                title="Random Roll",
                color=Color.blue(),
                description=f"The random number is: {number}"
            )
            await ctx.send(embed=embed)
        else:
            embed = Embed(
                title="Random Roll",
                color=Color.red(),
                description="Please specify numbers with difference of **at least 2**"
            )
            await ctx.send(embed=embed)

    @command(aliases=['8ball'])
    async def ball8(self, ctx: Context, *, question: str) -> None:
        """Play 8ball."""
        reply_type = random.randint(1, 3)

        if reply_type == 1:
            answer = random.choice(POSITIVE_BALL8_RESPONSES)
        elif reply_type == 2:
            answer = random.choice(NEGATIVE_BALL8_RESPONSES)
        elif reply_type == 3:
            answer = random.choice(UNSURE_BALL8_RESPONSES)

        embed = Embed(
            title="Magic 8-ball",
            color=Color.blurple(),
        )
        embed.add_field(name="Question", value=question)
        embed.add_field(name="Answer", value=answer)


def setup(bot: Bot):
    bot.add_cog(Games(bot))
