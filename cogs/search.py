import re
from typing import List
from .utils import constants
import json
import datetime

import aiohttp
import html2text
from discord import Embed, utils, Color
from discord.ext.commands import Bot, Cog, Context, command, bot_has_permissions
import typing as t

from .search_utils import searchexceptions
from .search_utils.regex import filter_words


class Search(Cog, name="Basic"):
    """Searches the web for a variety of different resources."""

    def __init__(self, bot: Bot) -> None:
        # Main Stuff
        self.bot = bot
        self.emoji = "\U0001F50D"
        self.url = "https://graphql.anilist.co"

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

    async def _search_anime_manga(self, ctx: Context, cmd: str, entered_title: str) -> t.Union[tuple, None]:

        media_status_to_string = {
            "FINISHED": "Finished",
            "RELEASING": "Releasing",
            "NOT_YET_RELEASED": "Not yet released",
            "CANCELLED": "Cancelled",
        }

        variables = {"search": entered_title, "page": 1, "type": cmd}

        data = (await self._request(constants.SEARCH_ANIME_MANGA_QUERY, variables))["data"]["Page"]["media"]

        if data is not None and len(data) > 0:

            embeds = []

            for anime_manga in data:
                link = f"https://anilist.co/{cmd.lower()}/{anime_manga['id']}"
                description = anime_manga["description"]
                title = anime_manga["title"]["english"] or anime_manga["title"]["romaji"]
                if anime_manga.get("nextAiringEpisode"):
                    seconds = anime_manga["nextAiringEpisode"]["timeUntilAiring"]
                    time_left = str(datetime.timedelta(seconds=seconds))
                else:
                    time_left = "Never"

                external_links = ""
                for i in range(0, len(anime_manga["externalLinks"])):
                    ext_link = anime_manga["externalLinks"][i]
                    external_links += f"[{ext_link['site']}]({ext_link['url']}), "
                    if i + 1 == len(anime_manga["externalLinks"]):
                        external_links = external_links[:-2]

                embed = Embed(
                    title=title,
                    color=Color.green(),
                    description=self.description_parser(description)
                )
                embed.url = link
                embed.set_thumbnail(url=anime_manga["coverImage"]["medium"])
                embed.add_field(name="Score", value=anime_manga.get("averageScore", "N/A"))

                if cmd == "ANIME":
                    embed.add_field(name="Episodes", value=anime_manga.get("episodes", "N/A"))
                    embed.set_footer(
                        text="Status : " + media_status_to_string[anime_manga["status"]] + ", Next episode : " + time_left + ", Powered by Anilist"
                    )
                else:
                    embed.add_field(name="Chapters", value=anime_manga.get("chapters", "N/A"))
                    embed.set_footer(text="Status : " + media_status_to_string.get(anime_manga.get("status"), "N/A") + ", Powered by Anilist")

                if external_links:
                    embed.add_field(name="Streaming and/or Info sites", value=external_links)

                if anime_manga["bannerImage"]:
                    embed.set_image(url=anime_manga["bannerImage"])
                embed.add_field(
                    name="You can find out more",
                    value=f"[Anilist]({link}), [MAL](https://myanimelist.net/{cmd.lower()}/{anime_manga['idMal']}), Kitsu (Soon™)"
                )
                embeds.append(embed)

            return embeds, data

        else:
            return None

    async def _search_character(self, ctx: Context, entered_title: str) -> t.Union[tuple, None]:

        variables = {"search": entered_title, "page": 1}

        data = (await self._request(constants.SEARCH_CHARACTER_QUERY, variables))["data"]["Page"]["characters"]

        if data is not None and len(data) > 0:
            embeds = []

            for character in data:
                link = f"https://anilist.co/character/{character['id']}"
                character_anime = [f'[{anime["title"]["userPreferred"]}]({"https://anilist.co/anime/" + str(anime["id"])})'
                                   for anime in character["media"]["nodes"] if anime["type"] == "ANIME"]
                character_manga = [f'[{manga["title"]["userPreferred"]}]({"https://anilist.co/manga/" + str(manga["id"])})'
                                   for manga in character["media"]["nodes"] if manga["type"] == "MANGA"]

                embed = Embed(
                    title=self.format_name(character["name"]["first"], character["name"]["last"]),
                    color=Color.blue(),
                    description=self.description_parser(character["description"])
                )
                embed.url = link
                embed.set_thumbnail(url=character["image"]["large"])
                if len(character_anime) > 0:
                    embed.add_field(name="Anime", value="\n".join(self.list_maximum(character_anime)))
                if len(character_manga) > 0:
                    embed.add_field(name="Manga", value="\n".join(self.list_maximum(character_manga)))
                embed.set_footer(text="Powered by Anilist")
                embeds.append(embed)

            return embeds, data

        else:
            return None

    @command()
    @bot_has_permissions(embed_links=True, add_reactions=True)
    async def anime(self, ctx: Context, *, entered_title: str) -> None:
        """Searches for anime."""

        try:
            cmd = "ANIME"
            embeds, data = await self._search_anime_manga(ctx, cmd, entered_title)

            if embeds is not None:
                # TODO: add pagination
                await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=30)
            else:
                await ctx.send("No anime was found or there was an error in the process")

        except TypeError:
            await ctx.send("No anime was found or there was an error in the process")

    @command()
    @bot_has_permissions(embed_links=True, add_reactions=True)
    async def manga(self, ctx: Context, *, entered_title: str) -> None:
        """Searches for manga."""

        try:
            cmd = "MANGA"
            embeds, data = await self._search_anime_manga(ctx, cmd, entered_title)

            if embeds is not None:
                # TODO: implement pagination
                await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=30)
            else:
                await ctx.send("No mangas were found or there was an error in the process")

        except TypeError:
            await ctx.send("No mangas were found or there was an error in the process")

    def format_name(self, first_name: str, last_name: str) -> str:  # Combines first_name and last_name and/or shows either of the two
        if first_name and last_name:
            return first_name + " " + last_name
        elif first_name:
            return first_name
        elif last_name:
            return last_name
        else:
            return "No name"

    def clean_html(self, description: str) -> str:
        if not description:
            return ""
        regex = re.compile("<.*?>")
        cleantext = re.sub(regex, "", description)
        return cleantext

    def clean_spoilers(self, description: str) -> str:
        if not description:
            return ""
        regex = re.compile("/<span[^>]*>.*</span>/g")
        cleantext = re.sub(regex, "", description)
        return cleantext

    def description_parser(self, description: str) -> str:
        description = self.clean_spoilers(description)
        description = self.clean_html(description)
        description = "\n".join(description.split("\n")[:5])
        if len(description) > 400:
            return description[:400] + "..."
        else:
            return description

    def list_maximum(self, items: list) -> list:
        if len(items) > 5:
            return items[:5] + ["+ " + str(len(items) - 5) + " more"]
        else:
            return items

    async def _request(self, query: str, variables: str = None) -> dict:

        if variables is None:
            variables = {}

        request_json = {"query": query, "variables": variables}

        headers = {"content-type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=json.dumps(request_json), headers=headers) as response:
                return await response.json()

    async def _search_user(self, ctx: Context, entered_title: str) -> t.Union[tuple, None]:

        variables = {"search": entered_title, "page": 1}

        data = (await self._request(constants.SEARCH_USER_QUERY, variables))["data"]["Page"]["users"]

        if data is not None and len(data) > 0:

            embeds = []

            for user in data:
                link = f"https://anilist.co/user/{user['id']}"
                title = f"[{user['name']}]({link})"
                title = user["name"]

                embed = Embed(
                    title=title,
                    color=Color.green(),
                    description=self.description_parser(user["about"])
                )
                embed.url = link
                embed.set_thumbnail(url=user["avatar"]["large"])
                embed.add_field(name="Watched time", value=datetime.timedelta(minutes=int(user["stats"]["watchedTime"])))
                embed.add_field(name="Chapters read", value=user["stats"].get("chaptersRead", "N/A"))

                for category in "anime", "manga", "characters":
                    fav = []
                    for node in user["favourites"][category]["nodes"]:
                        url_path = category
                        if category == "characters":
                            name = node["name"]
                            title = self.format_name(name["first"], name["last"])
                            url_path = "character"
                        else:
                            title = node["title"]["userPreferred"]

                        fav.append(f'[{title}](https://anilist.co/{url_path}/{node["id"]})')

                    if fav:
                        embed.add_field(name=f"Favorite {category}", value="\n".join(self.list_maximum(fav)))
                embed.set_footer(text="Powered by Anilist")
                embeds.append(embed)

            return embeds, data

        else:
            return None

    @command()
    async def character(self, ctx: Context, *, entered_title: str) -> None:
        """Searches for characters."""

        try:
            embeds, data = await self._search_character(ctx, entered_title)

            if embeds is not None:
                # TODO: implement pagination
                await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=30)
            else:
                await ctx.send("No characters were found or there was an error in the process")

        except TypeError:
            await ctx.send("No characters were found or there was an error in the process")

    @command()
    @bot_has_permissions(embed_links=True, add_reactions=True)
    async def user(self, ctx: Context, *, entered_title: str) -> None:
        """Searches users."""

        try:
            embeds, data = await self._search_user(ctx, entered_title)

            if embeds is not None:
                # TODO: implement pagination
                await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=30)
            else:
                await ctx.send("No users were found or there was an error in the process")

        except TypeError:
            await ctx.send("No users were found or there was an error in the process")


def setup(bot: Bot) -> None:
    bot.add_cog(Search(bot))
