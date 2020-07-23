import random
import re
import typing as t
from collections import defaultdict
from os import path

from discord import Color, Embed, Guild, Member, Message, TextChannel
from discord.ext.commands import Cog, Context, command

from bot import config
from bot.core.bot import Bot

DIR_PATH = path.dirname(__file__)
# TODO: Define global hangman players


class HangmanGame:
    with open(path.join(DIR_PATH, "hangman_stages.txt"), "r") as f:
        stages = f.read().split("\n\n")

    with open(path.join(DIR_PATH, "hangman_words.txt"), "r") as f:
        word_list = []
        for line in f:
            word_list.append(line.replace("\n", ""))

    letter_pattern = re.compile(r"[A-z]")

    players = defaultdict(lambda: defaultdict(list))

    def __init__(self, bot: Bot, guild: Guild, channel: TextChannel, player: Member, word: str) -> None:
        self.bot = bot
        self.guild = guild
        self.channel = channel
        self.player = player
        self.word = word.upper()
        self.guesses = []
        self.tries = 6

    async def get_guess(self) -> str:
        """Accept a guess from the user"""
        def input_check(msg: Message) -> bool:
            return msg.author == self.player and msg.channel == self.channel

        guess = await self.bot.wait_for("message", check=input_check)
        content = guess.content.upper()
        await guess.delete()
        return content

    async def apply_guess(self, guess: str) -> t.Literal[0, 1, 2, 3, False]:
        """
        Return the guess status.

        Statuses:
        `0` = Incorrect guess (not in word)
        `1` = Correct guess (in word)
        `2` = Bad guess (not a single letter)
        `3` = Already guessed
        """
        if HangmanGame.letter_pattern.fullmatch(guess):
            if guess in self.guesses:
                return 3

            self.guesses.append(guess)

            if guess in self.word:
                return 1
            else:
                self.tries -= 1
                return 0
        else:
            if guess == f"{config.COMMAND_PREFIX}HANGEXIT":
                return False
            else:
                return 2

    @property
    def display_word(self) -> str:
        """Covered word."""
        display_word = ""
        for letter in self.word:
            if letter in self.guesses:
                display_word += letter
            else:
                display_word += "#"
        return display_word

    async def send_status(self, guess: t.Optional[str] = None, guess_status: t.Optional[t.Literal[0, 1, 2, 3]] = None) -> None:
        """Get current game status as embed."""
        embed = Embed(
            title="Hangman",
            color=Color.dark_green(),
        )
        embed.add_field(
            name="**❯❯ Status**",
            value=f"```\n{HangmanGame.stages[self.tries]}```",
            inline=False
        )
        embed.add_field(
            name="**❯❯ Word**",
            value=f"**{self.display_word}**",
            inline=False
        )
        if guess:
            description = f"Letter {guess}"
            if guess_status == 0:
                description += " isn't in the word"
                color = Color.red()
            elif guess_status == 1:
                description += " is in the word"
                color = Color.green()
            elif guess_status == 2:
                description += " isn't valid"
                color = Color.dark_red()
            elif guess_status == 3:
                description += " was already guessed."
                color = Color.dark_red()
            guess_embed = Embed(
                description=description,
                color=color
            )
            await self.channel.send(embed=guess_embed, delete_after=5)
        embed.set_footer(
            text=f"{config.COMMAND_PREFIX}hangexit to exit the game! | Powered By HotWired."
        )
        if hasattr(self, "message"):
            await self.message.edit(embed=embed)
        else:
            self.message = await self.channel.send(embed=embed)

    def is_finished(self) -> t.Literal[0, 1, 2]:
        """
        Return finish state of the game.

        `0` = In progress
        `1` = Win
        `2` = Lose
        """
        if set(self.word).issubset(set(self.guesses)):

            return 1
        elif self.tries <= 0:
            return 2
        else:
            return 0

    async def play(self) -> None:
        """Start the main game loop."""
        await self.send_status()
        HangmanGame.players[self.guild][self.channel].append(self.player)
        while self.player in HangmanGame.players[self.guild][self.channel]:
            guess = await self.get_guess()
            guess_status = await self.apply_guess(guess)
            if guess_status is False:
                embed = Embed(
                    title="Game aborted",
                    description="You aborted the game.",
                    color=Color.dark_red()
                )
                await self.channel.send(embed=embed)
                return
            await self.send_status(guess, guess_status)
            state = self.is_finished()
            if state > 0:
                if state == 1:
                    embed = Embed(
                        title="You won",
                        description=":tada: You won the game!",
                        color=Color.green()
                    )
                    await self.channel.send(embed=embed)
                elif state == 2:
                    embed = Embed(
                        title="You lost",
                        description="You ran out of guesses.",
                        color=Color.green()
                    )
                    await self.channel.send(embed=embed)
                return

    @classmethod
    def random(cls, ctx: Context) -> "HangmanGame":
        """Create a game with random word"""
        word = random.choice(HangmanGame.word_list)
        return cls(ctx.bot, ctx.guild, ctx.channel, ctx.author, word)


class Hangman(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def hangman(self, ctx: Context) -> None:
        """Play game of Hangman."""
        hangman_game = HangmanGame.random(ctx)
        await hangman_game.play()
