from discord import Embed, Color
from discord.ext.commands import Cog, Context, command, Bot, cooldown, BucketType
from .utils.constants import Emojis
import aiohttp
import textwrap

BAD_RESPONSES = {
    404: "Issue/pull request not Found! Please enter a valid PR Number!",
    403: "Rate limit is hit! Please try again later!"
}


# TODO : add gitlab commands too ig.
class Github(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @command()
    @cooldown(1, 5, type=BucketType.user)
    async def issue(self, ctx: Context, number: int, repository: str = "HotWired-Bot", user: str = "The-Codin-Hole") -> None:
        """Command to retrieve issues from a GitHub repository."""
        url = f"https://api.github.com/repos/{user}/{repository}/issues/{number}"
        merge_url = f"https://api.github.com/repos/{user}/{repository}/pulls/{number}/merge"

        async with self.session.get(url) as resp:
            json_data = await resp.json()

        if resp.status in BAD_RESPONSES:
            await ctx.send(f"ERROR: {BAD_RESPONSES.get(resp.status)}")
            return

        if "issues" in json_data.get("html_url"):
            if json_data.get("state") == "open":
                title = "Issue Opened"
                icon_url = Emojis.issue
            else:
                title = "Issue Closed"
                icon_url = Emojis.issue_closed
        else:
            async with self.session.get(merge_url) as merge:
                if json_data.get("state") == "open":
                    title = "PR Opened"
                    icon_url = Emojis.pull_request
                elif merge.status == 204:
                    title = "PR Merged"
                    icon_url = Emojis.merge
                else:
                    title = "PR Closed"
                    icon_url = Emojis.pull_request_closed

        issue_url = json_data.get("html_url")
        resp = Embed(
            title=f"{icon_url} {title}",
            colour=Color.gold(),
            description=textwrap.dedent(
                f"""
                Repository : **{user}/{repository}**
                Title : **{json_data.get('title')}**
                ID : **`{number}`**
                Link :  [Here]({issue_url})
                """
            )
        )
        resp.set_author(name="GitHub", url=issue_url)
        await ctx.send(embed=resp)

    @command()
    @cooldown(1, 5, type=BucketType.user)
    async def ghrepo(self, ctx: Context, repo: str = "HotWired-Bot", user: str = "The-Codin-Hole") -> None:
        """
        Show info about a given GitHub repository.

        This command uses the GitHub API and is limited to 1 use per 5 seconds to comply with the rules.
        """
        embed = Embed(color=Color.blue())
        async with await self.session.get(f"https://api.github.com/repos/{user}/{repo}") as resp:
            response = await resp.json()

        if resp.status in BAD_RESPONSES:
            await ctx.send(f"ERROR: {BAD_RESPONSES.get(resp.status)}")
            return

        if response["message"]:
            await ctx.send(f"ERROR: {response['message']}")
        if response["description"] == "":
            desc = "No description provided."
        else:
            desc = response["description"]

        stars = response["stargazers_count"]
        forks = response["forks_count"]
        cmd = f'git clone {response["clone_url"]}'
        embed.title = f"{repo} on GitHub"
        embed.description = f"**{desc}**\nStars: {stars} Forks: {forks}\n Command: {cmd}"

        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Github(bot))
