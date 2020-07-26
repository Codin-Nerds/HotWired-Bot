import textwrap

from bot.config import Emojis

from discord import Color, Embed
from discord.ext.commands import (Bot, BucketType, Cog, Context, command,
                                  cooldown)

BAD_RESPONSES = {
    404: "Issue/pull request not Found! Please enter a valid PR Number!",
    403: "Rate limit is hit! Please try again later!"
}


class Github(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = bot.aio_session

    @command(aliases=["pullrequest", "pullrequests", "issues"])
    @cooldown(1, 5, type=BucketType.user)
    async def issue(self, ctx: Context, issue_num: int, repository: str = "HotWired-Bot", user: str = "The-Codin-Hole") -> None:
        """Command to retrieve issues or PRs from a GitHub repository."""
        url = f"https://api.github.com/repos/{user}/{repository}/issues/{issue_num}"
        merge_url = f"https://api.github.com/repos/{user}/{repository}/pulls/{issue_num}/merge"

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
                ID : **`{issue_num}`**
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
