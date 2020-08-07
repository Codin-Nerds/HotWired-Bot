import asyncio

import aiohttp

from collections import defaultdict

from discord import Color, Embed, Message
from discord.ext.commands import Cog, Context, group

from bot.core.bot import Bot
from bot import config


def convert_markdown(in_string: str) -> str:
    """Replaces markdown with its intended symbol."""
    pass_one = in_string.replace("&quot;", '"').replace("&#039;", "''").replace("\\", "")
    pass_two = pass_one.replace("&ntilde;", "").replace("&aacute;", "").replace("&amp;", "and")
    return pass_two


class Trivia(Cog):
    """The Cog that handles Trivia commands."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.players = defaultdict(lambda: defaultdict(list))

    @group(aliases=["quiz"])
    async def trivia(self, ctx: Context) -> None:
        """The group for all the trivia commands."""

    @trivia.command()
    async def start(self, ctx: Context, questions: int = 10) -> None:
        """Start a trivia session."""
        def input_check(msg: Message) -> bool:
            return msg.author == ctx.author and msg.channel == ctx.channel

        if questions > 200 or questions < 5:
            await ctx.send("Invalid range! Number of questions must be between 5 and 200.")
            return

        async with self.session.get(f"https://opentdb.com/api.php?amount={questions}&type=multiple") as resp:
            data = await resp.json()

        for result in data["results"]:
            result.update({
                "question": convert_markdown(result["question"]),
                "correct_answer": convert_markdown(result["correct_answer"])
            })

            for incorrect_ans in result["incorrect_answers"]:
                incorrect_answers = result["incorrect_answers"]
                incorrect_answers[incorrect_answers.index(incorrect_ans)] = convert_markdown(incorrect_ans)

        question_num = 1
        await ctx.send(f"❓Starting a trivia round with {questions} questions!")
        self.players[ctx.guild.id][ctx.channel.id].append(ctx.author.id)

        for result in data["results"]:

            options = result["incorrect_answers"]
            options.append(result["correct_answer"])

            enumerated_options = {}
            option_number = 1
            embed_option_string = ""

            options.sort()
            for option in options:
                enumerated_options.update({str(question_num): option})
                embed_option_string += f"{option_number}. {option}\n"
                option_number += 1

            trivia_embed = Embed(
                title=f"Question #{question_num}",
                color=Color.blurple()
            )
            trivia_embed.add_field(
                name=result["question"],
                value=embed_option_string
            )
            trivia_embed.set_author(name=result["category"])
            trivia_embed.set_footer(text=f"Difficulty: {result['difficulty']} | Use {config.COMMAND_PREFIX}triviastop to exit")
            await ctx.send(embed=trivia_embed)
            # first wait (+2 points)
            try:
                first_guess = await self.bot.wait_for("message", timeout=10.0, check=input_check)
                content = first_guess.content.strip().lower()

                if content == f"{config.COMMAND_PREFIX}triviastop":
                    await ctx.send("You aborted the trivia game!")
                    return

                if content == result["correct_answer"].lower() or content in result["correct_answer"]:
                    # TODO: make a point system, the following code is placeholder
                    # points_gained = 2
                    await ctx.send("Yay! you got it right! +2 Points")
                    continue
                else:
                    await ctx.send(f"Sorry, the answer was {result['correct_answer']}")
                    continue

            except asyncio.TimeoutError:
                pass

            try:
                second_guess = await self.bot.wait_for("message", timeout=5, check=input_check)
                content = second_guess.content().strip().lower()

                if content == result["correct_answer"].lower() or content in result["correct_answer"]:
                    # TODO: make a point system, the following code is placeholder
                    # points_gained = 1
                    await ctx.send("Yay! you got it right! +1 Points")
                else:
                    await ctx.send(f"Sorry, the answer was {result['correct_answer']}")

            except asyncio.TimeoutError:
                await ctx.send(f"You took too long to reply, the answer was:\n`{result['correct_answer']}`")

            question_num += 1
