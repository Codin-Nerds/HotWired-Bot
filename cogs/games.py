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

    @command(aliases=["guess", "guessgame"])
    async def guessthenumber(self, ctx: Context, minimum: int = 1, maximum: int = 20) -> None:
        """Play guess the number."""

        def check(message: Message) -> bool:
            return message.author == ctx.author and message.channel == ctx.channel


        if minimum > maximum:
            await ctx.send("Max limit cannot be smaller than Min limit.")
        elif maximum - minimum < 10:
            await ctx.send("The Max and Min limits difference must be atleast 10!")
        else:
            rand = random.randint(minimum, maximum)
            tries = 5
            guessed = False

            embed = Embed(title="Let's play Guess the number!", color=Color.dark_green())
            embed.add_field(name="**❯❯ Range**", value=f"{minimum} > {maximum}", inline=False)
            embed.add_field(name="**❯❯ Tries Left**", value=f"**{tries}**", inline=False)
            embed.add_field(name="**❯❯ Guess Status**", value="**Not Yet Guessed**", inline=False)
            embed.set_footer(text="Powered By HotWired.")
            message = await ctx.send(embed=embed)

            while not guessed and tries > 0:
                input = await self.bot.wait_for("message", check=check)
                guess = input.content

                await input.delete()

                if guess.isdigit():
                    guess_num = int(guess)
                    if guess_num == rand:
                        guessed = True
                    elif guess_num > rand:
                        tries -= 1

                        embed = Embed(title="Let's play Guess the number!", color=Color.gold())
                        embed.add_field(name="**❯❯ Range**", value=f"{minimum} > {maximum}", inline=False)
                        embed.add_field(name="**❯❯ Tries Left**", value=f"**{tries}**", inline=False)
                        embed.add_field(name="**❯❯ Guess Status**", value="**Guess is higher than the Number**", inline=False)
                        embed.set_footer(text="Powered By HotWired.")
                        await message.edit(embed=embed)

                    elif guess_num < rand:
                        tries -= 1

                        embed = Embed(title="Let's play Guess the number!", color=Color.gold())
                        embed.add_field(name="**❯❯ Range**", value=f"{minimum} > {maximum}", inline=False)
                        embed.add_field(name="**❯❯ Tries Left**", value=f"**{tries}**", inline=False)
                        embed.add_field(name="**❯❯ Guess Status**", value="**Guess is lower than the Number**", inline=False)
                        embed.set_footer(text="Powered By HotWired.")
                        await message.edit(embed=embed)
                else:
                    await ctx.send("Numbers only allowed!")

            if guessed:
                await ctx.send(embed=Embed(description="Congrats, you guessed the Number! You win! :partying_face: ", color=Color.dark_green()))
            else:
                await ctx.send(
                    embed=Embed(description=f"Sorry, you ran out of tries. The number was {rand}. Maybe next time! :frowning: ", color=Color.red())
                )

    @commands.command(aliases=["ms"])
	async def minesweeper(self, ctx: Context, width: int = 10, height: int = 10, difficulty: int = 30) -> None:
		"""Play minesweeper"""
        grid = tuple([['' for i in range(width)] for j in range(height)])
        num = ('0⃣','1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣')
        msg = ''

        if not (1 <= difficulty <= 100):
            await ctx.send("Please enter difficulty in terms of percentage (1-100).")
            return
        if width <= 0 or height <= 0:
            await ctx.send("Invalid width or height value.")
            return
        if width * height > 198:
            return await ctx.channel.send("Your grid size is too big.")
            return
        if width * height <= 4:
            await ctx.send("Your grid size is too small.")
            return

        # set bombs in random location
        for y in range(0, height):
            for x in range(0, width):
                if randint(0, 100) <= difficulty:
                    grid[y][x] = '💣'

		# now set the number emojis
        for y in range(0, height):
            for x in range(0, width):
                if grid[y][x] != '💣':
                    grid[y][x] = num[sum((
                        grid[y - 1][x - 1] == '💣' if y - 1 >= 0 and x - 1 >= 0 else False,
                        grid[y - 1][x] == '💣' if y - 1 >= 0 else False,
                        grid[y - 1][x + 1] == '💣' if y - 1 >= 0 and x + 1 < width else False,
                        grid[y][x - 1] == '💣' if x - 1 >= 0 else False,
                        grid[y][x + 1] == '💣' if x + 1 < width else False,
                        grid[y + 1][x - 1] == '💣' if y + 1 < height and x - 1 >= 0 else False,
                        grid[y + 1][x] == '💣' if y + 1 < height else False,
                        grid[y + 1][x + 1] == '💣' if y + 1 < height and x + 1 < width else False
                    ))]
        await ctx.send(grid[y][x])

        for i in grid:
	        for tile in i:
		        msg += '||' + tile + '|| '
	        msg += '\n'
        await ctx.send(msg)

    @command()
    async def hangman(self, ctx: Context) -> None:
        """Play Hangman game."""

        def check(message: Message) -> bool:
            return message.author == ctx.author and message.channel == ctx.channel

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

        while not guessed and tries > 0 and self.is_playing_hangman(ctx.author, ctx.guild, ctx.channel):
            input = await self.bot.wait_for("message", check=check)
            guess = input.content.upper()

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

    @command()
    async def hangexit(self, ctx: Context) -> None:
        try:
            self.del_hangman_player(ctx.author, ctx.guild, ctx.channel)
        except errors.BadArgument:
            await ctx.send(f"No active games by {ctx.author.mention} found!")

    def is_playing_hangman(self, player: Member, guild: Guild, channel: TextChannel) -> bool:
        if player in self.hangman_players[guild][channel]:
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
            self.hangman_players[guild][channel].remove(player)
        else:
            raise errors.BadArgument("Player is not in game!")


def setup(bot: Bot) -> None:
    bot.add_cog(Games(bot))
