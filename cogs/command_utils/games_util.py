import asyncio
import random

import discord
from discord.ext import commands

from cogs.utils import misc
from cogs.utils.embeds import BaseEmbeds


class RPSBase(BaseEmbeds):
    def __init__(self, ctx, content, color=discord.Color.default(),
                 title="Rock Paper Scissors!", rounds=3):
        """Initializes and controls a embed with pagination."""
        super().__init__(ctx, content, color=discord.Color.default(), title="Placeholder Title")

        self.emb = discord.Embed(title=title, color=color)
        self.content = content

        self.react_controls = [
            ("💎", self.rock),
            ("📜", self.paper),
            ("✂️", self.scissor),
            ("\N{BLACK SQUARE FOR STOP}️", self.stop),
        ]

        self.current_round = 0
        self.win_lose = [0, 0]  # index 0 is win | index 1 is lose
        self.total_rounds = rounds
        self.game_state = 0
        self.meta_info = ""

        self.emb.set_footer(text=f"Rounds: {self.current_round}/{self.total_rounds}\n"
                                 f"{self.win_lose[0]} wins | {self.win_lose[1]} losses")

    @staticmethod
    async def rps_to_words(player_one, player_two):
        conversion = str.maketrans({"1": "Rock", "2": "Paper", "3": "Scissor"})
        return str(player_one).translate(conversion), str(player_two).translate(conversion)

    async def is_playing(self):
        if self.instance and self.current_round <= self.total_rounds:
            return True
        else:
            return False

    async def stop(self):
        await super().stop()
        return False

    async def get_content(self):
        # Needs more advanced functionaliies
        # ["Rock Paper Scissors!\nPick a option...", [0]
        # "Congratulations you won the round!" [1]
        # "Oof you lost!", [2]
        # "Tie!", [3]
        # "Congratulations you have won the game!" [4]
        # "Unfortunately you have lost the game.", [5]
        # "Looks like the game was a tie!"] [6]
        return self.content[self.game_state] + self.meta_info

    async def rock(self):
        return 1

    async def paper(self):
        return 2

    async def scissor(self):
        return 3


class RPSBot(RPSBase):
    def __init__(self, ctx, content, color=discord.Color.default(),
                 title="Rock Paper Scissors!", rounds=3):
        """Initializes and controls a embed with pagination."""
        super().__init__(ctx, content, color=discord.Color.default(), title="Placeholder Title")

        self.emb = discord.Embed(title=title, color=color)
        self.content = content

        self.react_controls = [
            ("💎", self.rock),
            ("📜", self.paper),
            ("✂️", self.scissor),
            ("\N{BLACK SQUARE FOR STOP}", self.stop),
        ]

        self.current_round = 0
        self.win_lose = [0, 0]  # index 0 is win | index 1 is lose
        self.total_rounds = rounds
        self.game_state = 0
        self.meta_info = ""

        self.emb.set_footer(text=f"Rounds: {self.current_round}/{self.total_rounds}\n"
                                 f"{self.win_lose[0]} wins | {self.win_lose[1]} losses")

    async def calculate_win(self, bot_choice, player_choice):
        if not player_choice:
            return False, False

        bot_words, player_words = await self.rps_to_words(bot_choice, player_choice)
        if (bot_choice % 3) + 1 == player_choice:
            return True, f" {player_words} beats {bot_words}"
        elif (player_choice % 3) + 1 == bot_choice:
            return False, f" {player_words} is countered by {bot_words}"
        else:
            return None, f""

    async def bot_generate(self):
        return random.randint(1, 3)

    async def start(self):
        self.controller = self.embed_controller(create=True)

        if self.instance:
            self.controller_task = self.ctx.bot.loop.create_task(self.controller)

        while await self.is_playing():
            try:
                control = await self.ctx.bot.wait_for("raw_reaction_add", check=self.invoker, timeout=60)
            except asyncio.TimeoutError:
                return await self.stop()

            try:
                await self.message.remove_reaction(control.emoji, discord.Object(id=control.user_id))
            except (discord.NotFound, discord.Forbidden):
                pass
            try:
                win_lose_drawn, self.meta_info = await self.calculate_win(await self.bot_generate(),
                                                                          await self.control_function())
                if win_lose_drawn is False and self.meta_info is False:
                    break
            except AttributeError:
                return False

            self.current_round += 1
            if await self.is_playing():
                win_table = {True: 1, False: 2, None: 3}
                self.game_state = win_table[win_lose_drawn]
                if win_lose_drawn is True:
                    self.win_lose[0] = self.win_lose[0] + 1
                elif win_lose_drawn is False:
                    self.win_lose[1] = self.win_lose[1] + 1
                else:
                    pass
                self.emb.set_footer(text=f"Rounds: {self.current_round}/{self.total_rounds}\n"
                                         f"{self.win_lose[0]} wins | {self.win_lose[1]} losses")
                await self.embed_controller()

        if self.instance:
            self.meta_info = ""
            if self.win_lose[0] > self.win_lose[1]:
                self.game_state = 4
            elif self.win_lose[0] < self.win_lose[1]:
                self.game_state = 5
            else:
                self.game_state = 6

            await self.embed_controller()
            self.controller_task.cancel()
            try:
                await self.message.clear_reactions()
            except discord.Forbidden:
                pass


class RPSPlayer:
    def __init__(self, user, rounds):
        self.user: discord.User = user
        self.message = None
        self.win_lose = [0, 0]
        self.current_round = 0
        self.total_rounds = rounds

        self.emb = discord.Embed(title="Rock Paper Scissor", color=misc.random_color())
        self.emb.set_footer(text=f"\nRounds: {self.current_round+1}/{self.total_rounds}\n"
                                 f"Wins: {self.win_lose[0]} | Losses: {self.win_lose[1]}")

    async def outfit_embed(self, information):
        self.emb.description = information
        return self.emb

    async def update_footer(self, winlose, rounds):
        self.win_lose, self.current_round = winlose, rounds
        self.emb.set_footer(text=f"\nRounds: {self.current_round}/{self.total_rounds}\n"
                                 f"Wins: {self.win_lose[0]} | Losses: {self.win_lose[1]}")


class RPSMulti(RPSBase):
    def __init__(self, ctx, color=discord.Color.default(),
                 title="Rock Paper Scissors!", rounds=3, players=None):
        """Initializes and controls a embed with pagination."""
        super().__init__(ctx, "None", color=discord.Color.default(), title="Placeholder Title")

        self.emb = discord.Embed(title=title, color=color)

        self.react_controls = [
            ("💎", self.rock),
            ("📜", self.paper),
            ("✂️", self.scissor),
            ("\N{BLACK SQUARE FOR STOP}", self.stop),
        ]

        self.current_round = 0
        self.current_player = 0

        self.win_lose = [0, 0]  # index 0 is win | index 1 is lose
        self.total_rounds = rounds
        self.game_state = 0
        self.game_text = {"starting": "starting...", "pick": "Pick a option...", "await": "Awaiting response from {}",
                          "win": "{} you've won the round!", "lose": "{} lost the round!",
                          "tie": "The round is a tie!", "win_game": "Congratulations you have won the game!",
                          "lose_game": "Unfortunately you have lost the game",
                          "tie_game": "Looks like the game was a tie!"}
        self.meta_info = ""

        self.players = self.order_players(players)
        self.player_responses = {ply.user.mention: None for ply in self.players.values()}

    def get_player(self):
        self.current_player += 1
        if self.current_player > len(self.players) - 1:
            self.current_player = 0
        return self.players[self.current_player]

    def peek_player(self):
        return self.players[self.current_player]

    def order_players(self, players):
        return {index: RPSPlayer(user, self.total_rounds) for index, user in enumerate(players)}

    def reset_responses(self):
        self.player_responses = {ply.user.mention: None for ply in self.players.values()}

    def format_string(self, get, fmt=None):
        if fmt:
            return self.game_text[get].format(fmt)
        else:
            return self.game_text[get]

    async def ensure_responses(self, response):
        ply = self.peek_player()
        self.player_responses[ply.user.mention] = response
        if len([null for null in self.player_responses.values() if null is not None]) != len(self.players.values()):
            return False
        else:
            return True

    async def calculate_win(self):
        def calc_win(first_player, second_player):
            """Calculates winner
            If resulting winner is player_one then returns 0
            If resulting winnner is player_two returns 1
            if tied returns 2
            """
            if (second_player % 3) + 1 == first_player:
                return 0
            elif (first_player % 3) + 1 == second_player:
                return 1
            else:
                return 2

        responses = self.player_responses.values()
        plys = [key for key in self.player_responses.keys()]
        self.reset_responses()

        result = calc_win(*responses)
        player_one_words, player_two_words = await self.rps_to_words(*responses)
        if result is 0:
            return True, f"{plys[0]}'s {player_one_words} beats {plys[1]}'s {player_two_words}"
        elif result is 1:
            return False, f"{plys[0]}'s {player_one_words} is countered by {plys[1]}'s {player_two_words}"
        else:
            return None, False

    async def embed_controller(self, create=False, send_or_await="", *args, sp=False):
        if sp is False:
            player = self.peek_player()
        else:
            player = self.players[sp]
        await player.outfit_embed(self.format_string(send_or_await, *args))

        if create is False:
            try:
                await player.message.edit(embed=player.emb)
            except discord.Forbidden:
                raise commands.BotMissingPermissions("Embed Links!")
        else:
            try:
                player.message = await player.user.send(embed=player.emb)
            except discord.Forbidden:
                raise commands.BotMissingPermissions(f"DM {player.user.mention}")

            for user_input_buttons in self.react_controls:
                try:
                    await player.message.add_reaction(user_input_buttons[0])
                except (discord.NotFound, discord.Forbidden):
                    pass

    async def send_win_lose(self, win_lose):
        if win_lose is True:
            first_data, second_data = "win", "lose"

        elif win_lose is False:
            first_data, second_data = "lose", "win"
        else:
            first_data, second_data = "tie", "tie"

        await self.players[0].update_footer(self.win_lose, self.current_round)
        await self.players[1].update_footer(self.win_lose[::-1], self.current_round)
        await self.embed_controller(False, first_data, self.players[0].user.mention, sp=0)
        await self.embed_controller(False, second_data, self.players[1].user.mention, sp=1)

    async def send_await(self):
        wait = None  # Placeholder
        for player, response in self.player_responses.items():
            if response is None:
                wait = player
                break
        for _ in self.players:
            await self.embed_controller(False, "await", wait)

    def invoker(self, reaction):
        if (reaction.user_id in [ply.user.id for ply in self.players.values()] and
           str(reaction.emoji) == "\N{BLACK SQUARE FOR STOP}"):
            self.control_function = self.stop
            return True

        if (reaction.user_id != self.peek_player().user.id or
            reaction.message_id != self.peek_player().message.id
        ):
            return False
        for react_controls, functionality in self.react_controls:
            if str(reaction.emoji) == react_controls:
                self.control_function = functionality
                return True

    async def cancel(self, *args):
        self.instance = False
        for user in self.players.values():
            await user.outfit_embed("Game has eneded because a player quit!")
            await user.message.edit(embed=user.emb)

    async def start(self):
        for _ in self.players:
            self.get_player()
            await self.embed_controller(create=True, send_or_await="starting")
        self.current_player += 1
        await self.send_await()

        while await self.is_playing():
            ply = self.get_player()
            await self.embed_controller(create=False, send_or_await="pick")

            try:
                control = await self.ctx.bot.wait_for("raw_reaction_add", check=self.invoker, timeout=60)
            except asyncio.TimeoutError:
                await self.stop()
                break

            try:
                await ply.message.remove_reaction(control.emoji, discord.Object(id=control.user_id))
            except (discord.NotFound, discord.Forbidden):
                pass
            if await self.ensure_responses(await self.control_function()) is True and self.instance:
                try:
                    win_lose_drawn, self.meta_info = await self.calculate_win()
                    if win_lose_drawn is False and self.meta_info is False:
                        break
                except AttributeError:
                    return False

                self.current_round += 1
                if await self.is_playing():
                    if win_lose_drawn is True:
                        self.win_lose[0] += 1
                    elif win_lose_drawn is False:
                        self.win_lose[1] += 1
                    else:
                        pass
                    await self.send_win_lose(win_lose_drawn)
                    await asyncio.sleep(1.5)
                    await self.send_await()
            elif self.instance:
                await self.send_await()

        if self.instance:
            if self.win_lose[0] > self.win_lose[1]:
                ply_1, ply_2 = "win_game", "lose_game"
            elif self.win_lose[0] < self.win_lose[1]:
                ply_1, ply_2 = "lose_game", "win_game"
            else:
                ply_1, ply_2 = ["tie_game"]*2

            await self.embed_controller(send_or_await=ply_1, sp=0)
            await self.embed_controller(send_or_await=ply_2, sp=1)
