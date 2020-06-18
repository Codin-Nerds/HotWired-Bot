import random
import textwrap

from assets.words import word_list

from discord import Color, Embed, Message
from discord.ext.commands import Bot, Cog, Context, command

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
            embed = Embed(title="Random Roll", color=Color.blurple(), description=f"The random number is: {number}")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Random Roll", color=Color.red(), description="Please specify numbers with difference of **at least 2**")
            await ctx.send(embed=embed)

    @command(aliases=["8ball"])
    async def ball8(self, ctx: Context, *, question: str) -> None:
        """Play 8ball."""
        answer = ""
        reply_type = random.randint(1, 3)

        if reply_type == 1:
            answer = random.choice(POSITIVE_BALL8_RESPONSES)
        elif reply_type == 2:
            answer = random.choice(NEGATIVE_BALL8_RESPONSES)
        elif reply_type == 3:
            answer = random.choice(UNSURE_BALL8_RESPONSES)

        embed = Embed(title="Magic 8-ball", color=Color.blurple())
        embed.add_field(name="Question", value=question)
        embed.add_field(name="Answer", value=answer)

    @command()
    async def hangman(self, ctx: Context) -> None:
        def display_hangman(tries: int) -> str:
            stages = [
                # final state: head, torso, both arms, and both legs
                textwrap.dedent(
                    r"""
                       --------
                       |      |
                       |      O
                       |     \|/
                       |      |
                       |     / \
                       -
                    """
                ),
                # head, torso, both arms, and one leg
                textwrap.dedent(
                    r"""
                       --------
                       |      |
                       |      O
                       |     \|/
                       |      |
                       |     /
                       -
                    """
                ),
                # head, torso, and both arms
                textwrap.dedent(
                    r"""
                       --------
                       |      |
                       |      O
                       |     \|/
                       |      |
                       |
                       -
                    """
                ),
                # head, torso, and one arm
                textwrap.dedent(
                    r"""
                       --------
                       |      |
                       |      O
                       |     \|
                       |      |
                       |
                       -
                    """
                ),
                # head and torso
                textwrap.dedent(
                    r"""
                       --------
                       |      |
                       |      O
                       |      |
                       |      |
                       |
                       -
                    """
                ),
                # head
                textwrap.dedent(
                    r"""
                       --------
                       |      |
                       |      O
                       |
                       |
                       |
                       -
                    """
                ),
                # initial empty state
                textwrap.dedent(
                    r"""
                       --------
                       |      |
                       |
                       |
                       |
                       |
                       -
                    """
                ),
            ]
            return stages[tries]

        def check(message: Message) -> bool:
            return message.author == ctx.author and message.channel == ctx.channel

        word = random.choice(word_list).upper()
        word_completion = "*" * len(word)
        guessed = False
        guessed_letters = []
        guessed_words = []
        tries = 6

        await ctx.send(embed=Embed(title="Let's play Hangman!", color=Color.dark_green()))
        await ctx.send(embed=Embed(title="Hangman Status", description=display_hangman(tries), color=Color.dark_magenta()))
        await ctx.send(embed=Embed(title="Word Completion", description=word_completion, color=Color.dark_magenta()))

        while not guessed and tries > 0:
            await ctx.send(embed=Embed(description="Please guess a letter or word: ", color=Color.gold()))
            input = await self.bot.wait_for("message", check=check)
            guess = input.content.upper()

            if len(guess) == 1 and guess.isalpha():
                if guess in guessed_letters:
                    await ctx.send(embed=Embed(description=f"You already guessed the letter {guess}", color=Color.red()))
                elif guess not in word:
                    await ctx.send(embed=Embed(description=f"{guess} is not in the word.", color=Color.dark_magenta()))
                    tries -= 1
                    guessed_letters.append(guess)
                else:
                    await ctx.send(embed=Embed(description=f"Good job, {guess} is in the word!", color=Color.dark_green()))
                    guessed_letters.append(guess)
                    word_as_list = list(word_completion)
                    indices = [i for i, letter in enumerate(word) if letter == guess]

                    for index in indices:
                        word_as_list[index] = guess
                    word_completion = "".join(word_as_list)
                    if "*" not in word_completion:
                        guessed = True

            elif len(guess) == len(word) and guess.isalpha():
                if guess in guessed_words:
                    await ctx.send(embed=Embed(description=f"You already guessed the word {guess}", color=Color.red()))
                elif guess != word:
                    await ctx.send(embed=Embed(description=f"{guess} is not the word.", color=Color.dark_orange()))
                    tries -= 1
                    guessed_words.append(guess)
                else:
                    guessed = True
                    word_completion = word
            else:
                await ctx.send(embed=Embed(description="Not a valid guess.", color=Color.blurple()))

            await ctx.send(embed=Embed(title="Hangman Status", description=display_hangman(tries), color=Color.dark_magenta()))
            await ctx.send(embed=Embed(title="Word Completion", description=word_completion, color=Color.dark_magenta()))

        if guessed:
            await ctx.send(embed=Embed(description="Congrats, you guessed the word! You win! :partying_face: ", color=Color.dark_green()))
        else:
            await ctx.send(
                embed=Embed(description=f"Sorry, you ran out of tries. The word was {word}. Maybe next time! :frowning: ", color=Color.red())
            )


def setup(bot: Bot) -> None:
    bot.add_cog(Games(bot))
