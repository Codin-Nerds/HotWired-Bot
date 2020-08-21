import random
import typing as t
from itertools import cycle

import discord
from discord.ext import commands
from discord.ext import menus


class TTT_Game(menus.Menu):
    """Tic-tac-Toe menu."""

    emojis = [
        ":black_large_square:",
        ":o:",
        ":x:",
    ]

    def __init__(self, author: discord.Member, opponent: t.Optional[discord.Member], **kwargs) -> None:
        super().__init__(**kwargs)
        self.players = (author, opponent)
        self.player_cycle = cycle(self.players)
        self.next_player = next(self.player_cycle)
        self.is_ia = bool(opponent)
        self.status = [[0] * 3 for _ in range(3)]

    def reaction_check(self, payload: discord.RawReactionActionEvent) -> bool:
        """Whether or not to process the payload."""
        if payload.message_id != self.message.id:
            return False
        if not self.next_player:
            return False
        return payload.user_id == self.next_player.id and payload.emoji in self.buttons

    async def send_initial_message(self, ctx: commands.Context, channel: discord.TextChannel) -> discord.Message:
        """Send the first message."""
        return await ctx.send(embed=self.get_embed())

    def get_embed(self) -> discord.Embed:
        """Generate the board embed."""
        return discord.Embed(
            title="Tic Tac Toe",
            description="\n".join(
                (
                    "".join(
                        self.emojis[state] for state in column
                    ) for column in self.status
                )
            ),
            color=discord.Color.blurple(),
        )

    async def action(self, row: int, column: int) -> None:
        """Play in the given place."""
        if self.status[row][column]:
            await self.ctx.send(
                f"{self.next_player.mention}, you can't play here !",
                delete_after=3,
            )
        self.status[row][column] = self.players.index(self.next_player) + 1
        await self.update_board()

    async def update_board(self) -> None:
        """Update the board, and check for win."""
        await self.message.edit(embed=self.get_embed())
        self.next_player = next(self.player_cycle)
        if await self.check():
            return
        if not self.next_player:
            await self.cpu_move()

    async def send_result(self, result: int) -> None:
        """Send the final result message."""
        if result == -1:
            await self.ctx.send("Game result: draw")
        elif self.is_ia:
            if result:
                await self.ctx.send(
                    f":tada: Congratulations {self.players[0].mention}, you won !"
                )
            else:
                await self.ctx.send(
                    f"You lost {self.players[0].mention}, better luck next time!"
                )
        else:
            await self.ctx.send(
                f":tada: Congratulations {self.players[result].mention}, you won !"
            )
        await self.stop()

    async def cpu_move(self) -> None:
        """Make the computer move."""
        for row in range(3):
            if 0 in self.status[row]:
                if self.status[row].count(2) == 2 or self.status[row].count(1) == 2:
                    return await self.action(row, self.status[row].index(0))

        for column_id in range(3):
            column = [self.status[row_id][column_id] for row_id in range(3)]
            if 0 in column:
                if column.count(1) == 2 or column.count(2) == 2:
                    return await self.action(column.index(0), column_id)

        diag_1 = [self.status[place_id][place_id] for place_id in range(3)]
        if 0 in diag_1:
            if diag_1.count(1) == 2 or diag_1.count(2) == 2:
                return await self.action(diag_1.index(0), diag_1.index(0))

        diag_2 = [self.status[2 - place_id][place_id] for place_id in range(3)]
        if 0 in diag_2:
            if diag_2.count(1) == 2 or diag_2.count(2) == 2:
                return await self.action(2 - diag_2.index(0), diag_2.index(0))

        possible_moves = []
        for row in range(3):
            for column in range(3):
                if not self.status[row][column]:
                    possible_moves.append((row, column))
        await self.action(*random.choice(possible_moves))

    async def check(self) -> bool:
        """Check if somebody won."""
        all_checks = []
        # rows
        for row in self.status:
            all_checks.append(row)
        # columns
        for column_id in range(3):
            all_checks.append([self.status[row_id][column_id] for row_id in range(3)])
        # diagonals
        all_checks.append([self.status[place_id][place_id] for place_id in range(3)])
        all_checks.append([self.status[2 - place_id][place_id] for place_id in range(3)])

        for to_check in all_checks:
            if to_check.count(1) == 3:
                await self.send_result(0)
                return True
            if to_check.count(2) == 3:
                await self.send_result(1)
                return True
        if not any(0 in row for row in self.status):
            await self.send_result(-1)
            return True
        return False

    @menus.button("\N{north west arrow}\N{variation selector-16}")
    async def top_left(self, payload: discord.RawReactionActionEvent) -> None:
        """Top left button."""
        await self.action(0, 0)

    @menus.button("\N{upwards black arrow}\N{variation selector-16}")
    async def top(self, payload: discord.RawReactionActionEvent) -> None:
        """Top button."""
        await self.action(0, 1)

    @menus.button("\N{north east arrow}\N{variation selector-16}")
    async def top_right(self, payload: discord.RawReactionActionEvent) -> None:
        """Top right button."""
        await self.action(0, 2)

    @menus.button("\N{leftwards black arrow}\N{variation selector-16}")
    async def left(self, payload: discord.RawReactionActionEvent) -> None:
        """Left button."""
        await self.action(1, 0)

    @menus.button("\N{black circle for record}\N{variation selector-16}")
    async def middle(self, payload: discord.RawReactionActionEvent) -> None:
        """Middle button."""
        await self.action(1, 1)

    @menus.button("\N{black rightwards arrow}\N{variation selector-16}")
    async def right(self, payload: discord.RawReactionActionEvent) -> None:
        """Right button."""
        await self.action(1, 2)

    @menus.button("\N{south west arrow}\N{variation selector-16}")
    async def bottom_left(self, payload: discord.RawReactionActionEvent) -> None:
        """Bottom left button."""
        await self.action(2, 0)

    @menus.button("\N{downwards black arrow}\N{variation selector-16}")
    async def down(self, payload: discord.RawReactionActionEvent) -> None:
        """Down button."""
        await self.action(2, 1)

    @menus.button("\N{south east arrow}\N{variation selector-16}")
    async def bottom_right(self, payload: discord.RawReactionActionEvent) -> None:
        """Bottom right button."""
        await self.action(2, 2)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload: discord.RawReactionActionEvent) -> None:
        """Stop button."""
        await self.stop()
