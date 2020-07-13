import asyncio
import os
import re
import urllib.parse
from io import BytesIO
import aiohttp
from .utils import constants

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from contextlib import suppress

import discord

# import stackexchange
# from stackexchange import Site
from discord.ext import commands

# from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Cog, Context, Bot
from discord.utils import escape_mentions

from .code_utils import documentation, reference
from .code_utils.utility import get_raw, paste
import typing as t
from .code_utils.tiorun import Tio


class Coding(Cog):
    """To test code and check docs."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.STACKEXCHANGE = os.getenv("STACKEXCHANGE")
        self.session = aiohttp.ClientSession()

    def get_h2_content(self, tag: NavigableString) -> str:
        """Returns content between two h2 tags."""
        bs_siblings = tag.next_siblings
        siblings = []

        # get only tag elements, before the next h2
        for element in bs_siblings:
            if type(element) == NavigableString:
                continue
            if element.name == "h2":
                break
            siblings.append(element.text)  # get the text of the elemets before the next h2
        content = "\n".join(siblings)

        if len(content) >= 1024:
            content = content[:1021] + "..."

        return content

    wrapping = {
        "c": "#include <stdio.h>\nint main() {code}",
        "cpp": "#include <iostream>\nint main() {code}",
        "cs": "using System;class Program {static void Main(string[] args) {code}}",
        "java": "public class Main {public static void main(String[] args) {code}}",
        "rust": "fn main() {code}",
        "d": "import std.stdio; void main(){code}",
    }

    referred = {
        "csp-directives": reference.csp_directives,
        "git": reference.git_ref,
        "git-guides": reference.git_tutorial_ref,
        "haskell": reference.haskell_ref,
        "html5": reference.html_ref,
        "http-headers": reference.http_headers,
        "http-methods": reference.http_methods,
        "http-status-codes": reference.http_status,
        "sql": reference.sql_ref,
    }

    # TODO: lua, java, javascript, asm, c#
    documented = {
        "c": documentation.c_doc,
        "cpp": documentation.cpp_doc,
        "haskell": documentation.haskell_doc,
        "python": documentation.python_doc,
        "rust": documentation.rust_doc,
    }

    @commands.command(
        help="""
        run <language> [--wrapped] [--stats] <code>
        for command-line-options, compiler-flags and arguments you may
        add a line starting with this argument, and after a space add
        your options, flags or args.
        stats option displays more information on execution consumption
        wrapped allows you to not put main function in some languages, which you can see in `list wrapped argument`
        <code> may be normal code, but also an attached file,
        or a link from [hastebin](https://hasteb.in) or [Github gist](https://gist.github.com)
        If you use a link, your command must end with this syntax:
        `link=<link>` (no space around `=`)
        for instance : `run python link=https://hastebin.com/resopedahe.py`
        The link may be the raw version, and with/without the file extension
        If the output exceeds 40 lines or Discord max message length, it will be put
        in a new hastebin and the link will be returned.
        When the code returns your output, you may delete it by clicking :wastebasket: in the following minute.
        Useful to hide your syntax fails or when you forgot to print the result.
        """,
        brief="Execute code in a given programming language",
    )
    async def run(self, ctx: Context, language: str, *, code: str = "") -> t.Union[None, str]:
        """Execute code in a given programming language."""

        options = {"--stats": False, "--wrapped": False}  # the flags to be used when the compiler is needed

        lang = language.strip("`").lower()  # strip the "`" characters to obtain code
        options_amount = len(options)

        # Setting options and removing them from the beginning of the command
        # options may be separated by any single whitespace, which we keep in the list
        code = re.split(r"(\s)", code, maxsplit=options_amount)

        for option in options:
            if option in code[: options_amount * 2]:
                options[option] = True
                i = code.index(option)
                code.pop(i)
                code.pop(i)  # remove following whitespace character

        code = "".join(code)

        compilerFlags = []
        commandLineOptions = []
        args = []
        inputs = []

        lines = code.split("\n")  # split the raw code into lines
        code = []
        for line in lines:
            if line.startswith("input "):
                inputs.append(" ".join(line.split(" ")[1:]).strip("`"))

            elif line.startswith("compiler-flags "):  # check for flags
                compilerFlags.extend(line[15:].strip("`").split(" "))

            elif line.startswith("command-line-options "):
                commandLineOptions.extend(line[21:].strip("`").split(" "))  # cli options

            elif line.startswith("arguments "):
                args.extend(line[10:].strip("`").split(" "))  # arguments

            else:
                code.append(line)  # append the code, if nothing above

        inputs = "\n".join(inputs)
        code = "\n".join(code)
        text = None

        async with ctx.typing():
            if ctx.message.attachments:  # if file is sent instead of raw code in codeblocks
                file = ctx.message.attachments[0]
                if file.size > 20000:  # check the size of file exceeding max limit
                    return await ctx.send("File must be smaller than 20 kio.")

                buffer = BytesIO()
                await ctx.message.attachments[0].save(buffer)
                text = buffer.read().decode("utf-8")
            elif code.split(" ")[-1].startswith("link="):  # if link is sent instead of file or codeblocks
                base_url = urllib.parse.quote_plus(code.split(" ")[-1][5:].strip("/"), safe=";/?:@&=$,><-[]")

                url = get_raw(base_url)  # extract the raw url

                async with self.session.get(url) as response:
                    if response.status == 404:
                        return await ctx.send("Nothing found. Check your link")
                    elif response.status != 200:
                        return await ctx.send("An error occurred. Retry later.")
                    text = await response.text()
                    if len(text) > 20000:
                        return await ctx.send("Code must be shorter than 20,000 characters.")

            elif code.strip("`"):  # strip the raw code, if codeblock
                text = code.strip("`")
                firstLine = text.splitlines()[0]
                if re.fullmatch(r"( |[0-9A-z]*)\b", firstLine):
                    header = len(firstLine) + 1
                    text = text[header:]

            # Ensures code isn't empty after removing options
            if text is None:
                raise commands.MissingRequiredArgument(ctx.command.clean_params["code"])

            quickmap = {
                "asm": "assembly",
                "c#": "cs",
                "c++": "cpp",
                "csharp": "cs",
                "f#": "fs",
                "fsharp": "fs",
                "js": "javascript",
                "nimrod": "nim",
                "py": "python",
                "q#": "qs",
                "rs": "rust",
                "sh": "bash",
            }

            if lang in quickmap:
                lang = quickmap[lang]

            if lang in self.bot.default:
                lang = self.bot.default[lang]

            if lang not in self.bot.languages:  # if lang not found
                matches = "\n".join([language for language in self.bot.languages if lang in language][:10])
                lang = escape_mentions(lang)
                message = f"`{lang}` isn't available."
                if matches:
                    message = message + f" Maybe you meant {matches}?"  # provide a suggestion.

                await ctx.send(message)
                return

            if options["--wrapped"]:
                if not (any(map(lambda x: lang.split("-")[0] == x, self.wrapping))) or lang in ("cs-mono-shell", "cs-csi"):
                    return await ctx.send(f"`{lang}` cannot be wrapped")

                for beginning in self.wrapping:
                    if lang.split("-")[0] == beginning:
                        text = self.wrapping[beginning].replace("code", text)
                        break

            tio = Tio(lang, text, compilerFlags=compilerFlags, inputs=inputs, commandLineOptions=commandLineOptions, args=args)
            result = await tio.send()

            if not options["--stats"]:
                with suppress(ValueError):
                    start = result.rindex("Real time: ")
                    end = result.rindex("%\nExit code: ") + 2
                    result = result[:start] + result[end:]

            if len(result) > 1991 or result.count("\n") > 40:
                # If it exceeds 2000 characters (Discord longest message), counting ` and ph\n characters
                link = await paste(result)

                if link is None:
                    return await ctx.send("Your output was too long, but I couldn't make an online bin out of it")
                return await ctx.send(f"Output was too long (more than 2000 characters or 40 lines) so the hastebn link is: {link}")

            zero = "\N{zero width space}"
            result = re.sub("```", f"{zero}`{zero}`{zero}`{zero}", result)

            # ph, as placeholder, prevents Discord from taking the first line
            # as a language identifier for markdown and remove it
            returned = await ctx.send(f"```ph\n{result}```")

        await returned.add_reaction("🗑")

        def check(reaction: discord.Reaction, user: discord.Member) -> bool:
            return user == ctx.author and str(reaction.emoji) == "🗑" and reaction.message.id == returned.id

        try:
            await self.bot.wait_for("reaction_add", timeout=65.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            await returned.delete()

    @commands.command(aliases=["ref"])
    async def reference(self, ctx: Context, language: str, *, query: str) -> None:
        """Returns element reference from given language."""

        lang = language.strip("`")

        async with ctx.typing():
            if not lang.lower() in self.referred:
                await ctx.send(f"{lang} not available. See `{constants.COMMAND_PREFIX}list references` for available ones.")
                return

        await self.referred[lang.lower()](ctx, query.strip("`"))

    @commands.command(aliases=["docs"])
    async def documentation(self, ctx: Context, language: str, *, query: str) -> None:
        """Returns element reference from given language."""
        lang = language.strip("`")
        async with ctx.typing():
            if not lang.lower() in self.documented:
                await ctx.send(f"{lang} not available. See `{constants.COMMAND_PREFIX}list documentations` for available ones.")
                return

        await self.documented[lang.lower()](ctx, query.strip("`"))

    @commands.command()
    async def man(self, ctx: Context, *, page: str) -> None:
        """Returns the manual's page for a linux command."""
        base_url = f"https://man.cx/{page}"
        url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

        async with ctx.typing():
            async with self.session.get(url) as response:
                if response.status != 200:
                    await ctx.send("An error occurred (status code: {response.status}). Retry later.")
                    return

                    soup = BeautifulSoup(await response.text(), "lxml")

                    nameTag = soup.find("h2", string="NAME\n")

                    if not nameTag:
                        return await ctx.send(f"No manual entry for `{page}`. (Debian)")

                    contents = soup.find_all("nav", limit=2)[1].find_all("li", limit=3)[1:]

                    if contents[-1].string == "COMMENTS":
                        contents.remove(-1)

                    title = self.get_h2_content(nameTag)

                    emb = discord.Embed(title=title, url=f"https://man.cx/{page}")
                    emb.set_author(name="Linux man pages")
                    emb.set_thumbnail(url="https://www.debian.org/logos/openlogo-nd-100.png")

                    for tag in contents:
                        h2 = tuple(soup.find(attrs={"name": tuple(tag.children)[0].get("href")[1:]}).parents)[0]
                        emb.add_field(name=tag.string.strip(), value="\n".join([i for i in self.get_h2_content(h2).split("\n") if i]), inline=False)

        await ctx.send(embed=emb)

    # @commands.cooldown(1, 8, BucketType.user)
    # @commands.command(aliases=["stack"])
    # async def overflow(self, ctx: Context, *, query: str) -> None:
    #     """Queries Stackoverflow and gives you top results."""

    #     async with ctx.typing():
    #         site = Site(stackexchange.StackOverflow, self.STACKEXCHANGE)
    #         site.impose_throttling = True
    #         site.throttle_stop = False

    #         qs = site.search(intitle=query)[:5]
    #         if qs:
    #             emb = discord.Embed(title=query)
    #             emb.set_thumbnail(url=f"http://s2.googleusercontent.com/s2/favicons?domain_url={site.domain}")

    #             for q in qs:
    #                 # Fetch question's data, include vote_counts and answers
    #                 q = site.question(q.id, filter="!b1MME4lS1P-8fK")
    #                 emb.add_field(
    #                     name=f"`{len(q.answers)} answers` Score : {q.score}", value=f"[{q.title}](https://{site.domain}/q/{q.id}", inline=False,
    #                 )

    #             await ctx.send(embed=emb)
    #         else:
    #             await ctx.send("No results Found! Sorry.")

    @commands.command()
    async def list(self, ctx: Context, *, group: t.Optional[str] = None) -> None:
        """Lists available choices for other commands."""

        choices = {
            "documentations": self.documented,
            "references": self.referred,
            "wrapped argument": self.wrapping,
        }

        if group == "languages":
            emb = discord.Embed(
                title=f"Available for {group}",  # {len(data)}
                description="View them on [tio.run](https://tio.run/#), or in [JSON format](https://tio.run/languages.json)",
            )
            await ctx.send(embed=emb)
            return

        if group not in choices:
            emb = discord.Embed(title="Available commands", description=f"`languages`, `{'`, `'.join(choices)}`")
            await ctx.send(embed=emb)
            return

        availables = choices[group]
        description = f"`{'`, `'.join([*availables])}`"
        emb = discord.Embed(title=f"Available for {group}: {len(availables)}", description=description)
        await ctx.send(embed=emb)


def setup(bot: Bot) -> None:
    bot.add_cog(Coding(bot))
