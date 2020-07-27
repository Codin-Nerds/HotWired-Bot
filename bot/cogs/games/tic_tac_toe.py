import random
import typing as t
from collections import defaultdict

from discord import Color, Embed, Member, Reaction, User
from discord.ext.commands import Cog, Context, command

from bot.core.bot import Bot
from bot.core.decorators import ProcessedMember


class Game:
    """Internal Tic Tac Toe logic."""
    reactions = [
        "\u2196",  # top left
        "\u2B06",  # top
        "\u2197",  # top right
        "\u2B05",  # left
        "\u23FA",  # middle
        "\u27A1",  # right
        "\u2199",  # bottom left
        "\u2B07",  # bottom
        "\u2198",  # bottom right
    ]
    emojis = {
        "x": ":x:",
        "o": ":o:",
        "": ":black_large_square:",
    }

    def __init__(self, ctx: Context, opponent: t.Optional[Member]) -> None:
        self.ctx = ctx
        self.author = ctx.author
        self.player = "x"
        self.opponent = opponent
        self.cpu_opponent = opponent is None
        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]

    def next_player(self) -> None:
        """Switch player."""
        if self.player == "x":
            self.player = "o"
        else:
            self.player = "x"

    async def send_board(self) -> None:
        """Send the embed with the board."""
        embed = Embed(
            title="Tic Tac Toe",
            description=self.str_board,
            color=Color.blurple()
        )
        if not hasattr(self, "msg"):
            self.msg = await self.ctx.send(embed=embed)
            await self.add_buttons()
        else:
            await self.msg.edit(embed=embed)

    async def add_buttons(self) -> None:
        """Add reaction buttons to the message."""
        for reaction in self.reactions:
            await self.msg.add_reaction(reaction)

    def apply_emoji_move(self, reaction_emoji: str, xo: t.Literal["x", "o"]) -> bool:
        """Apply move based on an emoji."""
        try:
            move_id = self.reactions.index(reaction_emoji)
        except ValueError:
            # Bad emoji passed
            return False

        row = move_id // 3
        col = move_id % 3

        if not self.board[row][col]:
            self.board[row][col] = xo
            return True
        return False

    @property
    def str_board(self) -> str:
        """Stringify the board using emojis."""
        stringified = ""
        for row in self.board:
            stringified += "|".join(self.emojis[col] for col in row)
            stringified += "\n"
        return stringified

    def check_win(self) -> t.Tuple[bool, t.Literal["x", "o", None]]:
        """Check if the board is in win status, if it is return (True, winner)"""

        # Check rows and columns for X streaks
        row_stat = {"x": [0, 0, 0], "o": [0, 0, 0]}
        col_stat = {"x": [0, 0, 0], "o": [0, 0, 0]}

        for row_id, row in enumerate(self.board):
            for col_id, col in enumerate(row):
                if col:
                    row_stat[col][row_id] += 1
                    col_stat[col][col_id] += 1

        if 3 in row_stat["x"] or 3 in col_stat["x"]:
            return (True, "x")
        if 3 in row_stat["o"] or 3 in col_stat["o"]:
            return (True, "o")

        # Check diagonals
        diag_1 = [row[col] for col, row in enumerate(self.board)]
        diag_2 = [row[(col + 1) * -1] for col, row in enumerate(self.board)]

        for xo in ["x", "o"]:
            if all(field == xo for field in diag_1):
                return (True, xo)
            if all(field == xo for field in diag_2):
                return (True, xo)

        return (False, None)

    def check_draw(self) -> bool:
        """Check if current board is in draw."""

        return all("" not in row for row in self.board)

    async def apply_win(self, xo: t.Literal["x", "o"]) -> None:
        """Send an appropriate win/lose message based on `xo`."""
        if xo == "x":
            winner = self.author
        else:
            winner = self.opponent

        if winner:
            await self.ctx.send(f":tada: Congratulations {winner.mention}, you won!")
        else:
            await self.ctx.send(f"You lost {self.author.mention}, better luck next time!")

    async def turn(self, member: Member, reaction: Reaction) -> bool:
        """A single turn of the game, returns ended status of game (True = ended)."""
        if not any([
            (self.opponent == member and self.player == "o"),
            (self.author == member and self.player == "x"),
        ]):
            await self.ctx.send(f"Hey {member.mention}, it's not your turn!")
            await reaction.remove(member)
            return False

        if not self.apply_emoji_move(str(reaction.emoji), self.player):
            await self.ctx.send(f"Hey {member.mention}, that tile is occupied!")
            await reaction.remove(member)
            return False

        await self.send_board()

        win, xo = self.check_win()
        if win:
            await self.apply_win(xo)
            return True

        if self.check_draw():
            await self.ctx.send("Game result: draw")
            return True

        if self.cpu_opponent:
            self.cpu_move()
            await self.send_board()
            win, xo = self.check_win()
            if win:
                await self.apply_win(xo)
                return True
            if self.check_draw():
                await self.ctx.send("Game result: draw")
                return True
            return False

        self.next_player()
        return False

    def test_win_move(self, row: int, col: int, xo: t.Literal["x", "o"]) -> bool:
        """Retrun True if given move is a winning move"""
        if self.board[row][col]:
            return False

        self.board[row][col] = xo
        win, _ = self.check_win()
        self.board[row][col] = ""

        if win:
            return True
        return False

    def cpu_move(self) -> None:
        """CPU's game turn."""
        cpu_xo = "o"

        # Check if CPU can win on any square
        for row in range(3):
            for col in range(3):
                if self.test_win_move(row, col, cpu_xo):
                    self.board[row][col] = cpu_xo
                    return

        # Check for square that player can win on
        for row in range(3):
            for col in range(3):
                if self.test_win_move(row, col, self.player):
                    self.board[row][col] = cpu_xo
                    return

        # Move on a free corner
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        random.shuffle(corners)
        for row, col in corners:
            if self.board[row][col]:
                continue

            self.board[row][col] = cpu_xo
            return

        # Move on a free center
        if not self.board[1][1]:
            self.board[1][1] = cpu_xo
            return

        # Move on a free side
        sides = [(0, 1), (1, 0), (2, 1), (1, 2)]
        random.shuffle(sides)
        for row, col in sides:
            if self.board[row][col]:
                continue

            self.board[row][col] = cpu_xo
            return

    def __str__(self) -> str:
        """Convert the board 2D array to string"""
        result = ""

        for row in self.board:
            result += "|".join(f"{val: ^{2}}" for val in row)
            result += f"\n{'-' * 9}\n"

        return "\n".join(result.splitlines()[:-1])


class TicTacToe(Cog):
    """Tic-Tac-Toe Game."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.games = defaultdict(lambda: defaultdict(lambda: None))

    @command(aliases=["ttt", "tictactoe"])
    async def tic_tac_toe(self, ctx: Context, opponent: t.Optional[ProcessedMember] = None) -> None:
        """Play a game of Tic-Tac-Toe."""
        if self.games[ctx.guild][ctx.author]:
            await ctx.send(f"Sorry {ctx.author.mention}, you already have an active tic tac toe game on this server.")
            return
        if self.games[ctx.guild][ctx.author]:
            await ctx.send(
                f"Sorry, {ctx.author.mention}, {opponent.mention} already has an active tic tac toe game on this server, let him finish first."
            )
            return

        game = Game(ctx, opponent)
        self.games[ctx.guild][ctx.author] = game
        if opponent:
            self.games[ctx.guild][opponent] = game
        await game.send_board()

    @command(aliases=["tttstop", "tictactoestop"])
    async def tic_tac_toe_stop(self, ctx: Context) -> None:
        """Stop playing tic tac toe."""
        if self.games[ctx.guild][ctx.author]:
            del self.games[ctx.guild][ctx.author]
            await ctx.send("Game stopped.")
        else:
            await ctx.send(f"Sorry {ctx.author.mention}, you don't have an active game of tic tac toe on this server.")

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User) -> None:
        # TODO: Use a custom converter for converting User to Member
        guild = reaction.message.guild
        member = guild.get_member(user.id)
        game = self.games[guild][member]

        if game:
            ended = await game.turn(member, reaction)
            if ended:
                if game.opponent == member:
                    del self.games[guild][game.author]
                elif game.author == member and not game.cpu_opponent:
                    del self.games[guild][game.opponent]
                del self.games[guild][member]
