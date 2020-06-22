import random
from collections import defaultdict

from discord import Color, Embed, Guild, Member, Message, TextChannel
from discord.ext.commands import Bot, Cog, Context, command, errors

from assets.words import word_list

from .utils import constants


class Games(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.hangman_players = defaultdict(lambda: defaultdict(list))

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
        reply_type = random.randint(1, 3)

        if reply_type == 1:
            answer = random.choice(constants.POSITIVE_REPLIES)
        elif reply_type == 2:
            answer = random.choice(constants.NEGATIVE_REPLIES)
        elif reply_type == 3:
            answer = random.choice(constants.ERROR_REPLIES)

        embed = Embed(title="Magic 8-ball", color=Color.blurple())
        embed.add_field(name="Question", value=question)
        embed.add_field(name="Answer", value=answer)

    @command()
    async def hangman(self, ctx: Context) -> None:
        """Play Hangman game."""
        def display_hangman(tries: int) -> str:
            stages = [
                # final state: head, torso, both arms, and both legs
                r"""```
--------
|      |
|      O
|     \|/
|      |
|     / \
-
                    ```""",
                # head, torso, both arms, and one leg
                r"""```
--------
|      |
|      O
|     \|/
|      |
|     /
-
                    ```""",
                # head, torso, and both arms
                r"""```
--------
|      |
|      O
|     \|/
|      |
|
-
                    ```""",
                # head, torso, and one arm
                r"""```
--------
|      |
|      O
|     \|
|      |
|
-
                    ```""",
                # head and torso
                r"""```
--------
|      |
|      O
|      |
|      |
|
-
                    ```""",
                # head
                r"""```
--------
|      |
|      O
|
|
|
-
                    ```""",
                # initial empty state
                r"""```
--------
|      |
|
|
|
|
-
                    ```""",
            ]
            return stages[tries]

        def check(message: Message) -> bool:
            return message.author == ctx.author and message.channel == ctx.channel

        word = random.choice(word_list).upper()
        word_completion = "#" * len(word)
        guessed = False
        guessed_letters = []
        guessed_words = []
        tries = 6

        embed = Embed(title="Let's play Hangman!", color=Color.dark_green())
        embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
        embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
        embed.add_field(name="**❯❯ Word Status**", value="**Not Yet Guessed**", inline=False)
        embed.set_footer(text=">>hangexit to exit the game! | Powered By HotWired.")
        message = await ctx.send(embed=embed)
        guess_embed = await ctx.send(embed=Embed(description="Please guess a letter or word: ", color=Color.gold()))
        if not self.is_playing_hangman(ctx.author, ctx.guild, ctx.channel):
            try:
                self.add_hangman_player(ctx.author, ctx.guild, ctx.channel)
            except errors.BadArgument:
                await ctx.send(f"Active games by {ctx.author.mention} found. Use `>>hangexit` to exit!")

        while not guessed and tries > 0:
            input = await self.bot.wait_for("message", check=check)
            guess = input.content.upper()
            # TODO : Repair this exit statement
            if guess == ">>HANGEXIT":
                try:
                    self.del_hangman_player(ctx.author, ctx.guild, ctx.channel)
                except errors.BadArgument:
                    await ctx.send(f"No active games by {ctx.author.mention} found!")
            await input.delete()

            if len(guess) == 1 and guess.isalpha():
                if guess in guessed_letters:
                    embed = Embed(title="Hangman Stats", color=Color.dark_blue())
                    embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
                    embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
                    embed.add_field(name="**❯❯ Word Status**", value=f"You already guessed the letter {guess}", inline=False)
                    embed.set_footer(text="Powered By HotWired.")
                    await message.edit(embed=embed)
                elif guess not in word:
                    tries -= 1
                    guessed_letters.append(guess)

                    embed = Embed(title="Hangman Stats", color=Color.dark_blue())
                    embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
                    embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
                    embed.add_field(name="**❯❯ Word Status**", value=f"{guess} is not in the word.", inline=False)
                    embed.set_footer(text="Powered By HotWired.")
                    await message.edit(embed=embed)
                else:
                    guessed_letters.append(guess)
                    word_as_list = list(word_completion)
                    indices = [i for i, letter in enumerate(word) if letter == guess]

                    for index in indices:
                        word_as_list[index] = guess
                    word_completion = "".join(word_as_list)
                    if "#" not in word_completion:
                        guessed = True

                    embed = Embed(title="Hangman Stats", color=Color.dark_blue())
                    embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
                    embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
                    embed.add_field(name="**❯❯ Word Status**", value=f"Good job, {guess} is in the word!", inline=False)
                    embed.set_footer(text="Powered By HotWired.")
                    await message.edit(embed=embed)

            elif len(guess) == len(word) and guess.isalpha():
                if guess in guessed_words:
                    embed = Embed(title="Hangman Stats", color=Color.dark_blue())
                    embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
                    embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
                    embed.add_field(name="**❯❯ Word Status**", value=f"You already guessed the word {guess}", inline=False)
                    embed.set_footer(text="Powered By HotWired.")
                    await message.edit(embed=embed)
                elif guess != word:
                    tries -= 1
                    guessed_words.append(guess)

                    embed = Embed(title="Hangman Stats", color=Color.dark_blue())
                    embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
                    embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
                    embed.add_field(name="**❯❯ Word Status**", value=f"{guess} is not in the word.", inline=False)
                    embed.set_footer(text="Powered By HotWired.")
                    await message.edit(embed=embed)
                else:
                    guessed = True
                    word_completion = word
            else:
                embed = Embed(title="Hangman Stats", color=Color.dark_blue())
                embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
                embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
                embed.add_field(name="**❯❯ Word Status**", value="Not a valid guess.", inline=False)
                embed.set_footer(text="Powered By HotWired.")
                await message.edit(embed=embed)

        await guess_embed.delete()
        if guessed:
            embed = Embed(title="Hangman Stats", color=Color.dark_blue())
            embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
            embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
            embed.set_footer(text="Powered By HotWired.")
            await message.edit(embed=embed)
            await ctx.send(embed=Embed(description="Congrats, you guessed the word! You win! :partying_face: ", color=Color.dark_green()))
        else:
            embed = Embed(title="Hangman Stats", color=Color.dark_blue())
            embed.add_field(name="**❯❯ Hang Status**", value=display_hangman(tries), inline=False)
            embed.add_field(name="**❯❯ Word Completion Status**", value=f"**{word_completion}**", inline=False)
            embed.set_footer(text="Powered By HotWired.")
            await message.edit(embed=embed)
            await ctx.send(
                embed=Embed(description=f"Sorry, you ran out of tries. The word was {word}. Maybe next time! :frowning: ", color=Color.red())
            )

    def is_playing_hangman(self, player: Member, guild: Guild, channel: TextChannel) -> bool:
        if player.id in self.hangman_players[guild][channel]:
            return True
        else:
            return False

    def add_hangman_player(self, player: Member, guild: Guild, channel: TextChannel) -> None:
        if not self.is_playing_hangman(player, guild, channel):
            self.hangman_players[guild][channel].append(player)
        else:
            raise errors.BadArgument("Player is already in game!")

    def del_hangman_player(self, player: Member, guild: Guild, channel: TextChannel) -> None:
        if self.is_playing_hangman(player, guild, channel):
            self.hangman_players[guild.id][channel.id].remove[player]
        else:
            raise errors.BadArgument("Player is not in game!")


def setup(bot: Bot) -> None:
    bot.add_cog(Games(bot))
