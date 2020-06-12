import random
import discord
from discord.ext import commands

from assets.context import Command, argument, example, usage_info
from cogs.command_utils import games_util
from typing import Union


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

    @commands.command(aliases=['cflip'])
    async def coinflip(self, ctx):
        await ctx.send(random.choice(["Heads", "Tails", "Sideways"]))

    @commands.command(cls=Command,
                      description="Play a round of rock paper scissors with the bot or another user!",
                      syntax=[argument(False, "Rounds | Defaults to 3"), argument(False, "2nd Player")],
                      usage_information=[
                          usage_info("", "• If 2nd player isn't set then the game will be played against the bot"),
                          usage_info("", "\n• A DM would be sent to the 2nd player asking "
                                         "if they want to join unless they disabled bot invitations"),
                      ],
                      examples=[
                          example("10", "Plays a game of RPS with the bot that has 10 rounds"),
                          example("3 @usermention", "A game of RPS with usermention that has 3 rounds")
                      ])
    async def rps(self, ctx, rounds: Union[int, None] = 3, player: Union[discord.Member, str] = None):
        if rounds is None:
            return await ctx.send("Invalid amount of rounds!")
        if not player:
            singleplayer_text = [" Rock Paper Scissors!\nPick a option...", " Congratulations you've won the round!",
                                 "Oof you've lost the round!", "The round is a tie!",
                                 "Congratulations you have won the game!", "Unfortunately you have lost the game",
                                 "Looks like the game was a tie!"]
            game_instance = games_util.RPSBot(ctx, singleplayer_text, rounds=rounds)
            await game_instance.start()
        elif isinstance(player, str) or (ctx.guild and player.guild.id != ctx.guild.id):
            return await ctx.send("The second player must be within the same server! ")
        else:
            await ctx.send(f"Awaiting confirmation by {player}...")

            accept = await ctx.confirm_another(player, title=f"Invitation to play rock paper scissors!",
                                               content=[f"{ctx.author.mention} has invited you to play a "
                                                        f"game of rock paper scissors with {rounds} "
                                                        f"rounds do you accept?"])
            if not accept:
                return await ctx.send(f"{player.name} has declined!")

            game_instance = games_util.RPSMulti(ctx, rounds=rounds, players=[ctx.author, player])
            await game_instance.start()
            await ctx.send("Game ended!")


def setup(client):
    client.add_cog(Games(client))
