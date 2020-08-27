import aiohttp
import random
import asyncio
from bot.utils.messagepredicate import MessagePredicate

from discord import Color, Embed, Member
from discord.ext.commands import Cog, Context, command, group
from discord.ext import tasks

from bot import config
from bot.core.bot import Bot

from .hangman import HangmanGame
from .tic_tac_toe import TTT_Game
from .more_games import Connect4, Blackjack, Blackjack_players

from .poker import Card, Deck


class Games(Cog):
    """We all love playing games."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.blackjack_list = []
        self.blackjack_updater.start()

        self._in_game = {}
        self._hit = {}
        self.player_deck = Deck()
        self.dealer_deck = Deck()

    def cog_unload(self) -> None:
        self.blackjack_updater.cancel()

    @tasks.loop(seconds=5)
    async def blackjack_updater(self) -> None:
        new = []
        for black in self.blackjack_list:
            if black.current_state == 1:
                await black.updater()
            elif black.current_state == -1:
                continue
            new.append(black)
        self.blackjack_list = new

    @command(ignore_extra=True)
    async def blackjack(self, ctx: Context, cost: int = 5) -> None:
        """
        Rules: if it's your turn, press the button corresponding to the column in which you want to place the card.
        If you want to split (play on one more column, up to a max of 3, press :regional_indicator_3:).  If you want to stop, press :x:.
        To win, you must score more than the dealer, but no more than 21 (each card's value is its pip value,
        except for faces, which are worth 10 points, and the Ace, which is worth either 1 or 11).
        An Ace plus a face is called a blackjack and beats a 21
        """
        if cost < 0:
            await ctx.send("You can't bet negative money")
        players, money_dict = await Blackjack_players(ctx.author, 100, cost, delete_message_after=True).prompt(ctx)
        if not players:
            return await ctx.send("Nobody wants to play")
        await Blackjack(players, money_dict, cost, clear_reactions_after=True).prompt(ctx)

    @command(aliases=["c4"])
    async def connect4(self, ctx: Context, member: Member) -> None:
        """Play connect 4 with a friend"""
        winner = await Connect4(ctx.author, member, clear_reactions_after=True).prompt(ctx)
        if winner:
            await ctx.send(f"{winner.mention} won !")
        else:
            await ctx.send("Game cancelled")

    @command()
    async def hangman(self, ctx: Context) -> None:
        """Play game of Hangman."""
        hangman_game = HangmanGame.random(ctx)
        await hangman_game.play()

    @command(aliases=["ttt", "tictactoe"])
    async def tic_tac_toe(self, ctx: Context, opponent: Member = None) -> None:
        """Play a game of Tic-Tac-Toe."""
        game = TTT_Game(ctx.author, opponent, clear_reactions_after=True)
        await game.start(ctx)

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
        """Ask the all-knowing 8ball your burning questions."""
        reply_type = random.randint(1, 3)

        if reply_type == 1:
            answer = random.choice(config.POSITIVE_REPLIES)
        elif reply_type == 2:
            answer = random.choice(config.NEGATIVE_REPLIES)
        elif reply_type == 3:
            answer = random.choice(config.ERROR_REPLIES)

        embed = Embed(title="Magic 8-ball", color=Color.blurple())
        embed.add_field(name="Question", value=question)
        embed.add_field(name="Answer", value=answer)

        await ctx.send(embed=embed)

    @command(aliases=["pokesearch"])
    async def pokemon(self, ctx: Context, pokemon: str) -> None:
        """
        Fetches data about a given pokemon eg. `pokemon pikachu`.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}") as resp:
                data = await resp.json()

        pokemon_embed = Embed(
            title=f"{pokemon.capitalize()} Info",
            color=Color.blurple()
        )

        ability_names = [f"`{ability['ability']['name']}`" for ability in data["abilities"]]
        pokemon_types = [f"`{ptype_raw['type']['name']}`" for ptype_raw in data["types"]]
        base_stat_names = ["Hp", "Attack", "Defence", "Special-Attack", "Special-Defence", "Speed"]
        base_stats_zip = zip(base_stat_names, data["stats"])
        base_stats = [f"**{stat_name}**: `{str(base_stat_dict['base_stat'])}`" for stat_name, base_stat_dict in base_stats_zip]

        pokemon_embed.set_thumbnail(url=data["sprites"]["front_default"])
        pokemon_embed.add_field(name="❯❯Base Stats", value="\n ".join(base_stats))
        pokemon_embed.add_field(name="❯❯Type", value="\n".join(pokemon_types))
        pokemon_embed.add_field(name="❯❯Weight", value=f"`{str(data['weight'])}`")
        pokemon_embed.add_field(name="❯❯Abilities", value="\n".join(ability_names), inline=True)

        await ctx.send(embed=pokemon_embed)

    @command(aliases=["wyr"])
    async def wouldyourather(self, ctx: Context) -> None:
        """Would you rather?."""
        strings = config.talk_games["wyr"]
        choices = len(strings)
        i = random.randint(0, choices - 1)

        embed = Embed(
            title="Would you rather?",
            description=f"Would you rather ..{strings[i]}",
            color=Color.dark_magenta()
        )
        await ctx.send(embed=embed)

    @command(aliases=["havei"])
    async def haveiever(self, ctx: Context) -> None:
        """Have i Ever?."""
        strings = config.talk_games["nhie"]
        choices = len(strings)
        i = random.randint(0, choices - 1)

        embed = Embed(
            title="Have I ever?",
            description=f"Have you ever ..{strings[i]}",
            color=Color.dark_magenta()
        )
        await ctx.send(embed=embed)

    @command()
    async def truth(self, ctx: Context, *, user: Member) -> None:
        """Ask a truth question to a random user."""
        strings = config.talk_games["truths"]
        str_len = len(strings)
        random_truth = random.randint(0, str_len - 1)

        # TODO: choose only non-offline users
        member_len = len(ctx.guild.members)
        random_user = random.randint(0, member_len - 1)
        name = ctx.guild.members[random_user].mention

        embed = Embed(
            title=f"{ctx.author.name} asked {user.name}",
            description=strings[random_truth].format(name=name),
            color=Color.dark_magenta()
        )
        await ctx.send(embed=embed)

    @command()
    async def dare(self, ctx: Context, *, user: Member) -> None:
        """Dare someone."""
        strings = config.talk_games["dares"]
        str_len = len(strings)
        random_dare = random.randint(0, str_len - 1)

        # TODO: choose only non-offline users
        member_len = len(ctx.guild.members)
        random_user = random.randint(0, member_len - 1)
        name = ctx.guild.members[random_user].mention

        embed = Embed(
            title=f"{ctx.author.name} dared {user.name}",
            description=strings[random_dare].format(name=name),
            color=Color.dark_magenta()
        )
        await ctx.send(embed=embed)

    @group()
    async def poker(self, ctx: Context) -> None:
        """The Luigi Poker minigame from New Super Mario Brothers."""
        if ctx.invoked_subcommand is None:
            space = "\N{EN SPACE}"
            msg = (
                f"I'm Luigi, Number 1!\n"
                f"This game plays the same as Luigi's "
                f"Poker in Super Mario 64 DS Minigames.\n"
                f"The card's worth is based on the suit.\n"
                f"Starman > Mario > Luigi > Fire Flower > Mushroom > Cloud.\n"
                f"{space*3}{Card(6)}{space*4}>{space*3}{Card(5)}{space*3}>{space*3}{Card(4)}{space*3}"
                f">{space*6}{Card(3)}{space*6}>{space*4}{Card(2)}{space*5}>{space*4}{Card(1)}\n"
                f"---------------------------------------------------------\n"
                f"The following table represents the winning matches.\n"
                f"For example, a Full House is greater than Three of a Kind, but "
                f"less than a Four of a Kind.\n"
                f"---------------------------------------------------------\n"
                f"Flush:           {Card(6)}{Card(6)}{Card(6)}{Card(6)}{Card(6)}\n"
                f"Four of a Kind:  {Card(6)}{Card(6)}{Card(6)}{Card(6)}\n"
                f"Full House:      {Card(6)}{Card(6)}{Card(6)}{Card(3)}{Card(3)}\n"
                f"Three of a Kind: {Card(6)}{Card(6)}{Card(6)}\n"
                f"Two Pairs:       {Card(6)}{Card(6)}{Card(2)}{Card(2)}\n"
                f"Pair:            {Card(6)}{Card(6)}\n"
            )
            await ctx.send(
                embed=Embed(
                    title="How to play Luigi Poker?",
                    description=msg,
                    color=Color.blue()
                )
            )
            return await ctx.send(
                f"Are you ready to play my game?! What are you waiting for? Start the game using `{ctx.prefix}poker play`!"
            )

    @poker.command()
    async def play(self, ctx):
        """Starts the Game!"""
        if not self._in_game.get(ctx.guild.id, False):
            self._in_game[ctx.guild.id] = True
            self.player_deck.new_deck()
            self.dealer_deck.new_deck()
        else:
            return await ctx.send("You're already in a game...")

        square = "\N{WHITE MEDIUM SMALL SQUARE}"
        msg = (
            f"Dealer's Deck: {square*5}\n"
            f"Your Deck:     {self.player_deck.suit(0)}{self.player_deck.suit(1)}"
            f"{self.player_deck.suit(2)}{self.player_deck.suit(3)}{self.player_deck.suit(4)}"
        )

        await ctx.send(
            embed=Embed(
                description=msg,
                color=Color.blue()
            )
        )

        if self._hit.get(ctx.guild.id, False):
            await ctx.send("`Stay` or `fold`?")
            answers = ["stay", "fold"]
        else:
            await ctx.send("`Stay`, `hit`, or `fold`?")
            answers = ["stay", "hit", "fold"]
        await self._play_response(ctx, answers)

    async def _play_response(self, ctx, answers):
        pred = MessagePredicate.lower_contained_in(answers, ctx=ctx)
        try:
            user_resp = await ctx.bot.wait_for("message", timeout=120, check=pred)
        except asyncio.TimeoutError:
            await ctx.send("No response.")
            return await self.fold(ctx)
        if "stay" in user_resp.content.lower():
            return await self.stay(ctx)
        elif "hit" in user_resp.content.lower():
            return await self.hit(ctx)
        elif "fold" in user_resp.content.lower():
            return await self.fold(ctx)
        else:
            print(
                "LuigiPoker: Something broke unexpectedly in _play_response. Please report it."
            )

    async def hit(self, ctx):
        await ctx.send(
            "What cards do you want to swap out?\n"
            "Use numbers 1 through 5 to specify, with commas in between.\n"
            "Examples: `1,3,5` or `4, 5`"
        )
        try:
            user_resp = await ctx.bot.wait_for(
                "message", timeout=60, check=MessagePredicate.same_context(ctx)
            )
        except asyncio.TimeoutError:
            await ctx.send("No response.")
            return await self.fold(ctx)

        user_answers = user_resp.content.strip().split(",")
        user_answers_valid = list(set(user_answers) & set(["1", "2", "3", "4", "5"]))
        if len(user_answers_valid) == 0:
            return await self.hit(ctx)

        await ctx.send("Swapping Cards...")
        self.player_deck.swap(user_answers_valid)
        square = "\N{WHITE MEDIUM SMALL SQUARE}"
        msg = (
            f"Dealer's Deck: {square*5}\n"
            f"Your Deck:     {self.player_deck.suit(0)}{self.player_deck.suit(1)}"
            f"{self.player_deck.suit(2)}{self.player_deck.suit(3)}{self.player_deck.suit(4)}"
        )
        await ctx.send(
            embed=Embed(
                description=msg,
                color=Color.blue()
            )
        )
        await ctx.send("`Stay` or `fold`?")
        self._hit[ctx.guild.id] = True
        answers = ["stay", "fold"]
        await self._play_response(ctx, answers)

    async def fold(self, ctx):
        msg = "You have folded.\n"
        msg += (
            f"```Dealer's Deck: {self.dealer_deck.suit(0)}{self.dealer_deck.suit(1)}"
            f"{self.dealer_deck.suit(2)}{self.dealer_deck.suit(3)}{self.dealer_deck.suit(4)}\n"
            f"Your Deck:     {self.player_deck.suit(0)}{self.player_deck.suit(1)}"
            f"{self.player_deck.suit(2)}{self.player_deck.suit(3)}{self.player_deck.suit(4)}```"
        )

        self._in_game[ctx.guild.id] = False
        self._hit[ctx.guild.id] = False
        await ctx.send(msg)

    async def stay(self, ctx):
        say = ""
        win = False
        same_move = False
        tied = False

        # Flush
        if self.flush(self.player_deck) != self.flush(self.dealer_deck):
            say = "a Flush"
            if self.flush(self.player_deck):
                win = True
        elif self.flush(self.player_deck) and self.flush(self.dealer_deck):
            say = "Flush"
            same_move = True
            if self.player_deck.first_pair > self.dealer_deck.first_pair:
                win = True
            elif self.player_deck.first_pair == self.dealer_deck.first_pair:
                tied = True

        # Four of a Kind
        elif self.four_of_a_kind(self.player_deck) != self.four_of_a_kind(self.dealer_deck):
            say = "a Four of a Kind"
            if self.four_of_a_kind(self.player_deck):
                win = True
        elif self.four_of_a_kind(self.player_deck) and self.four_of_a_kind(self.dealer_deck):
            say = "Four of a Kind"
            same_move = True
            if self.player_deck.first_pair > self.dealer_deck.first_pair:
                win = True
            elif self.player_deck.first_pair == self.dealer_deck.first_pair:
                tied = True

        # Full House
        elif self.full_house(self.player_deck) != self.full_house(self.dealer_deck):
            say = "a Full House"
            if self.full_house(self.player_deck):
                win = True
        elif self.full_house(self.player_deck) and self.full_house(self.dealer_deck):
            say = "Full House"
            same_move = True
            if self.player_deck.first_pair > self.dealer_deck.first_pair:
                win = True
            elif self.player_deck.second_pair > self.dealer_deck.second_pair:
                win = True
            elif (
                self.player_deck.first_pair == self.dealer_deck.first_pair and self.player_deck.second_pair == self.dealer_deck.second_pair
            ):
                tied = True

        # Full House
        elif self.three_of_a_kind(self.player_deck) != self.three_of_a_kind(self.dealer_deck):
            say = "a Three of a Kind"
            if self.three_of_a_kind(self.player_deck):
                win = True
        elif self.three_of_a_kind(self.player_deck) and self.three_of_a_kind(self.dealer_deck):
            say = "Three of a Kind"
            same_move = True
            if self.player_deck.first_pair > self.dealer_deck.first_pair:
                win = True
            elif self.player_deck.first_pair == self.dealer_deck.first_pair:
                tied = True

        # Two Pairs
        elif self.two_pair(self.player_deck) != self.two_pair(self.dealer_deck):
            say = "Two Pairs"
            if self.two_pair(self.player_deck):
                win = True
        elif self.two_pair(self.player_deck) and self.two_pair(self.dealer_deck):
            say = "Two Pairs"
            same_move = True
            if self.player_deck.first_pair > self.dealer_deck.first_pair:
                win = True
            elif self.player_deck.second_pair > self.dealer_deck.second_pair:
                win = True
            elif (
                self.player_deck.first_pair == self.dealer_deck.first_pair and self.player_deck.second_pair == self.dealer_deck.second_pair
            ):
                tied = True

        # One Pair
        elif self.one_pair(self.player_deck) != self.one_pair(self.dealer_deck):
            say = "a Pair"
            if self.one_pair(self.player_deck):
                win = True
        elif self.one_pair(self.player_deck) and self.one_pair(self.dealer_deck):
            say = "Pair"
            same_move = True
            if self.player_deck.first_pair > self.dealer_deck.first_pair:
                win = True
            elif self.player_deck.first_pair == self.dealer_deck.first_pair:
                tied = True
        else:
            tied = True

        msg = "You've stayed.\n"

        if same_move:
            if win:
                msg += f"You won! Your {say} is greater than Dealer's {say}!"
            else:
                msg += f"You lost! The Dealer's {say} is greater than your {say}!"
        elif win:
            msg += f"You won! You got {say}!"
        elif tied:
            msg += "Both the Dealer and the Player have tied."
        else:
            msg += f"You lost! The Dealer got {say}."

        msg += (
            f"```Dealer's Deck: {self.dealer_deck.suit(0)}{self.dealer_deck.suit(1)}"
            f"{self.dealer_deck.suit(2)}{self.dealer_deck.suit(3)}{self.dealer_deck.suit(4)}\n"
            f"Your Deck:     {self.player_deck.suit(0)}{self.player_deck.suit(1)}"
            f"{self.player_deck.suit(2)}{self.player_deck.suit(3)}{self.player_deck.suit(4)}```"
        )
        self._in_game[ctx.guild.id] = False
        self._hit[ctx.guild.id] = False
        await ctx.send(msg)

    @staticmethod
    def one_pair(deck):
        answer = False
        for x in range(0, deck.len() - 1):
            if deck.num(x) == deck.num(x + 1):
                deck.first_pair = deck.num(x)
                answer = True

        return answer

    @staticmethod
    def two_pair(deck):
        answer = False
        first_pair = 0
        second_pair = 0

        for x in range(0, deck.len() - 1):
            if deck.num(x) == deck.num(x + 1):
                if first_pair == 0:
                    first_pair = deck.num(x)
                elif first_pair != deck.num(x) and second_pair == 0:
                    second_pair = deck.num(x)

        if first_pair != 0 and second_pair != 0:
            deck.first_pair = first_pair
            deck.second_pair = second_pair
            answer = True

        return answer

    @staticmethod
    def three_of_a_kind(deck):
        answer = False
        for x in range(0, deck.len() - 2):
            if deck.num(x) == deck.num(x + 1) and deck.num(x + 1) == deck.num(x + 2):
                deck.first_pair = deck.num(x)
                answer = True

        return answer

    @staticmethod
    def full_house(deck):
        answer = False
        first_pair = 0
        second_pair = 0
        for x in range(0, deck.len() - 2):
            if deck.num(x) == deck.num(x + 1) and deck.num(x + 1) == deck.num(x + 2):
                if first_pair == 0:
                    first_pair = deck.num(x)
        for x in range(0, deck.len() - 1):
            if deck.num(x) == deck.num(x + 1):
                if first_pair != deck.num(x) and second_pair == 0:
                    second_pair = deck.num(x)

        if first_pair != 0 and second_pair != 0:
            deck.first_pair = first_pair
            deck.second_pair = second_pair
            answer = True

        return answer

    @staticmethod
    def four_of_a_kind(deck):
        answer = False
        for x in range(0, deck.len() - 3):
            if (
                deck.num(x) == deck.num(x + 1) and deck.num(x + 1) == deck.num(x + 2) and deck.num(x + 2) == deck.num(x + 3)
            ):
                deck.first_pair = deck.num(x)
                answer = True

        return answer

    @staticmethod
    def flush(deck):
        answer = False
        x = 0
        if (
            deck.num(x) == deck.num(x + 1)
            and deck.num(x + 1) == deck.num(x + 2)
            and deck.num(x + 2) == deck.num(x + 3)
            and deck.num(x + 3) == deck.num(x + 4)
        ):
            deck.first_pair = deck.num(x)
            answer = True

        return answer
