from discord import Embed, Color
from discord.ext.commands import Cog, Bot, Context, is_nsfw, group
import praw
import os
import random
from .utils import constants

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
    username=os.getenv("REDDIT_USERNAME")
)


class Reddit(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group()
    async def reddit(self, ctx: Context) -> None:
        """Administrative information."""
        pass

    @reddit.command()
    async def memes(self, ctx: Context) -> None:
        name = random.choice(constants.reddit["meme"])
        subreddit = reddit.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
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
    async def funny(self, ctx: Context) -> None:
        name = random.choice(constants.reddit["funny"])
        subreddit = reddit.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        if len(randompost.selftext) > 0:
            description = randompost.selftext
        elif len(randompost.selftext) > 2048:
            description = f"{randompost.selftext[:2000]} Read more..."
        else:
            description = "",
        embed = Embed(
            title=randompost.title,
            url=randompost.url,
            description=description,
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
    async def technology(self, ctx: Context) -> None:
        name = random.choice(constants.reddit["tech"])
        subreddit = reddit.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        if len(randompost.selftext) > 0:
            description = randompost.selftext
        elif len(randompost.selftext) > 2048:
            description = f"{randompost.selftext[:2000]} Read more..."
        else:
            description = "",
        embed = Embed(
            title=randompost.title,
            url=randompost.url,
            description=description,
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
    async def videos(self, ctx: Context) -> None:
        name = random.choice(constants.reddit["vid"])
        subreddit = reddit.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        if len(randompost.selftext) > 0:
            description = randompost.selftext
        elif len(randompost.selftext) > 2048:
            description = f"{randompost.selftext[:2000]} Read more..."
        else:
            description = "",
        embed = Embed(
            title=randompost.title,
            url=randompost.url,
            description=description,
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
    @is_nsfw()
    async def nsfw(self, ctx: Context) -> None:
        name = random.choice(constants.reddit["nsfw"])
        subreddit = reddit.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
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
    async def aww(self, ctx: Context) -> None:
        name = random.choice(constants.reddit["aww"])
        subreddit = reddit.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
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
    async def science(self, ctx: Context) -> None:
        name = random.choice(constants.reddit["sci"])
        subreddit = reddit.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        if len(randompost.selftext) > 0:
            description = randompost.selftext
        elif len(randompost.selftext) > 2048:
            description = f"{randompost.selftext[:2000]} Read more..."
        else:
            description = "",
        embed = Embed(
            title=randompost.title,
            url=randompost.url,
            description=description,
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
    async def relation(self, ctx: Context) -> None:
        name = random.choice(constants.reddit["relation`"])
        subreddit = reddit.subreddit(name)

        postlist = list(subreddit.hot(limit=100))

        randompost = random.choice(postlist)
        if len(randompost.selftext) > 0:
            description = f"{randompost.selftext}"
        elif len(randompost.selftext) > 2048:
            description = f"{randompost.selftext[:2000]} Read more..."
        else:
            description = "",
        embed = Embed(
            title=randompost.title,
            url=randompost.url,
            description=description,
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
    async def new(self, ctx: Context, subreddit: str) -> None:
        """sends you the fresh posts from a subreddit"""
        subreddit = reddit.subreddit(f'{subreddit}')
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
        subreddit = reddit.subreddit(f'{subreddit}')
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
