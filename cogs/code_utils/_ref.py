import re
import urllib.parse
from functools import partial

from bs4 import BeautifulSoup

import aiohttp
from discord import Message, Embed
from discord.ext.commands import Context
from markdownify import MarkdownConverter
import typing as t


def markdownify(html: str) -> str:
    return MarkdownConverter(bullets="•").convert(html)


async def _process_mozilla_doc(ctx: Context, url: str) -> t.Union[Message, str]:
    """Get tag formatted content from given url from developers.mozilla.org."""
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as response:
            if response.status == 404:
                return await ctx.send("No results")
            if response.status != 200:
                return await ctx.send(f"An error occurred (status code: {response.status}). Retry later.")

            body = BeautifulSoup(await response.text(), "lxml").find("body")

    # First tag not empty
    contents = body.find(id="wikiArticle").find(lambda x: x.name == "p" and x.text)
    result = markdownify(contents).replace("(/en-US/docs", "(https://developer.mozilla.org/en-US/docs")

    return result


async def html_ref(ctx: Context, text: str) -> None:
    """Displays information on an HTML tag."""
    text = text.strip("<>`")

    base_url = f"https://developer.mozilla.org/en-US/docs/Web/HTML/Element/{text}"
    url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

    output = await _process_mozilla_doc(ctx, url)
    if not isinstance(output, str):
        # Error message already sent
        return

    embed = Embed(title=text, description=output, url=url)
    embed.set_author(name="HTML5 Reference")
    embed.set_thumbnail(url="https://www.w3.org/html/logo/badge/html5-badge-h-solo.png")

    await ctx.send(embed=embed)


async def _http_ref(part: str, ctx: Context, text: str) -> None:
    """Displays information about HTTP protocol."""
    base_url = f"https://developer.mozilla.org/en-US/docs/Web/HTTP/{part}/{text}"
    url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

    output = await _process_mozilla_doc(ctx, url)
    if not isinstance(output, str):
        # Error message already sent
        return

    embed = Embed(title=text, description=output, url=url)
    embed.set_author(name="HTTP protocol")
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/HTTP_logo.svg/1280px-HTTP_logo.svg.png")

    await ctx.send(embed=embed)


http_headers = partial(_http_ref, "Headers")
http_methods = partial(_http_ref, "Methods")
http_status = partial(_http_ref, "Status")
csp_directives = partial(_http_ref, "Headers/Content-Security-Policy")


async def _git_main_ref(part: str, ctx: Context, text: str) -> Message:
    """Displays a git help page."""
    text = text.strip("`")

    if part and text == "git":
        # just 'git'
        part = ""
    if not part and not text.startswith("git"):
        # gittutorial, giteveryday...
        part = "git"
    base_url = f"https://git-scm.com/docs/{part}{text}"
    url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as response:
            if response.status != 200:
                return await ctx.send(f"An error occurred (status code: {response.status}). Retry later.")
            if str(response.url) == "https://git-scm.com/docs":
                # Website redirects to home page
                return await ctx.send("No results")

            soup = BeautifulSoup(await response.text(), "lxml")
            sectors = soup.find_all("div", {"class": "sect1"}, limit=3)

            title = sectors[0].find("p").text

            embed = Embed(title=title, url=url)
            embed.set_author(name="Git reference")
            embed.set_thumbnail(url="https://git-scm.com/images/logo@2x.png")

            for tag in sectors[1:]:
                content = "\n".join([markdownify(p) for p in tag.find_all(lambda x: x.name in ["p", "pre"])])
                embed.add_field(name=tag.find("h2").text, value=content[:1024])

            return await ctx.send(embed=embed)


git_ref = partial(_git_main_ref, "git-")
git_tutorial_ref = partial(_git_main_ref, "")


async def sql_ref(ctx: Context, text: str) -> Message:
    """Displays reference on an SQL statement."""
    text = text.strip("`").lower()
    if text in ("check", "unique", "not null"):
        text += " constraint"
    text = re.sub(" ", "-", text)

    base_url = f"http://www.sqltutorial.org/sql-{text}/"
    url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as response:
            if response.status != 200:
                return await ctx.send(f"An error occurred (status code: {response.status}). Retry later.")

            body = BeautifulSoup(await response.text(), "lxml").find("body")
            intro = body.find(lambda x: x.name == "h2" and "Introduction to " in x.string)
            title = body.find("h1").string

            ps = []
            for tag in tuple(intro.next_siblings):
                if tag.name == "h2" and tag.text.startswith("SQL "):
                    break
                if tag.name == "p":
                    ps.append(tag)

            description = "\n".join([markdownify(p) for p in ps])[:2048]

            embed = Embed(title=title, url=url, description=description)
            embed.set_author(name="SQL Reference")
            embed.set_thumbnail(url="https://users.soe.ucsc.edu/~kunqian/logos/sql-logo.png")

            return await ctx.send(embed=embed)


async def haskell_ref(ctx: Context, text: str) -> Message:
    """Displays information on given Haskell topic."""

    text = text.strip("`")

    snake = "_".join(text.split(" "))

    base_url = f"https://wiki.haskell.org/{snake}"
    url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as response:
            if response.status == 404:
                return await ctx.send(f"No results for `{text}`")
            if response.status != 200:
                return await ctx.send(f"An error occurred (status code: {response.status}). Retry later.")

            soup = BeautifulSoup(await response.text(), "lxml").find("div", id="content")

            title = soup.find("h1", id="firstHeading").string
            description = "\n".join(
                [markdownify(p) for p in soup.find_all(lambda x: x.name in ["p", "li"] and tuple(x.parents)[1].name not in ("td", "li"), limit=6,)]
            )[:2048]

            embed = Embed(title=title, description=description, url=url)
            embed.set_thumbnail(url="https://wiki.haskell.org/wikiupload/thumb/4/4a/HaskellLogoStyPreview-1.png/120px-HaskellLogoStyPreview-1.png")

            return await ctx.send(embed=embed)
