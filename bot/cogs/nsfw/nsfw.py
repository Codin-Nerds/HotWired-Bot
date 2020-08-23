import json
import os
import random

from discord import Color, Embed
from discord.ext.commands import Bot, Cog, Context, group, is_nsfw
from praw import Reddit as RedditAPI
from praw.exceptions import MissingRequiredAttributeException
from loguru import logger


async def reddit_embed(subreddit: str, randompost: RedditAPI.submission) -> Embed:
    """Make a reddit post an embed."""
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
        IMGUR_LINKS = "https://imgur.com/", "https://i.imgur.com/", "http://i.imgur.com/", "http://imgur.com", "https://m.imgur.com"
        ACCEPTED_EXTENSIONS = ".png", ".jpg", ".jpeg", ".gif"

        url = randompost.url

        if url.startswith(IMGUR_LINKS):
            if url.endswith(".mp4"):
                url = url[:-3] + "gif"

            elif url.endswith(".gifv"):
                url = url[:-1]

            elif url.endswith(ACCEPTED_EXTENSIONS):
                url = url

            else:
                url = url + ".png"

        elif url.startswith("https://gfycat.com/"):
            url_cut = url.replace("https://gfycat.com/", "")

            url = f"https://thumbs.gfycat.com/{url_cut}-size_restricted.gif"

        elif url.endswith(ACCEPTED_EXTENSIONS):
            url = url

        embed.set_image(url=url)

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


with open(os.path.sep.join(("bot", "assets", "subreddit.json")), "r") as f:
    subreddits = json.load(f)

with open("bot/assets/nsfw_subreddit.json", "r") as f:
    nsfw_subreddits = json.load(f)


class Nsfw(Cog):
    """Nsfw, Pictures of the nature."""

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
    async def nsfw(self, ctx: Context) -> None:
        """Nsfw commands."""

    @nsfw.command()
    @is_nsfw()
    async def img(self, ctx: Context) -> None:
        """Get a NSFW picture."""
        name = random.choice(subreddits["nsfw"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    async def new(self, ctx: Context, subreddit: str) -> None:
        """Retrieve fresh posts from the given subreddit."""
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

    @nsfw.command()
    async def hot(self, ctx: Context, subreddit: str) -> None:
        """Retrieve the hottest posts from the given subreddit."""
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

    @nsfw.command(name="4k")
    @is_nsfw()
    async def _4k(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        name = random.choice(nsfw_subreddits["fourk"])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def ass(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "ass"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def anal(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "anal"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def bdsm(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "bdsm"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def blowjob(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "blowjob"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def cunnilingus(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "cunnilingus"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def bottomless(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "bottomless"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def cumshots(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "cumshots"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def deepthroat(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "deepthroat"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def dick(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "dick"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def doublepenetration(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "double_penetration"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def gay(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "gay"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def hentai(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "hentai"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def lesbian(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "lesbian"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def public(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "public"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def rule34(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "rule34"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def trap(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "trap"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def boobs(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "boobs"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def ahegao(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "ahegao"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def group(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "group"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def milf(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "milf"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def thigh(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "thigh"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def redhead(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "redhead"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def wild(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "wild"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = self.reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))
        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if ("https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url):
            await ctx.send(randompost.url)
