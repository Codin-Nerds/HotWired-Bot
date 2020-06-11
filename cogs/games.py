import random

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
            await ctx.send('The random number is ' + str(number))
        else:
            await ctx.send('Please specify numbers with difference of **at least 2**')

    @command(aliases=['8ball'])
    async def ball8(self, ctx: Context, *, question: str) -> None:
        """Play 8ball."""
        reply_type = random.randint(1, 3)

        if reply_type == 1:  # Positive reply
            answer = random.choice(POSITIVE_BALL8_RESPONSES)
        elif reply_type == 2:  # Negative reply
            answer = random.choice(NEGATIVE_BALL8_RESPONSES)
        elif reply_type == 3:  # Unsure reply
            answer = random.choice(UNSURE_BALL8_RESPONSES)

        await ctx.send(f"Question: {question}\nAnswer: {answer}")


def setup(bot: Bot):
    bot.add_cog(Games(bot))
