import datetime
import json
import re
import typing as t

import aiohttp
import discord
from discord.ext import commands, menus

SEARCH_ANIME_MANGA_QUERY = """
query ($id: Int, $page: Int, $search: String, $type: MediaType) {
    Page (page: $page, perPage: 10) {
        media (id: $id, search: $search, type: $type) {
            id
            idMal
            description(asHtml: false)
            title {
                english
                romaji
            }
            coverImage {
            		medium
            }
            bannerImage
            averageScore
            meanScore
            status
            episodes
            chapters
            externalLinks {
                url
                site
            }
            nextAiringEpisode {
                timeUntilAiring
            }
        }
    }
}
"""

SEARCH_CHARACTER_QUERY = """
query ($id: Int, $page: Int, $search: String) {
  Page(page: $page, perPage: 10) {
    characters(id: $id, search: $search) {
      id
      description (asHtml: true),
      name {
        first
        last
        native
      }
      image {
        large
      }
      media {
        nodes {
          id
          type
          title {
            romaji
            english
            native
            userPreferred
          }
        }
      }
    }
  }
}
"""

SEARCH_USER_QUERY = """
query ($id: Int, $page: Int, $search: String) {
    Page (page: $page, perPage: 10) {
        users (id: $id, search: $search) {
            id
            name
            siteUrl
            avatar {
                    large
            }
            about (asHtml: true),
            stats {
                watchedTime
                chaptersRead
            }
            favourites {
            manga {
              nodes {
                id
                title {
                  romaji
                  english
                  native
                  userPreferred
                }
              }
            }
            characters {
              nodes {
                id
                name {
                  first
                  last
                  native
                }
              }
            }
            anime {
              nodes {
                id
                title {
                  romaji
                  english
                  native
                  userPreferred
                }
              }
            }
            }
        }
    }
}
"""


class EmbedSource(menus.ListPageSource):
    """Source for showing embeds."""

    async def format_page(
            self, menu: menus.Menu, embed: discord.Embed) -> discord.Embed:
        """Create an embed from a dict."""
        embed.set_footer(
            f"Page {menu.current_page + 1}/{self.get_max_pages()}"
        )
        return embed

class AniSearch(commands.Cog):
    """Search for anime, manga, characters and users using Anilist."""

    def __init__(self, bot: commands.Bot) -> None:
        self.url = "https://graphql.anilist.co"
        self.bot = bot

    @staticmethod
    def format_name(first_name: str, last_name: str) -> str:
        """Combine first_name and last_name and/or shows either of the two."""
        if first_name and last_name:
            return f"{first_name} {last_name}"
        if first_name:
            return first_name
        if last_name:
            return last_name
        return "No name"

    @staticmethod
    def clean_html(description: str) -> str:
        """Remove html tags."""
        if not description:
            return ""
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", description)
        return cleantext

    @staticmethod
    def clean_spoilers(description: str) -> str:
        """Remove spoilers using the html tag given by AniList."""
        if not description:
            return ""
        cleanr = re.compile("/<span[^>]*>.*</span>/g")
        cleantext = re.sub(cleanr, "", description)
        return cleantext

    def description_parser(self, description: str) -> str:
        """Limit text to 400 characters and 5 lines and adds "..." at the end."""
        description = self.clean_spoilers(description)
        description = self.clean_html(description)
        description = "\n".join(description.split("\n")[:5])
        if len(description) > 400:
            return description[:400] + "..."
        return description

    @staticmethod
    def list_maximum(items: t.List[str]) -> t.List[str]:
        """Limit to 5 strings than adds "+X more"."""
        if len(items) > 5:
            return items[:5] + [f"+ {len(items) - 5} more"]
        return items

    async def _request(self, query: str, variables: dict = None) -> dict:

        if variables is None:
            variables = {}

        request_json = {"query": query, "variables": variables}

        headers = {"content-type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=json.dumps(request_json), headers=headers) as response:
                return await response.json()

    async def _search_anime_manga(self, cmd: str, entered_title: str) -> t.List[discord.Embed]:

        # Outputs MediaStatuses to strings
        mediastatustostring = {
            # Has completed and is no longer being released
            "FINISHED": "Finished",
            # Currently releasing
            "RELEASING": "Releasing",
            # To be released at a later date
            "NOT_YET_RELEASED": "Not yet released",
            # Ended before the work could be finished
            "CANCELLED": "Cancelled",
        }

        data = (
            self._request(SEARCH_ANIME_MANGA_QUERY, {
                "search": entered_title,
                "page": 1,
                "type": cmd,
            })
        )["data"]["Page"]["media"]

        if data:

            # a list of embeds
            embeds = []

            for anime_manga in data:
                # Sets up various variables for Embed
                link = f"https://anilist.co/{cmd.lower()}/{anime_manga['id']}"
                if anime_manga.get("nextAiringEpisode"):
                    seconds = anime_manga[
                        "nextAiringEpisode"
                    ]["timeUntilAiring"]
                    time_left = str(datetime.timedelta(seconds=seconds))
                else:
                    time_left = "Never"

                external_links = ""
                for i in range(len(anime_manga["externalLinks"])):
                    ext_link = anime_manga["externalLinks"][i]
                    external_links += f"[{ext_link['site']}]({ext_link['url']}), "
                external_links = external_links[:-2]

                embed = discord.Embed(title=anime_manga[
                    "title"
                ]["english"] or anime_manga[
                    "title"
                ]["romaji"])
                embed.url = link
                embed.color = 3447003
                embed.description = self.description_parser(
                    anime_manga["description"]
                )
                embed.set_thumbnail(url=anime_manga["coverImage"]["medium"])
                embed.add_field(
                    name="Score",
                    value=anime_manga.get("averageScore", "N/A"),
                )
                if cmd == "ANIME":
                    embed.add_field(
                        name="Episodes",
                        value=anime_manga.get("episodes", "N/A"),
                    )
                    embed.set_footer(
                        text="Status : "
                        + mediastatustostring[anime_manga["status"]]
                        + ", Next episode : "
                        + time_left
                        + ", Powered by Anilist",
                    )
                else:
                    embed.add_field(
                        name="Chapters",
                        value=anime_manga.get("chapters", "N/A"),
                    )
                    embed.set_footer(
                        text="Status : "
                        + mediastatustostring.get(
                            anime_manga.get("status"), "N/A"
                        )
                        + ", Powered by Anilist")
                if external_links:
                    embed.add_field(
                        name="Streaming and/or Info sites",
                        value=external_links,
                    )
                if anime_manga["bannerImage"]:
                    embed.set_image(url=anime_manga["bannerImage"])
                embed.add_field(
                    name="You can find out more",
                    value=f"[Anilist]({link}), "
                    + f"[MAL](https://myanimelist.net/{cmd.lower()}/"
                    + f"{anime_manga['idMal']}), Kitsu (Soon™)",
                )
                embeds.append(embed)

            return embeds

    async def _search_character(self, entered_title: str) -> t.List[discord.Embed]:

        variables = {"search": entered_title, "page": 1}

        data = (await self._request(SEARCH_CHARACTER_QUERY, variables))[
            "data"
        ]["Page"]["characters"]

        if data:

            # a list of embeds
            embeds = []

            for character in data:
                # Sets up various variables for Embed
                link = f"https://anilist.co/character/{character['id']}"
                character_anime = [
                    f'[{anime["title"]["userPreferred"]}](https://anilist.co/'
                    + f'anime/{anime["id"]})'
                    for anime in character["media"][
                        "nodes"
                    ] if anime["type"] == "ANIME"
                ]
                character_manga = [
                    f'[{manga["title"]["userPreferred"]}](https://anilist.co/'
                    + f'manga/{manga["id"]})'
                    for manga in character["media"][
                        "nodes"
                    ] if manga["type"] == "MANGA"
                ]
                embed = discord.Embed(
                    title=self.format_name(
                        character["name"]["first"],
                        character["name"]["last"],
                    ),
                )
                embed.url = link
                embed.color = 3447003
                embed.description = self.description_parser(
                    character["description"],
                )
                embed.set_thumbnail(url=character["image"]["large"])
                if character_anime:
                    embed.add_field(
                        name="Anime",
                        value="\n".join(self.list_maximum(character_anime)),
                    )
                if character_manga:
                    embed.add_field(
                        name="Manga",
                        value="\n".join(self.list_maximum(character_manga)),
                    )
                embed.set_footer(text="Powered by Anilist")
                embeds.append(embed)

            return embeds

    async def _search_user(self, entered_title: str) -> t.List[discord.Embed]:

        variables = {"search": entered_title, "page": 1}

        data = (await self._request(SEARCH_USER_QUERY, variables))["data"][
            "Page"
        ]["users"]

        if data:

            # a list of embeds
            embeds = []

            for user in data:
                # Sets up various variables for Embed
                link = f"https://anilist.co/user/{user['id']}"
                title = f"[{user['name']}]({link})"
                title = user["name"]

                embed = discord.Embed(title=title)
                embed.url = link
                embed.color = 3447003
                embed.description = self.description_parser(user["about"])
                embed.set_thumbnail(url=user["avatar"]["large"])
                embed.add_field(
                    name="Watched time",
                    value=datetime.timedelta(
                        minutes=int(user["stats"]["watchedTime"]),
                    ),
                )
                embed.add_field(
                    name="Chapters read",
                    value=user["stats"].get("chaptersRead", "N/A"),
                )
                for category in "anime", "manga", "characters":
                    fav = []
                    for node in user["favourites"][category]["nodes"]:
                        url_path = category
                        if category == "characters":
                            name = node["name"]
                            title = self.format_name(
                                name["first"],
                                name["last"],
                            )
                            url_path = "character"  # without the s
                        else:
                            title = node["title"]["userPreferred"]

                        fav.append(
                            f'[{title}](https://anilist.co/{url_path}/'
                            + f'{node["id"]})'
                        )

                    if fav:
                        embed.add_field(
                            name=f"Favorite {category}",
                            value="\n".join(self.list_maximum(fav)),
                        )
                embed.set_footer(text="Powered by Anilist")
                embeds.append(embed)

            return embeds

    @commands.command()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def anime(self, ctx: commands.Context, *, entered_title: str) -> None:
        """Search for anime using Anilist."""
        try:
            cmd = "ANIME"
            embeds = await self._search_anime_manga(cmd, entered_title)

            if embeds:
                menu = menus.MenuPages(
                    source=EmbedSource(
                        embeds,
                        per_page=1,
                    ),
                    clear_reactions_after=True,
                )
                await menu.start(ctx)
            else:
                await ctx.send(
                    "No anime was found or there was an error in the process"
                )
        except TypeError:
            await ctx.send(
                "No anime was found or there was an error in the process"
            )

    @commands.command()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def manga(self, ctx: commands.Context, *, entered_title: str) -> None:
        """Search for manga using Anilist."""
        try:
            cmd = "MANGA"
            embeds = await self._search_anime_manga(cmd, entered_title)

            if embeds:
                menu = menus.MenuPages(
                    source=EmbedSource(
                        embeds,
                        per_page=1,
                    ),
                    clear_reactions_after=True,
                )
                await menu.start(ctx)
            else:
                await ctx.send(
                    "No mangas were found or there was an error in the process"
                )

        except TypeError:
            await ctx.send(
                "No mangas were found or there was an error in the process"
            )

    @commands.command()
    async def character(self, ctx: commands.Context, *, entered_title: str) -> None:
        """Search for characters using Anilist."""
        try:
            embeds = await self._search_character(entered_title)

            if embeds:
                menu = menus.MenuPages(
                    source=EmbedSource(
                        embeds,
                        per_page=1,
                    ),
                    clear_reactions_after=True,
                )
                await menu.start(ctx)
            else:
                await ctx.send(
                    "No characters were found or there was an error in the process"
                )

        except TypeError:
            await ctx.send(
                "No characters were found or there was an error in the process"
            )

    @commands.command()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def user(self, ctx: commands.Context, *, entered_title: str) -> None:
        """Search users using Anilist."""
        try:
            embeds = await self._search_user(entered_title)

            if embeds:
                menu = menus.MenuPages(
                    source=EmbedSource(
                        embeds,
                        per_page=1,
                    ),
                    clear_reactions_after=True,
                )
                await menu.start(ctx)
            else:
                await ctx.send(
                    "No users were found or there was an error in the process"
                )

        except TypeError:
            await ctx.send(
                "No users were found or there was an error in the process"
            )


def setup(bot: commands.Bot):
    """Add Anisearch cog to the bot."""
    bot.add_cog(AniSearch(bot))
