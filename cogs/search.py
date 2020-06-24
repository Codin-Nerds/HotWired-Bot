import os
import re
from typing import List
from urllib.parse import quote_plus
from .utils import constants
import textwrap

import aiohttp
import html2text
from discord import Embed, utils
from discord.ext.commands import Bot, CheckFailure, Cog, CommandNotFound, Context, command, errors

from .search_utils import searchexceptions
from .search_utils.regex import filter_words


class Search(Cog, name="Basic"):
    """Searches the web for a variety of different resources."""

    def __init__(self, bot: Bot) -> None:
        # Main Stuff
        self.bot = bot
        self.emoji = "\U0001F50D"
        self.scrape_token = os.getenv("SCRAPESTACK")

        # Markdown converter
        self.tomd = html2text.HTML2Text()
        self.tomd.ignore_links = True
        self.tomd.ignore_images = True
        self.tomd.ignore_tables = True
        self.tomd.ignore_emphasis = True
        self.tomd.body_width = 0

    async def _search_logic(self, query: str, is_nsfw: bool = False, category: str = "web", count: int = 5) -> list:
        """Uses scrapestack and the Qwant API to find search results."""
        # Typing
        base: str
        safesearch: str

        if filter_words.match(query) and not is_nsfw:
            raise searchexceptions.SafesearchFail("Query had NSFW.")

        base = "https://api.qwant.com/api"

        # Safesearch
        if is_nsfw:
            safesearch = "0"
        else:
            safesearch = "2"

        # Search URL Building
        search_url = f"{base}/search/{category}" f"?count={count}" f"&q={query}" f"&safesearch={safesearch}" "&t=web" "&locale=en_US" "&uiv=4"

        # Scrape or not
        if self.scrape_token != "":
            search_url = "http://api.scrapestack.com/scrape" f"?access_key={self.scrape_token}" f"&url={quote_plus(search_url)}"

        # Searching
        headers = {"User-Agent": ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0")}
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers) as resp:
                to_parse = await resp.json()

                # Sends results
                return to_parse["data"]["result"]["items"]

    async def _basic_search(self, ctx, query: str, category: str = "web") -> None:
        """Basic search formatting."""
        count: int = 5

        is_nsfw = ctx.channel.is_nsfw() if hasattr(ctx.channel, "is_nsfw") else False

        # Handling
        async with ctx.typing():

            # Searches
            results = await self._search_logic(query, is_nsfw, category)
            count = len(results)

            # Escapes all nasties for displaying
            query_display = utils.escape_mentions(query)
            query_display = utils.escape_markdown(query_display)

            # Return if no results
            try:
                results[0]
            except IndexError:
                await ctx.send(f"No results found for `{query_display}`.")
                return

            # Gets the first entry's stuff
            first_title = self.tomd.handle(results[0]["title"]).rstrip("\n")
            first_url = results[0]["url"]
            first_desc = self.tomd.handle(results[0]["desc"]).rstrip("\n")

            # Builds the substring for each of the other results.
            other_results: List[str] = []
            for r in results[1:count]:
                title = self.tomd.handle(r["title"]).rstrip("\n")
                url = r["url"]
                other_results.append(f"**{title}** {url}")
            other_msg: str = "\n".join(other_results)

            # Builds message
            msg = (
                f"Showing **{count}** results for `{query_display}`.\n\n"
                f"**{first_title}** {first_url}\n{first_desc}\n\n"
                f"{other_msg}\n\n_Powered by HotWired._"
            )

            msg = re.sub(r"(https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]+\." r"[a-zA-Z0-9()]+\b[-a-zA-Z0-9()@:%_+.~#?&/=]*)", r"<\1>", msg)

            await ctx.send(msg)

    @command()
    async def search(self, ctx: Context, category: str, *, query: str) -> None:
        """Search online for general results."""
        if category not in constants.basic_search_categories:
            await ctx.send(f"Invalid Category! ```Available Categories : {', '.join(constants.basic_search_categories)}```")
            return
        await self._basic_search(ctx, query, category)

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: errors) -> None:
        """Listener makes no command fallback to searching."""
        fallback = (CommandNotFound, CheckFailure)

        if isinstance(error, fallback):
            try:
                await self._basic_search(ctx, ctx.message.content[len(ctx.prefix):])
            except searchexceptions.SafesearchFail:
                await ctx.send("**Sorry!** That query included language we cannot accept in a non-NSFW channel. Please try again in an NSFW channel.")

    @command()
    async def anime(self, ctx: Context, *, query: str) -> None:
        """Look up anime information."""
        base = "https://kitsu.io/api/edge/"

        # Handling
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(base + "anime", params={"filter[text]": query}) as resp:
                    resp = await resp.json()
                    resp = resp["data"]

                    query = utils.escape_mentions(query)
                    query = utils.escape_markdown(query)

                    if not resp:
                        await ctx.send(f"No results for `{query}`.")
                        return

                    anime = resp[0]
                    title = f'{anime["attributes"]["canonicalTitle"]}'
                    anime_id = anime["id"]
                    url = f"https://kitsu.io/anime/{anime_id}"
                    thing = "" if not anime["attributes"]["endDate"] else f' to {anime["attributes"]["endDate"]}'

                    embed = Embed(title=f"{title}", color=ctx.author.color, rl=url)
                    embed.description = anime["attributes"]["synopsis"][0:425] + "..."
                    embed.add_field(name="Average Rating", value=anime["attributes"]["averageRating"])
                    embed.add_field(name="Popularity Rank", value=anime["attributes"]["popularityRank"])
                    embed.add_field(name="Age Rating", value=anime["attributes"]["ageRating"])
                    embed.add_field(name="Status", value=anime["attributes"]["status"])
                    embed.add_field(name="Aired", value=f"{anime['attributes']['startDate']}{thing}")
                    embed.add_field(name="Episodes", value=anime["attributes"]["episodeCount"])
                    embed.add_field(name="Type", value=anime["attributes"]["showType"])
                    embed.set_thumbnail(url=anime["attributes"]["posterImage"]["original"])
                    embed.set_footer(text=f"Requested by {ctx.author.name} | Powered by HotWired", icon_url=ctx.author.avatar_url_as(format="png"))
                    try:
                        await ctx.send(f"**{title}** - <{url}>", embed=embed)
                    except Exception:
                        aired = f"{anime['attributes']['startDate']}{thing}"
                        template = textwrap.dedent(
                            f"""
                            ```
                            url: {url}
                            Title: {title}
                            Average Rating: {anime["attributes"]["averageRating"]}
                            Popularity Rank: {anime["attributes"]["popularityRank"]}
                            Age Rating: {anime["attributes"]["ageRating"]}
                            Status: {anime["attributes"]["status"]}
                            Aired: {aired}
                            Type: {anime['attributes']["showType"]}
                            Powered by HotWired
                            ```
                            """
                        )
                        await ctx.send(template)

        @command()
        async def manga(self, ctx: Context, *, query: str) -> None:
            """Look up manga information."""
            base = "https://kitsu.io/api/edge/"

            # Handling
            async with ctx.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(base + "manga", params={"filter[text]": query}) as resp:
                        resp = await resp.json()
                        resp = resp["data"]

                        query = utils.escape_mentions(query)
                        query = utils.escape_markdown(query)

                        if not resp:
                            await ctx.send(f"No results for `{query}`.")
                            return

                        manga = resp[0]
                        title = f'{manga["attributes"]["canonicalTitle"]}'
                        manga_id = manga["id"]
                        url = f"https://kitsu.io/manga/{manga_id}"

                        embed = Embed(title=f"{title}", color=ctx.author.color, url=url)
                        embed.description = manga["attributes"]["synopsis"][0:425] + "..."

                        if manga["attributes"]["averageRating"]:
                            embed.add_field(name="Average Rating", value=manga["attributes"]["averageRating"])
                        embed.add_field(name="Popularity Rank", value=manga["attributes"]["popularityRank"])

                        if manga["attributes"]["ageRating"]:
                            embed.add_field(name="Age Rating", value=manga["attributes"]["ageRating"])
                        embed.add_field(name="Status", value=manga["attributes"]["status"])
                        thing = "" if not manga["attributes"]["endDate"] else f' to {manga["attributes"]["endDate"]}'
                        embed.add_field(name="Published", value=f"{manga['attributes']['startDate']}{thing}")

                        if manga["attributes"]["chapterCount"]:
                            embed.add_field(name="Chapters", value=manga["attributes"]["chapterCount"])
                        embed.add_field(name="Type", value=manga["attributes"]["mangaType"])
                        embed.set_thumbnail(url=manga["attributes"]["posterImage"]["original"])

                        try:
                            await ctx.send(f"**{title}** - <{url}>", embed=embed)
                        except Exception:
                            aired = f"{manga['attributes']['startDate']}{thing}"
                            template = textwrap.dedent(
                                f"""
                                ```
                                url: {url}
                                Title: {title}
                                Average Rating: {manga["attributes"]["averageRating"]}
                                Popularity Rank: {manga["attributes"]["popularityRank"]}
                                Age Rating: {manga["attributes"]["ageRating"]}
                                Status: {manga["attributes"]["status"]}
                                Aired: {aired}
                                Type: {manga['attributes']["showType"]}
                                Powered by HotWired
                                ```
                                """
                            )
                            await ctx.send(template)


def setup(bot: Bot) -> None:
    bot.add_cog(Search(bot))
