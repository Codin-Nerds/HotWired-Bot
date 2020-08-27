import asyncio
import re
import textwrap
import time
import typing as t
from contextlib import suppress

from dateutil.relativedelta import relativedelta
from discord import (
    Color,
    Embed,
    File,
    Forbidden,
    Member,
)
from discord.ext.commands import (
    BadArgument, BucketType, Cog, Context,
    command, cooldown, has_permissions
)

from io import BytesIO
from bs4 import BeautifulSoup as bs
from random import choice
import unicodedata

from bot import config
from bot.core.bot import Bot
from bot.core.converters import TimeDelta
from bot.utils.time import stringify_timedelta
from datetime import datetime

IMAGE_LINKS = re.compile(r"(http[s]?:\/\/[^\"\']*\.(?:png|jpg|jpeg|gif|png))")


class Common(Cog):
    """Common commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    # TODO : Add custom command support after db integration
    @command()
    async def hello(self, ctx: Context) -> None:
        """Greet a Member."""
        await ctx.send("Hey there Buddy! How's it Going?")

    @command()
    @has_permissions(manage_messages=True)
    async def ping(self, ctx: Context) -> None:
        """Show bot ping."""
        start = time.perf_counter()
        embed = Embed(title="Info", description="Pong!", color=Color.blurple())
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        discord_start = time.monotonic()
        async with self.bot.session.get("https://discord.com/") as resp:
            if resp.status == 200:
                discord_end = time.monotonic()
                discord_ms = f"{round((discord_end - discord_start) * 1000)}ms"
            else:
                discord_ms = "fucking dead"

        desc = textwrap.dedent(
            f"""
            :ping_pong: Pong!
            Bot ping: ({duration}ms)
            Discord Server Ping: ({discord_ms}ms)
            """
        )

        embed = Embed(title="Info", description=desc, color=Color.blurple())
        await message.edit(embed=embed)

    # TODO : after db integration, add Time Limit, and grand announcement, when the poll is over.
    @command(aliases=("poll",))
    async def vote(self, ctx: Context, title: str, *options: str) -> None:
        """Build a quick voting poll with matching reactions with the provided options.

        A maximum of 20 options can be provided, as Discord supports a max of 20
        reactions on a single message.
        """
        if len(options) < 2:
            raise BadArgument("Please provide at least 2 options.")
        if len(options) > 20:
            raise BadArgument("I can only handle 20 options!")

        codepoint_start = 127462  # represents "regional_indicator_a" unicode value
        options = {chr(i): f"{chr(i)} - {v}" for i, v in enumerate(options, start=codepoint_start)}
        embed = Embed(title=title, description="\n".join(options.values()))
        message = await ctx.send(embed=embed)
        for reaction in options:
            await message.add_reaction(reaction)

    @command(aliases=["spoll"])
    async def strawpoll(self, ctx: Context, *, question_and_choices: str = None) -> None:
        """Strawpoll my question.

        Syntax : answer a | answer b | answer c
        At least two answers required.
        """
        if question_and_choices is None:
            return await ctx.send_help("strawpoll")

        if "|" in question_and_choices:
            delimiter = "|"
        else:
            delimiter = ","
        question_and_choices = question_and_choices.split(delimiter)

        if len(question_and_choices) == 1:
            return await ctx.send("Not enough choices supplied")
        if len(question_and_choices) >= 31:
            return await ctx.send("Too many choices")

        question, *choices = question_and_choices
        choices = [x.lstrip() for x in choices]

        header = {"Content-Type": "application/json"}
        payload = {
            "title": question,
            "options": choices,
            "multi": False
        }

        async with self.bot.session.post("https://www.strawpoll.me/api/v2/polls", headers=header, json=payload) as r:
            data = await r.json()

        strawpoll_id = data["id"]
        await ctx.send(f"http://www.strawpoll.me/{strawpoll_id}")

    # TODO : add github logo thumnail to embed, and some more content.
    @command(aliases=["git"])
    async def github(self, ctx: Context) -> None:
        """Send a link to the bots GitHub repository."""
        await ctx.send(
            embed=Embed(
                title="Github Repo",
                description=f"[Click Here]({config.github_repo_link}) to visit the Open Source Repo of HotWired",
                color=Color.dark_blue(),
            )
        )

    # TODO : beautify this timer with a realtime updating clock image.
    @command()
    @cooldown(1, 10, BucketType.member)
    async def countdown(self, ctx: Context, duration: TimeDelta, *, description: t.Optional[str] = Embed.Empty) -> None:
        """A countdown timer that counts down for the specific duration."""
        embed = Embed(
            title="Timer",
            description=description,
            color=Color.blue()
        )
        embed.add_field(
            name="**Countdown**",
            value=stringify_timedelta(duration)
        )
        message = await ctx.send(embed=embed)

        final_time = datetime.utcnow() + duration
        while True:
            if final_time <= datetime.utcnow():
                break
            duration = relativedelta(final_time, datetime.utcnow())

            embed.set_field_at(
                0,
                name="**Countdown**",
                value=stringify_timedelta(duration)
            )
            await message.edit(embed=embed)

            await asyncio.sleep(1)

        embed.set_field_at(
            0,
            name="**Countdown**",
            value="Timer reached zero!"
        )
        await message.edit(embed=embed)

    @command(aliases=["asking"])
    async def howtoask(self, ctx: Context) -> None:
        """How to ask a question."""
        embed = Embed(
            title="How To Ask a Question?",
            description=textwrap.dedent(
                """
                **1 ❯** Pick the appropriate channel
                **2 ❯** Post your question mentioning all the details
                **3 ❯** Ping the appropriate helper role or someone for your question
                **4 ❯** Patiently wait for a helper to respond
                """
            ),
            color=Color.blurple(),
        )
        img_url = "https://media.giphy.com/media/3ojqPGJAHWqC1VQPDk/giphy.gif"
        embed.set_image(url=img_url)
        await ctx.send("**A S K I N G   A   Q U E S T I O N ❓**")
        await ctx.send(embed=embed)

    @command(aliases=["thank", "ty"])
    async def thanks(self, ctx: Context, member: Member, *, reason: str = None) -> None:
        """Thank a Member."""
        if ctx.author == member:
            embed = Embed(title="WARNING", description=f"{ctx.author.mention} **You Cannot Thank Yourself!**", color=Color.orange(),)
            await ctx.send(embed=embed)
        else:
            embed = Embed(
                title="THANKS",
                description=textwrap.dedent(
                    f"""
                    {member.mention} was thanked by {ctx.author.mention}!
                    {'**MESSAGE**:' + reason if reason else ''}
                    """
                ),
                color=Color.blurple(),
            )
            embed.set_image(url="https://media.giphy.com/media/6tHy8UAbv3zgs/giphy.gif")
            await ctx.send(embed=embed)

    @command()
    async def paste(self, ctx: Context, *, text: str) -> None:
        """Creates a Paste out of the text specified."""
        async with self.bot.session.post("https://hasteb.in/documents", data=self._clean_code(text)) as resp:
            key = (await resp.json())['key']
            file_paste = 'https://www.hasteb.in/' + key

            await ctx.send(
                embed=Embed(title="File pastes", description=file_paste, color=Color.blue())
            )

    def _clean_code(self, code: str) -> str:
        codeblock_match = re.fullmatch(r"\`\`\`(.*\n)?((?:[^\`]*\n*)+)\`\`\`", code)
        if codeblock_match:
            lang = codeblock_match.group(1)
            code = codeblock_match.group(2)
            ret = lang if not code else code
            if ret[-1] == "\n":
                ret = ret[:-1]
            return ret

        simple_match = re.fullmatch(r"\`(.*\n*)\`", code)
        if simple_match:
            return simple_match.group(1)

        return code

    @cooldown(1, 10, BucketType.member)
    async def shorten(self, ctx: Context, *, link: str) -> None:
        """Make a link shorter using the tinyurl api."""
        if not link.startswith("https://"):
            await ctx.send(f"Invalid link: `{link}`. Enter a valid URL.")
            return

        url = link.strip("<>")
        url = f"http://tinyurl.com/api-create.php?url={url}"

        async with self.bot.session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("Error retrieving shortened URL, please try again in a minute.")
                return
            shortened_link = await resp.text()

        embed = Embed(color=Color.blurple())
        embed.add_field(name="Original Link", value=link, inline=False)
        embed.add_field(name="Shortened Link", value=shortened_link, inline=False)
        await ctx.send(embed=embed)

        with suppress(Forbidden):
            await ctx.message.delete()

    @cooldown(1, 15, BucketType.guild)
    @command()
    async def retrosign(self, ctx, *, content: str):
        """Make a retrosign with 3 words seperated by ';' or with one word in the middle."""
        texts = [t.strip() for t in content.split(";")]
        if len(texts) == 1:
            lenstr = len(texts[0])
            if lenstr <= 15:
                data = dict(
                    bcg=choice([1, 2, 3, 4, 5]),
                    txt=choice([1, 2, 3, 4]),
                    text1="",
                    text2=texts[0],
                    text3="",
                )
            else:
                return await ctx.send("\N{CROSS MARK} Your line is too long (14 character limit)")
        elif len(texts) == 3:
            texts[0] = unicodedata.normalize('NFD', texts[0]).encode('ascii', 'ignore')
            texts[0] = texts[0].decode('UTF-8')
            texts[0] = re.sub(r'[^A-Za-z0-9 ]', '', texts[0])
            if len(texts[0]) >= 15:
                return await ctx.send(
                    "\N{CROSS MARK} Your first line is too long (14 character limit)"
                )
            if len(texts[1]) >= 13:
                return await ctx.send(
                    "\N{CROSS MARK} Your second line is too long (12 character limit)"
                )
            if len(texts[2]) >= 26:
                return await ctx.send(
                    "\N{CROSS MARK} Your third line is too long (25 character limit)"
                )
            data = dict(
                bcg=choice([1, 2, 3, 4, 5]),
                txt=choice([1, 2, 3, 4]),
                text1=texts[0],
                text2=texts[1],
                text3=texts[2],
            )
        else:
            return await ctx.send(
                "\N{CROSS MARK} please provide three words seperated by ';' or one word"
            )

        async with ctx.channel.typing():
            async with self.session.post(
                "https://photofunia.com/effects/retro-wave", data=data
            ) as response:
                if response.status == 200:
                    soup = bs(await response.text(), "html.parser")
                    download_url = soup.find("div", class_="downloads-container").ul.li.a["href"]
                    async with self.session.request("GET", download_url) as image_response:
                        if image_response.status == 200:
                            image_data = await image_response.read()
                            with BytesIO(image_data) as temp_image:
                                image = File(fp=temp_image, filename="image.png")
                                await ctx.channel.send(file=image)


def setup(bot: Bot) -> None:
    """Load the Common cog."""
    bot.add_cog(Common(bot))
