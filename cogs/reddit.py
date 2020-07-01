from discord import Embed, Color
from discord.ext.commands import Cog, Bot, command, Context, is_nsfw
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

    @command()
    async def memes(self, ctx: Context) -> None:
        name = random.choice(constants.meme_sublist)
        subreddit = reddit.subreddit(name)

        hotposts = subreddit.hot(limit=100)
        postlist = list(hotposts)

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

    @command()
    async def funny(self, ctx: Context) -> None:
        name = random.choice(constants.funny_sublist)
        subreddit = reddit.subreddit(name)

        hotposts = subreddit.hot(limit=100)
        postlist = list(hotposts)

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

    @command()
    async def technology(self, ctx: Context) -> None:
        name = random.choice(constants.tech_sublist)
        subreddit = reddit.subreddit(name)

        hotposts = subreddit.hot(limit=100)
        postlist = list(hotposts)

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

    @command()
    async def videos(self, ctx: Context) -> None:
        name = random.choice(constants.vid_sublist)
        subreddit = reddit.subreddit(name)

        hotposts = subreddit.hot(limit=100)
        postlist = list(hotposts)

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

    @command()
    @is_nsfw()
    async def nsfw(self, ctx: Context) -> None:
        name = random.choice(constants.nsfw_sublist)
        subreddit = reddit.subreddit(name)

        hotposts = subreddit.hot(limit=100)
        postlist = list(hotposts)

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

    @command()
    async def aww(self, ctx: Context) -> None:
        name = random.choice(constants.aww_sublist)
        subreddit = reddit.subreddit(name)

        hotposts = subreddit.hot(limit=100)
        postlist = list(hotposts)

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

    @command()
    async def science(self, ctx: Context) -> None:
        name = random.choice(constants.sci_sublist)
        subreddit = reddit.subreddit(name)

        hotposts = subreddit.hot(limit=100)
        postlist = list(hotposts)

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

    @command()
    async def relation(self, ctx: Context) -> None:
        name = random.choice(constants.relation_sublist)
        subreddit = reddit.subreddit(name)

        hotposts = subreddit.hot(limit=100)
        postlist = list(hotposts)

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

    @command(aliases=["new"])
    async def newpost(self, ctx: Context, subreddit: str) -> None:
        """sends you the fresh posts from a subreddit"""
        subreddit = reddit.subreddit(f'{subreddit}')
        newposts = subreddit.new(limit=10)
        postlist = list(newposts)
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

    @command()
    async def hotpost(self, ctx: Context, subreddit: str) -> None:
        """sends you the hottest posts from a subreddit"""
        subreddit = reddit.subreddit(f'{subreddit}')
        hotposts = subreddit.hot(limit=10)
        postlist = list(hotposts)
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
