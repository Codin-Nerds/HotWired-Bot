import json
import os
import random

from discord import Color, Embed
from discord.ext.commands import Bot, Cog, Context, group, is_nsfw
from praw import Reddit as RedditAPI
from praw.exceptions import MissingRequiredAttributeException
from loguru import logger


async def reddit_embed(subreddit: str, randompost: RedditAPI.submission) -> Embed:
    embed = Embed(colour=Color.green(), url=randompost.url)

    if len(randompost.title) > 0 and len(randompost.title) < 256:
        embed.title = randompost.title
    elif len(randompost.title) > 256:
        embed.title = f"{randompost.title[:200]}..."

    if len(randompost.selftext) > 0 and len(randompost.selftext) < 2048:
        embed.description = randompost.selftext
    elif len(randompost.selftext) > 2048:
        embed.description = f"{randompost.selftext[:2000]} Read more..."

    if not randompost.url.startswith("https://v.redd.it/") or randompost.url.startswith("https://youtube.com/"):
        embed.set_image(url=randompost.url)

    embed.set_footer(text=f"👍 {randompost.score} | 💬 {len(randompost.comments)} | Powered By HotWired")

    embed.set_author(
        name=f"u/{randompost.author}",
        icon_url=randompost.author.icon_img,
        url=f"https://www.reddit.com/user/{randompost.author}",
    )

    embed.add_field(
        name="SubReddit",
        value=f"[r/{subreddit}](https://www.reddit.com/r/{subreddit}/)",
        inline=False,
    )

    return embed


with open("bot/assets/subreddit.json", "r") as f:
    subreddits = json.load(f)


class Reddit(Cog):
    def __init__(self, bot: Bot) -> None:
        try:
            self.reddit_client = RedditAPI(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT"),
                username=os.getenv("REDDIT_USERNAME"),
            )
        except MissingRequiredAttributeException:
            logger.error("Reddit cog requires correct enviroment variables to run.")
            self.cog_unload()
        self.bot = bot

    @group()
    async def reddit(self, ctx: Context) -> None:
        """Reddit commands."""
        pass

    @reddit.command(aliases=["meme"])
    async def memes(self, ctx: Context) -> None:
        """Get random memes."""
        name = random.choice(subreddits["meme"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @reddit.command()
    async def funny(self, ctx: Context) -> None:
        """Get a funny picture."""
        name = random.choice(subreddits["funny"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @reddit.command(aliases=["tech"])
    async def technology(self, ctx: Context) -> None:
        """Get a post about tech."""
        name = random.choice(subreddits["tech"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @reddit.command()
    async def videos(self, ctx: Context) -> None:
        name = random.choice(subreddits["vid"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @reddit.command()
    @is_nsfw()
    async def nsfw(self, ctx: Context) -> None:
        """Get a nsfw picture."""
        name = random.choice(subreddits["nsfw"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @reddit.command()
    async def aww(self, ctx: Context) -> None:
        """Get a random aww picture."""
        name = random.choice(subreddits["aww"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @reddit.command()
    async def science(self, ctx: Context) -> None:
        """Get a science fact."""
        name = random.choice(subreddits["sci"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @reddit.command()
    async def relation(self, ctx: Context) -> None:
        """Get a relation story."""
        name = random.choice(subreddits["relation"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @reddit.command()
    async def new(self, ctx: Context, subreddit: str) -> None:
        """sends you the fresh posts from given subreddit."""
        subreddit = self.reddit_client.subreddit(f"{subreddit}")
        postlist = list(subreddit.hot(limit=10))
        randompost = random.choice(postlist)

        if randompost.over_18:
            if ctx.channel.is_nsfw():
                if "https://v.redd.it/" in randompost.url:
                    await ctx.send(randompost.title)
                    await ctx.send(randompost.url)
                elif "https://youtube.com/" in randompost.url:
                    await ctx.send(randompost.title)
                    await ctx.send(randompost.url)
                else:
                    embed = await reddit_embed(subreddit, randompost)
                    await ctx.send(embed=embed)

            else:
                await ctx.send("**STOP!** , **NSFW** commands can only be used in NSFW channels")
        else:
            if "https://v.redd.it/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            elif "https://youtube.com/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            else:
                embed = await reddit_embed(subreddit, randompost)
                await ctx.send(embed=embed)

    @reddit.command()
    async def hot(self, ctx: Context, subreddit: str) -> None:
        """sends you the hottest posts from given subreddit."""
        subreddit = self.reddit_client.subreddit(f"{subreddit}")
        postlist = list(subreddit.hot(limit=10))
        randompost = random.choice(postlist)

        if randompost.over_18:
            if ctx.channel.is_nsfw():
                if "https://v.redd.it/" in randompost.url:
                    await ctx.send(randompost.title)
                    await ctx.send(randompost.url)
                elif "https://youtube.com/" in randompost.url:
                    await ctx.send(randompost.title)
                    await ctx.send(randompost.url)

                else:
                    embed = await reddit_embed(subreddit, randompost)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("**STOP!** , **NSFW** commands can only be used in NSFW channels")
        else:
            if "https://v.redd.it/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            elif "https://youtube.com/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)

            else:
                embed = await reddit_embed(subreddit, randompost)
                await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Reddit(bot))
