import random
from collections import defaultdict

from discord import Color, Embed, Guild, Member, Message, TextChannel
from discord.ext.commands import Bot, Cog, Context, command, errors

from assets.words import word_list

from .utils import constants
from discord import User, Channel


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


# Make this flake8 compatible asap
class TTT:
    """Tic Tac Toe."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.ttt_games = {}

    @command(pass_context=True)
    async def ttt(self, ctx: Context, move: str = "") -> None:
        """ Tic Tac Toe """
        await self.ttt_new(ctx.message.author, ctx.message.channel)

    async def ttt_new(self, user: User, channel: Channel) -> None:
        self.ttt_games[user.id] = [" "] * 9
        response = self.ttt_make_board(user)
        response += "Your move:"
        msg = await self.bot.send_message(channel, response)
        await self.makeButtons(msg)

    async def ttt_move(self, user, message, move):
        print("ttt_move:{0}".format(user.id))
        uid = user.id
        if uid not in self.ttt_games:
            print("New game")
            return await self.ttt_new(user, message.channel)

        # Check spot is empty
        if self.ttt_games[uid][move] == " ":
            self.ttt_games[uid][move] = "x"
            print("Moved to {0}".format(move))
        else:
            print("Invalid move: {0}".format(move))
            return None

        # Check winner
        check = self.tttDoChecks(self.ttt_games[uid])
        if check is not None:
            msgAppend = "It's a draw!" if check == "draw" else "{0} wins!".format(check[-1])
            print(msgAppend)
            await self.bot.edit_message(message, new_content="{0}{1}".format(self.ttt_make_board(user), msgAppend))
            return None
        print("Check passed")

        # AI move
        mv = self.tttAIThink(self.tttMatrix(self.ttt_games[uid]))
        self.ttt_games[uid][self.tttCoordsToIndex(mv)] = "o"
        print("AI moved")

        # Update board
        await self.bot.edit_message(message, new_content=self.ttt_make_board(user))
        print("Board updated")

        # Check winner again
        check = self.tttDoChecks(self.ttt_games[uid])
        if check is not None:
            msgAppend = "It's a draw!" if check == "draw" else "{0} wins!".format(check[-1])
            print(msgAppend)
            await self.bot.edit_message(message, new_content="{0}{1}".format(self.ttt_make_board(user), msgAppend))
        print("Check passed")

    def ttt_make_board(self, author):
        return "{0}\n{1}\n".format(author.mention, self.tttTable(self.ttt_games[author.id]))

    async def makeButtons(self, msg):
        await self.bot.add_reaction(msg, u"\u2196")  # 0 tl
        await self.bot.add_reaction(msg, u"\u2B06")  # 1 t
        await self.bot.add_reaction(msg, u"\u2197")  # 2 tr
        await self.bot.add_reaction(msg, u"\u2B05")  # 3 l
        await self.bot.add_reaction(msg, u"\u23FA")  # 4 mid
        await self.bot.add_reaction(msg, u"\u27A1")  # 5 r
        await self.bot.add_reaction(msg, u"\u2199")  # 6 bl
        await self.bot.add_reaction(msg, u"\u2B07")  # 7 b
        await self.bot.add_reaction(msg, u"\u2198")  # 8 br

    async def on_reaction_add(self, reaction, user):
        if reaction.message.author.id == self.bot.user.id and not user.id == self.bot.user.id:
            move = self.decodeMove(str(reaction.emoji))
            if move is not None:
                await self.ttt_move(user, reaction.message, move)

    def decodeMove(self, emoji):
        dict = {
            u"\u2196": 0,
            u"\u2B06": 1,
            u"\u2197": 2,
            u"\u2B05": 3,
            u"\u23FA": 4,
            u"\u27A1": 5,
            u"\u2199": 6,
            u"\u2B07": 7,
            u"\u2198": 8
        }
        return dict[emoji] if emoji in dict else None

    # Utility Functions
    def tttTable(self, xo):
        return (("%s%s%s\n" * 3) % tuple(xo)).replace("o", ":o2:").replace("x", ":regional_indicator_x:").replace(" ", ":white_large_square:")

    def tttMatrix(self, b):
        return [
            [b[0], b[1], b[2]],
            [b[3], b[4], b[5]],
            [b[6], b[7], b[8]]
        ]

    def tttCoordsToIndex(self, coords):
        map = {
            (0, 0): 0,
            (0, 1): 1,
            (0, 2): 2,
            (1, 0): 3,
            (1, 1): 4,
            (1, 2): 5,
            (2, 0): 6,
            (2, 1): 7,
            (2, 2): 8
        }
        return map[coords]

    def tttDoChecks(self, b):
        m = self.tttMatrix(b)
        if self.tttCheckWin(m, "x"):
            return "win X"
        if self.tttCheckWin(m, "o"):
            return "win O"
        if self.tttCheckDraw(b):
            return "draw"
        return None

    def tttFindStreaks(self, m, xo):
        row = [0, 0, 0]
        col = [0, 0, 0]
        dia = [0, 0]

        # Check rows and columns for X streaks
        for y in range(3):
            for x in range(3):
                if m[y][x] == xo:
                    row[y] += 1
                    col[x] += 1

        # Check diagonals
        if m[0][0] == xo:
            dia[0] += 1
        if m[1][1] == xo:
            dia[0] += 1
            dia[1] += 1
        if m[2][2] == xo:
            dia[0] += 1
        if m[2][0] == xo:
            dia[1] += 1
        if m[0][2] == xo:
            dia[1] += 1

        return (row, col, dia)

    def tttFindEmpty(self, matrix, rcd, n):
        # Rows
        if rcd == "r":
            for x in range(3):
                if matrix[n][x] == " ":
                    return x
        # Columns
        if rcd == "c":
            for x in range(3):
                if matrix[x][n] == " ":
                    return x
        # Diagonals
        if rcd == "d":
            if n == 0:
                for x in range(3):
                    if matrix[x][x] == " ":
                        return x
            else:
                for x in range(3):
                    if matrix[x][2 - x] == " ":
                        return x

        return False

    def tttCheckWin(self, m, xo):
        row, col, dia = self.tttFindStreaks(m, xo)
        dia.append(0)

        for i in range(3):
            if row[i] == 3 or col[i] == 3 or dia[i] == 3:
                return True

        return False

    def tttCheckDraw(self, board):
        return " " not in board

    def tttAIThink(self, m):
        rx, cx, dx = self.tttFindStreaks(m, "x")
        ro, co, do = self.tttFindStreaks(m, "o")

        mv = self.tttAIMove(2, m, ro, co, do)
        if mv is not False:
            return mv
        mv = self.tttAIMove(2, m, rx, cx, dx)
        if mv is not False:
            return mv
        mv = self.tttAIMove(1, m, ro, co, do)
        if mv is not False:
            return mv
        return self.tttAIMove(1, m, rx, cx, dx)

    def tttAIMove(self, n, m, row, col, dia):
        for r in range(3):
            if row[r] == n:
                x = self.tttFindEmpty(m, "r", r)
                if x is not False:
                    return (r, x)
            if col[r] == n:
                y = self.tttFindEmpty(m, "c", r)
                if y is not False:
                    return (y, r)

        if dia[0] == n:
            y = self.tttFindEmpty(m, "d", 0)
            if y is not False:
                return (y, y)
        if dia[1] == n:
            y = self.tttFindEmpty(m, "d", 1)
            if y is not False:
                return (y, 2 - y)

        return False


def setup(bot: Bot) -> None:
    bot.add_cog(Games(bot))
    bot.add_cog(TTT(bot))
