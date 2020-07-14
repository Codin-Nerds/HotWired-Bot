from discord import Embed, Color
from discord.ext.commands import Cog, Bot, Context, is_nsfw, group
import random
from bot import config
import praw
import os

reddit_client = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
    username=os.getenv("REDDIT_USERNAME")
)


async def reddit_embed(subreddit: str, randompost: praw.Reddit.submission) -> Embed:
    embed = Embed(
        title=randompost.title,
        colour=Color.green(),
        url=randompost.url
    )

    if len(randompost.selftext) > 0 and len(randompost.selftext) < 2048:
        embed.description = randompost.selftext
    elif len(randompost.selftext) > 2048:
        embed.description = f"{randompost.selftext[:2000]} Read more..."

    if not randompost.url.startswith('https://v.redd.it/') or randompost.url.startswith("https://youtube.com/"):
        embed.set_image(url=randompost.url)

    embed.set_footer(
        text=f"👍 {randompost.score} | 💬 {len(randompost.comments)} | Powered By HotWired",
    )
    embed.set_author(
        name=f"u/{randompost.author}",
        icon_url=randompost.author.icon_img,
        url=f"https://www.reddit.com/user/{randompost.author}"
    )
    embed.add_field(
        name="SubReddit",
        value=f"[r/{subreddit}](https://www.reddit.com/r/{subreddit}/)",
        inline=False
    )

    return embed


class Reddit(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group()
    async def reddit(self, ctx: Context) -> None:
        """Reddit commands."""
        pass

    @reddit.command(aliases=["meme"])
    async def memes(self, ctx: Context) -> None:
        name = random.choice(config.reddit["meme"])
        subreddit = reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @reddit.command()
    async def funny(self, ctx: Context) -> None:
        name = random.choice(config.reddit["funny"])
        subreddit = reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @reddit.command(aliases="tech")
    async def technology(self, ctx: Context) -> None:
        name = random.choice(config.reddit["tech"])
        subreddit = reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @reddit.command()
    async def videos(self, ctx: Context) -> None:
        name = random.choice(config.reddit["vid"])
        subreddit = reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @reddit.command()
    @is_nsfw()
    async def nsfw(self, ctx: Context) -> None:
        name = random.choice(config.reddit["nsfw"])
        subreddit = reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @reddit.command()
    async def aww(self, ctx: Context) -> None:
        name = random.choice(config.reddit["aww"])
        subreddit = reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @reddit.command()
    async def science(self, ctx: Context) -> None:
        name = random.choice(config.reddit["sci"])
        subreddit = reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @reddit.command()
    async def relation(self, ctx: Context) -> None:
        name = random.choice(config.reddit["relation"])
        subreddit = reddit_client.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @reddit.command()
    async def new(self, ctx: Context, subreddit: str) -> None:
        """sends you the fresh posts from a subreddit"""
        subreddit = reddit_client.subreddit(f'{subreddit}')
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
                    embed = Embed(
                        title=randompost.title,
                        url=randompost.url,
                        colour=Color.green()
                    )
                    embed.set_image(url=randompost.url)
                    embed.set_footer(
                        text=f"👍 {randompost.score} | 💬 {len(randompost.comments)} | Powered By HotWired",
                    )
                    embed.set_author(
                        name=f"u/{randompost.author.name}",
                        icon_url=randompost.author.icon_img,
                        url=f"https://www.reddit.com/user/{randompost.author.name}"
                    )
                    embed.add_field(
                        name="SubReddit",
                        value=f"[r/{subreddit}](https://www.reddit.com/r/{subreddit}/)",
                        inline=False
                    )
                    await ctx.send(embed=embed)

            else:
                await ctx.send(
                    "**STOP!** , **NSFW** commands can only be used in NSFW channels"
                )
        else:
            if "https://v.redd.it/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            elif "https://youtube.com/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            else:
                embed = Embed(
                    title=randompost.title,
                    url=randompost.url,
                    colour=Color.green()
                )
                embed.set_image(url=randompost.url)
                embed.set_footer(
                    text=f"👍 {randompost.score} | 💬 {len(randompost.comments)} | Powered By HotWired",
                )
                embed.set_author(
                    name=f"u/{randompost.author.name}",
                    icon_url=randompost.author.icon_img,
                    url=f"https://www.reddit.com/user/{randompost.author.name}"
                )
                embed.add_field(
                    name="SubReddit",
                    value=f"[r/{subreddit}](https://www.reddit.com/r/{subreddit}/)",
                    inline=False
                )
                await ctx.send(embed=embed)

    @reddit.command()
    async def hot(self, ctx: Context, subreddit: str) -> None:
        """sends you the hottest posts from a subreddit"""
        subreddit = reddit_client.subreddit(f'{subreddit}')
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
                    embed = Embed(
                        title=randompost.title,
                        url=randompost.url,
                        colour=Color.green()
                    )
                    embed.set_image(url=randompost.url)
                    embed.set_footer(
                        text=f"👍 {randompost.score} | 💬 {len(randompost.comments)} | Powered By HotWired",
                    )
                    embed.set_author(
                        name=f"u/{randompost.author.name}",
                        icon_url=randompost.author.icon_img,
                        url=f"https://www.reddit.com/user/{randompost.author.name}"
                    )
                    embed.add_field(
                        name="SubReddit",
                        value=f"[r/{subreddit}](https://www.reddit.com/r/{subreddit}/)",
                        inline=False
                    )
                    await ctx.send(embed=embed)
            else:
                await ctx.send(
                    "**STOP!** , **NSFW** commands can only be used in NSFW channels"
                )
        else:
            if "https://v.redd.it/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            elif "https://youtube.com/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)

            else:
                embed = Embed(
                    title=randompost.title,
                    url=randompost.url,
                    colour=Color.green()
                )
                embed.set_image(url=randompost.url)
                embed.set_footer(
                    text=f"👍 {randompost.score} | 💬 {len(randompost.comments)} | Powered By HotWired",
                )
                embed.set_author(
                    name=f"u/{randompost.author.name}",
                    icon_url=randompost.author.icon_img,
                    url=f"https://www.reddit.com/user/{randompost.author.name}"
                )
                embed.add_field(
                    name="SubReddit",
                    value=f"[r/{subreddit}](https://www.reddit.com/r/{subreddit}/)",
                    inline=False
                )
                await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Reddit(bot))
