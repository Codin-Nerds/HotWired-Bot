import re
import textwrap
from typing import List

import aiohttp
import html2text
from discord import Embed, utils, Color
from discord.ext.commands import Cog, CommandError, Context, command

from bot import config
from bot.core.bot import Bot

with open("bot/assets/filter_words.txt", "r") as f:
    filter_words = f.readlines()

regexp = ""
for filter_word in filter_words:
    filter_word = filter_word.replace("\n", "")
    regexp += f"{filter_word}|"
regexp = regexp[:-1]

filter_words = re.compile(regexp, re.I)


class SafesearchFail(CommandError):
    """Thrown when a query contains NSFW content."""
    pass


class Search(Cog, name="Basic"):
    """Searches the web for a variety of different resources."""

    def __init__(self, bot: Bot) -> None:
        # Main Stuff
        self.bot = bot
        self.emoji = "\U0001F50D"

        # Markdown converter
        self.tomd = html2text.HTML2Text()
        self.tomd.ignore_links = True
        self.tomd.ignore_images = True
        self.tomd.ignore_tables = True
        self.tomd.ignore_emphasis = True
        self.tomd.body_width = 0

    async def _search_logic(self, query: str, is_nsfw: bool = False, category: str = "web", count: int = 5) -> list:
        """Uses scrapestack and the Qwant API to find search results."""
        if not is_nsfw:
            filter = filter_words.search(query)
            if filter:
                # TODO: Log this
                raise SafesearchFail("Query had NSFW.")

        base = "https://api.qwant.com/api"

        # Safesearch
        if is_nsfw:
            safesearch = "0"
        else:
            safesearch = "2"

        # Search URL Building
        search_url = f"{base}/search/{category}?count={count}&q={query}&safesearch={safesearch}&t=web&locale=en_US&uiv=4"

        # Searching
        headers = {"User-Agent": ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0")}
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers) as resp:
                to_parse = await resp.json()

                # Sends results
                return to_parse["data"]["result"]["items"]

    async def _basic_search(self, ctx, query: str, category: str) -> None:
        """Basic search formatting."""
        is_nsfw = ctx.channel.is_nsfw() if hasattr(ctx.channel, "is_nsfw") else False

        async with ctx.typing():
            # Searches
            try:
                results = await self._search_logic(query, is_nsfw, category)
            except SafesearchFail:
                await ctx.send(f":x: Sorry {ctx.author.mention}, your message contains filtered words, I've removed this message.")
                await ctx.message.delete()
                return
            count = len(results)

            # Ignore markdown when displaying
            query_display = utils.escape_mentions(query)
            query_display = utils.escape_markdown(query_display)

            # Return if no results
            if count == 0:
                await ctx.send(f"No results found for `{query_display}`.")
                return

            # Gets the first entry's data
            first_title = self.tomd.handle(results[0]["title"]).rstrip("\n")
            first_url = results[0]["url"]
            first_desc = self.tomd.handle(results[0]["desc"]).rstrip("\n")

            # Builds the substring for each of the other result.
            other_results: List[str] = []
            for r in results[1:count]:
                title = self.tomd.handle(r["title"]).rstrip("\n")
                url = r["url"]
                other_results.append(f"**{title}** {url}")
            other_msg: str = "\n".join(other_results)

            # Builds message
            msg = (textwrap.dedent(
                f"""
                Showing **{count}** results for `{query_display}`.


                **{first_title}** {first_url}
                {first_desc}

                {other_msg}

                _Powered by HotWired._
                """
            ))

            msg = re.sub(r"(https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]+\." r"[a-zA-Z0-9()]+\b[-a-zA-Z0-9()@:%_+.~#?&/=]*)", r"<\1>", msg)

            await ctx.send(msg)

    @command()
    async def search(self, ctx: Context, category: str, *, query: str) -> None:
        """
        Search online for general results.
        Valid Categories:
             - web
             - videos
             - music
             - files
             - images
             - it
             - maps
        """
        if category not in config.basic_search_categories:
            await ctx.send(f"Invalid Category! ```Available Categories : {', '.join(config.basic_search_categories)}```")
            return
        await self._basic_search(ctx, query, category)

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

                    embed = Embed(title=title, color=ctx.author.color, url=url)
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

    @command()
    async def weather(self, ctx: Context, *, city: str = None) -> None:
        """Sends current weather in the given city name

        eg. weather london
        """
        url_formatted_city = city.replace(" ", "-")
        async with aiohttp.ClientSession() as session:
            try:
                weather_lookup_url = f"https://api.openweathermap.org/data/2.5/weather?q={url_formatted_city}&appid={config.WEATHER_API_KEY}"
                async with session.get(weather_lookup_url) as resp:
                    data = await resp.json()
            except Exception:
                await ctx.send("You didn't provide a city name")
                return

        if data["cod"] == "401":
            await ctx.send("Invalid API key")
            return
        if data["cod"] == "404":
            await ctx.send("Invalid city name")
            return

        weather_embed = Embed(
            title=f"Current Weather in {city.capitalize()}",
            color=Color.blue()
        )
        longtitude = data["coord"]["lon"]
        lattitude = data["coord"]["lat"]
        weather_embed.add_field(
            name="Coordinates",
            value=f"**❯❯ Longtitude: **`{longtitude}`\n**❯❯ Latittude: **`{lattitude}`"
        )
        actual_temp = round(data["main"]["temp"] / 10, 1)
        feels_like = round(data["main"]["feels_like"] / 10, 1)
        weather_embed.add_field(
            name="Temperature",
            value=f"**❯❯ Temperature: **`{actual_temp}°C`\n**❯❯ Feels Like: **`{feels_like}°C`"
        )
        wind_speed = data["wind"]["speed"]
        wind_direction = data["wind"]["deg"]
        weather_embed.add_field(
            name="Wind",
            value=f"**❯❯ Speed: **`{wind_speed}km/h`\n**❯❯ Direction: **`{wind_direction}°`",
        )
        visibility = round(data["visibility"] / 1000, 2)
        humidity = data["main"]["humidity"]
        weather_description = data["weather"][0]["description"]
        weather_embed.add_field(
            name="Miscellaneous",
            value=f"**❯❯ Humidity: **`{humidity}%`\n**❯❯ Visibility: **`{visibility}km`\n**❯❯ Weather Summary: **`{weather_description}`",
        )

        if "wind" in weather_description:
            weather_embed.set_image(url=config.WEATHER_ICONS["wind"])
        elif "partly" in weather_description:
            weather_embed.set_image(url=config.WEATHER_ICONS["partly"])
        elif "cloud" in weather_description:
            weather_embed.set_image(url=config.WEATHER_ICONS["cloud"])
        elif "snow" in weather_description:
            weather_embed.set_image(url=config.WEATHER_ICONS["snow"])
        elif "rain" in weather_description:
            weather_embed.set_image(url=config.WEATHER_ICONS["rain"])
        else:
            weather_embed.set_image(url=config.WEATHER_ICONS["sun"])

        await ctx.send(embed=weather_embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Search(bot))
