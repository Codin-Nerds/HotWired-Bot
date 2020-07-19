import typing as t

from bot.core.bot import Bot

from discord import Channel, Message, Reaction, User
from discord.ext.commands import Cog, Context, command


class TTT(Cog):
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

    async def ttt_move(self, user: User, message: Message, move) -> None:
        print(f"ttt_move:{user.id}")
        uid = user.id
        if uid not in self.ttt_games:
            print("New game")
            return await self.ttt_new(user, message.channel)

        # Check spot is empty
        if self.ttt_games[uid][move] == " ":
            self.ttt_games[uid][move] = "x"
            print(f"Moved to {move}")
        else:
            print(f"Invalid move: {move}")
            return None

        # Check winner
        check = self.tttDoChecks(self.ttt_games[uid])
        if check is not None:
            msgAppend = "It's a draw!" if check == "draw" else f"{check[-1]} wins!"
            print(msgAppend)
            await self.bot.edit_message(message, new_content=f"{self.ttt_make_board(user)}{msgAppend}")
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
            msgAppend = "It's a draw!" if check == "draw" else f"{check[-1]} wins!"
            print(msgAppend)
            await self.bot.edit_message(message, new_content="{self.ttt_make_board(user)}{msgAppend}")
        print("Check passed")

    def ttt_make_board(self, author: User) -> str:
        return f"{author.mention}\n{self.tttTable(self.ttt_games[author.id])}\n"

    async def makeButtons(self, msg: Message) -> None:
        await self.bot.add_reaction(msg, u"\u2196")  # 0 tl
        await self.bot.add_reaction(msg, u"\u2B06")  # 1 t
        await self.bot.add_reaction(msg, u"\u2197")  # 2 tr
        await self.bot.add_reaction(msg, u"\u2B05")  # 3 l
        await self.bot.add_reaction(msg, u"\u23FA")  # 4 mid
        await self.bot.add_reaction(msg, u"\u27A1")  # 5 r
        await self.bot.add_reaction(msg, u"\u2199")  # 6 bl
        await self.bot.add_reaction(msg, u"\u2B07")  # 7 b
        await self.bot.add_reaction(msg, u"\u2198")  # 8 br

    async def on_reaction_add(self, reaction: Reaction, user: User) -> None:
        if reaction.message.author.id == self.bot.user.id and not user.id == self.bot.user.id:
            move = self.decodeMove(str(reaction.emoji))
            if move is not None:
                await self.ttt_move(user, reaction.message, move)

    def decodeMove(self, emoji: str) -> None:
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
    def tttTable(self, xo) -> str:
        return (("%s%s%s\n" * 3) % tuple(xo)).replace("o", ":o2:").replace("x", ":regional_indicator_x:").replace(" ", ":white_large_square:")

    def tttMatrix(self, b: list) -> list:
        return [
            [b[0], b[1], b[2]],
            [b[3], b[4], b[5]],
            [b[6], b[7], b[8]]
        ]

    def tttCoordsToIndex(self, coords: tuple) -> str:
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

    def tttDoChecks(self, b: str) -> t.Union[str, None]:
        m = self.tttMatrix(b)
        if self.tttCheckWin(m, "x"):
            return "win X"
        if self.tttCheckWin(m, "o"):
            return "win O"
        if self.tttCheckDraw(b):
            return "draw"
        return None

    def tttFindStreaks(self, m: list, xo: str) -> tuple:
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

    def tttFindEmpty(self, matrix: list, rcd: str, n: int) -> int:
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

    def tttCheckWin(self, m: list, xo: str) -> bool:
        row, col, dia = self.tttFindStreaks(m, xo)
        dia.append(0)

        for i in range(3):
            if row[i] == 3 or col[i] == 3 or dia[i] == 3:
                return True

        return False

    def tttCheckDraw(self, board: list) -> bool:
        return " " not in board

    def tttAIThink(self, m: list) -> t.Union[tuple, bool]:
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

    def tttAIMove(self, n: str, m: list, row: list, col: list, dia: list) -> t.Union[tuple, bool]:
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
