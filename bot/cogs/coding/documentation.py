import urllib.parse
from functools import partial
from typing import Literal

import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext.commands import Context


async def python_doc(ctx: Context, text: str) -> None:
    """Filter python.org results based on your query."""
    text = text.strip("`")
    url = "https://docs.python.org/3/genindex-all.html"

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as response:
            if response.status != 200:
                return await ctx.send(f"An error occurred (status code: {response.status}). Retry later.")

            soup = BeautifulSoup(str(await response.text()), "lxml")

            def soup_match(tag: str) -> bool:
                return all(string in tag.text for string in text.strip().split()) and tag.name == "li"

            elements = soup.find_all(soup_match, limit=10)
            links = [tag.select_one("li > a") for tag in elements]
            links = [link for link in links if link is not None]

            if not links:
                return await ctx.send("No results")

            content = [f"[{a.string}](https://docs.python.org/3/{a.get('href')})" for a in links]

            embed = discord.Embed(title="Python 3 docs")
            python_logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/240px-Python-logo-notext.svg.png"
            embed.set_thumbnail(url=python_logo)
            embed.add_field(name=f"Results for `{text}`:", value="\n".join(content), inline=False)

            await ctx.send(embed=embed)


async def cppreference(language: Literal["C", "C++"], ctx: Context, text: str) -> None:
    """Search something on cppreference."""
    text = text.strip("`")

    base_url = "https://cppreference.com/w/cpp/index.php?title=Special:Search&search=" + text
    url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as response:
            if response.status != 200:
                return await ctx.send(f"An error occurred (status code: {response.status}). Retry later.")

            soup = BeautifulSoup(await response.text(), "lxml")

            uls = soup.find_all("ul", class_="mw-search-results")

            if not uls:
                return await ctx.send("No results")

            if language == "C":
                wanted = "w/c/"
                url = "https://wikiprogramming.org/wp-content/uploads/2015/05/c-logo-150x150.png"
            elif language == "C++":
                wanted = "w/cpp/"
                url = "https://isocpp.org/files/img/cpp_logo.png"

            for elem in uls:
                if wanted in elem.select_one("a").get("href"):
                    links = elem.find_all("a", limit=10)
                    break

            content = [f"[{a.string}](https://en.cppreference.com/{a.get('href')})" for a in links]
            embed = discord.Embed(title=f"{language} docs")
            embed.set_thumbnail(url=url)
            embed.add_field(name=f"Results for `{text}` :", value="\n".join(content), inline=False)

            await ctx.send(embed=embed)


c_doc = partial(cppreference, "C")
cpp_doc = partial(cppreference, "C++")


async def haskell_doc(ctx: Context, text: str) -> None:
    """Search something on wiki.haskell.org."""
    text = text.strip("`")

    snake = "_".join(text.split(" "))

    base_url = f"https://wiki.haskell.org/index.php?title=Special%3ASearch&profile=default&search={snake}&fulltext=Search"
    url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as response:
            if response.status != 200:
                return await ctx.send(f"An error occurred (status code: {response.status}). Retry later.")

            results = BeautifulSoup(await response.text(), "lxml").find("div", class_="searchresults")

            if results.find("p", class_="mw-search-nonefound") or not results.find("span", id="Page_title_matches"):
                return await ctx.send("No results")

            # Page_title_matches is first
            ul = results.find("ul", "mw-search-results")

            embed = discord.Embed(title="Haskell docs")
            embed.set_thumbnail(url="https://wiki.haskell.org/wikiupload/thumb/4/4a/HaskellLogoStyPreview-1.png/120px-HaskellLogoStyPreview-1.png")

            content = []
            for li in ul.find_all("li", limit=10):
                a = li.find("div", class_="mw-search-result-heading").find("a")
                content.append(f"[{a.get('title')}](https://wiki.haskell.org{a.get('href')})")

            embed.add_field(name=f"Results for `{text}` :", value="\n".join(content), inline=False)

            await ctx.send(embed=embed)


async def rust_doc(ctx, text: str) -> None:
    """Get the doc.rust-lang.org results based on your query."""
    text = text.strip('`')
    if text.startswith("std::"):
        text = text[5:]

    url = "https://doc.rust-lang.org/stable/std/all.html"

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url) as response:
            if response.status != 200:
                return await ctx.send(f'An error occurred (status code: {response.status}). Retry later.')

            soup = BeautifulSoup(str(await response.text()), 'lxml')

            def soup_match(tag) -> None:
                return all(string in tag.text for string in text.strip().split()) and tag.name == 'li'

            elements = soup.find_all(soup_match, limit=10)
            links = [tag.select_one("a") for tag in elements]
            links = [link for link in links if link is not None]

            if not links:
                return await ctx.send("No results")

            content = [f"[{a.string}](https://doc.rust-lang.org/stable/std/{a.get('href')})" for a in links]

            emb = discord.Embed(title="Rust docs")
            emb.set_thumbnail(
                url='https://upload.wikimedia.org/wikipedia/commons/thumb/d/d'
                    '5/Rust_programming_language_black_logo.svg/240px-Rust_programming_language_black_logo.svg.png'
            )
            emb.add_field(name=f'Results for `{text}` :', value='\n'.join(content), inline=False)

            await ctx.send(embed=emb)
