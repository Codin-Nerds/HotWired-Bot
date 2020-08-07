import json
import os
import urllib

import aiohttp
import bleach
import stackexchange
from discord import Color, Embed
from discord.errors import HTTPException
from discord.ext.commands import Cog, Context, command, cooldown
from discord.ext.commands.cooldowns import BucketType

from bot.core.bot import Bot

StackExchangeToken = os.getenv("STACKEXCHANGE")


class Documentation(Cog):
    """I love documentation."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @cooldown(1, 8, BucketType.user)
    @command(aliases=["stackoverflow", "overflow"])
    async def stack_overflow(self, ctx: Context, *, query: str) -> None:
        """Query Stackoverflow and get the top results."""
        async with ctx.typing():
            site = stackexchange.Site(stackexchange.StackOverflow, StackExchangeToken)
            site.impose_throttling = True
            site.throttle_stop = False

            results = site.search(intitle=query)[:5]
            embed = Embed(title="StackOverflow search")
            embed.set_thumbnail(url=f"http://s2.googleusercontent.com/s2/favicons?domain_url={site.domain}")

            description = f"**Query:** {query}\n"

            if results:
                embed.color = Color.blue()
            else:
                embed.color = Color.red()
                description += "\nSorry, No results found for given query."

            for result in results:
                # Fetch question's data, include vote_counts and answers
                result = site.question(result.id, filter="!b1MME4lS1P-8fK")
                description += f"\n**[{result.title}](https://{site.domain}/q/{result.id})**"
                description += f"\n**Score:** {result.score}, **Answers:** {len(result.answers)}\n"

            embed.description = description
            await ctx.send(embed=embed)

    @command()
    async def man(self, ctx: Context, *, program: str) -> None:
        """Return the manual's page for a linux command."""
        base_query = f"https://www.mankier.com/api/v2/mans/?q={program}"
        query_url = urllib.parse.quote_plus(base_query, safe=";/?:@&=$,><-[]")

        async with ctx.typing():
            # Get API query responses
            async with self.session.get(query_url) as response:
                if response.status != 200:
                    await ctx.send(f"An error occurred (status code: {response.status})")
                    return

                results = json.loads(await response.text())["results"]

            # Use first result
            if len(results) > 0:
                result = results[0]
            else:
                await ctx.send("Invalid query, no such command")
                return

            base_url = f"https://www.mankier.com/api/v2/mans/{result['name']}.{result['section']}"
            url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")

            # Load man page from first result
            async with self.session.get(url) as response:
                if response.status != 200:
                    await ctx.send(f"An error occurred (status code: {response.status})")
                    return

                result = json.loads(await response.text())

            embed = Embed(
                title=f"Man page of: **{result['name'].capitalize()}**",
                url=result["url"],
                description=f"**{result['description']}** ({result['section']})"
            )

            for anchor in result['anchors']:
                embed.add_field(
                    name=f"`{bleach.clean(anchor['anchor'], tags=[], strip=True)}`",
                    value=f"{bleach.clean(anchor['description'], tags=[], strip=True)}\n[Link here]({anchor['url']})",
                    inline=False
                )
            # TODO: Solve this with pagination
            try:
                await ctx.send(embed=embed)
            except HTTPException as error:
                if error.code == 50035:
                    await ctx.send(embed=Embed(
                        description="Body is too long to show",
                        color=Color.red()
                    ))
                else:
                    raise error


def setup(bot: Bot) -> None:
    """Load the Documentation cog"""
    bot.add_cog(Documentation(bot))
