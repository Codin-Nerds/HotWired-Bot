import random
from assets.words import word_list

import discord
from discord.ext import commands


class Games(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def roll(self, ctx, min_limit=1, max_limit=10):
        """Roll a random number."""
        if max_limit - min_limit > 2:
            number = random.randint(min_limit, max_limit)
            await ctx.send('The random number is ' + str(number))
        else:
            await ctx.send('Please specify numbers with difference of **at least 2**')

    @commands.command(aliases=['8ball'])
    async def ball8(self, ctx, *, question):
        """Play 8ball."""
        yes_responses = [
                "Yes - definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes."
            ]
        responses = [
                "It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful."
            ]

        def is_lucky():
            no = random.randint(1, 3)
            if no == 1:
                return True

        if is_lucky():
            answer = random.choice(yes_responses)
        else:
            answer = random.choice(responses)

        await ctx.send(f'Question : {question}\nAnswer : {answer}')

    @commands.command()
    async def hangman(self, ctx):
        def display_hangman(tries):
            stages = [  # final state: head, torso, both arms, and both legs
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / \\
                   -
                """,
                # head, torso, both arms, and one leg
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / 
                   -
                """,
                # head, torso, and both arms
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |      
                   -
                """,
                # head, torso, and one arm
                """
                   --------
                   |      |
                   |      O
                   |     \\|
                   |      |
                   |     
                   -
                """,
                # head and torso
                """
                   --------
                   |      |
                   |      O
                   |      |
                   |      |
                   |     
                   -
                """,
                # head
                """
                   --------
                   |      |
                   |      O
                   |    
                   |      
                   |     
                   -
                """,
                # initial empty state
                """
                   --------
                   |      |
                   |      
                   |    
                   |      
                   |     
                   -
                """
            ]
            return stages[tries]

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        word = random.choice(word_list).upper()
        word_completion = "_" * len(word)
        guessed = False
        guessed_letters = []
        guessed_words = []
        tries = 6

        await ctx.send("Let's play Hangman!")
        await ctx.send(display_hangman(tries))
        await ctx.send(word_completion)
        await ctx.send("\n")

        while not guessed and tries > 0:
            await ctx.send("Please guess a letter or word: ")
            input = await self.client.wait_for('message', check=check)
            guess = input.upper()
            if len(guess) == 1 and guess.isalpha():
                if guess in guessed_letters:
                    await ctx.send(f"You already guessed the letter {guess}")
                elif guess not in word:
                    await ctx.send(f"{guess} is not in the word.")
                    tries -= 1
                    guessed_letters.append(guess)
                else:
                    await ctx.send(f"Good job, {guess} is in the word!")
                    guessed_letters.append(guess)
                    word_as_list = list(word_completion)
                    indices = [i for i, letter in enumerate(word) if letter == guess]

                    for index in indices:
                        word_as_list[index] = guess
                    word_completion = "".join(word_as_list)
                    if "_" not in word_completion:
                        guessed = True
            elif len(guess) == len(word) and guess.isalpha():
                if guess in guessed_words:
                    await ctx.send(f"You already guessed the word {guess}")
                elif guess != word:
                    await ctx.send(f"{guess} is not the word.")
                    tries -= 1
                    guessed_words.append(guess)
                else:
                    guessed = True
                    word_completion = word
            else:
                await ctx.send("Not a valid guess.")
            await ctx.send(display_hangman(tries))
            await ctx.send(word_completion)
            await ctx.send("\n")
        if guessed:
            await ctx.send("Congrats, you guessed the word! You win!")
        else:
            await ctx.send(f"Sorry, you ran out of tries. The word was {word}. Maybe next time!")


def setup(client):
    client.add_cog(Games(client))
