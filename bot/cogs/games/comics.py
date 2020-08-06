import io
import random

import aiohttp
from bs4 import BeautifulSoup
from discord import Color, Embed, File
from discord.ext.commands import Cog, Context, command

from bot import config
from bot.core.bot import Bot


class Comics(Cog):
    """View random comics from popular sources."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @command()
    async def ohno(self, ctx: Context) -> None:
        """Send a random 'Webcomic Name' comic."""
        url = "http://webcomicname.com/random"

        async with ctx.typing():
            async with self.session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

            img_url = soup.find(property="og:image")["content"]

            async with self.session.get(img_url) as response:
                img = io.BytesIO(await response.read())

            embed = Embed(title="Random Webcomic", color=Color.blurple())
            embed.set_image(url="attachment://ohno.png")
            file = File(img, "ohno.png")
            await ctx.send(file=file, embed=embed)

    @command()
    async def smbc(self, ctx: Context) -> None:
        """Send a random 'Saturday Morning' comic."""
        url = "http://www.smbc-comics.com/comic/archive"

        async with ctx.typing():
            async with self.session.get(url, headers={"Connection": "keep-alive"}) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

            all_comics = soup.find("select", attrs={"name": "comic"})
            all_comics_url_stubs = [
                option["value"] for option in all_comics.findChildren()
            ]

            random_comic = random.choice(all_comics_url_stubs)
            comic_url = f"http://www.smbc-comics.com/{random_comic}"

            async with self.session.get(
                    comic_url, headers={"Connection": "keep-alive"}
            ) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")
                img_url = soup.find(property="og:image")["content"]

            async with self.session.get(img_url) as response:
                img = io.BytesIO(await response.read())

            embed = Embed(title="Random Sunday Morning", color=Color.blurple())
            embed.set_image(url="attachment://smbc.png")
            file = File(img, "smbc.png")
            await ctx.send(file=file, embed=embed)

    @command()
    async def pbf(self, ctx: Context) -> None:
        """Send a random 'The Perry Bible' comic."""
        url = "http://pbfcomics.com/random"

        async with ctx.typing():
            async with self.session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

            img_url = soup.find(property="og:image")["content"]

            async with self.session.get(img_url) as response:
                img = io.BytesIO(await response.read())

            embed = Embed(title="Random Perry Bible", color=Color.blurple())
            embed.set_image(url="attachment://pbf.png")
            file = File(img, "pbf.png")
            await ctx.send(file=file, embed=embed)

    @command()
    async def cah(self, ctx: Context) -> None:
        """Send a random 'Cyanide and Happiness' comic."""
        url = "http://explosm.net/comics/random"

        async with ctx.typing():
            async with self.session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

            img_url = soup.find(property="og:image")["content"]

            async with self.session.get(img_url) as response:
                img = io.BytesIO(await response.read())

            embed = Embed(
                title="Random Cyanide and Happiness", color=Color.blurple()
            )
            embed.set_image(url="attachment://cah.png")
            file = File(img, "cah.png")
            await ctx.send(file=file, embed=embed)

    @command()
    async def xkcd(self, ctx: Context, comic_type: str = "latest") -> None:
        """See the latest/a random 'xkcd' comic."""
        comic_type = comic_type.lower()

        if comic_type not in ["latest", "random"]:
            url = f"https://xkcd.com/{comic_type}/info.0.json"
        else:
            url = "https://xkcd.com/info.0.json"

        if comic_type == "random":
            async with aiohttp.ClientSession() as session:
                async with session.get("https://xkcd.com/info.0.json") as response:
                    data = await response.json()
                random_comic = random.randint(1, data["num"])

                url = f"https://xkcd.com/{random_comic}/info.0.json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    day, month, year = data["day"], data["month"], data["year"]
                    comic_num = data["num"]

                    embed = Embed(
                        title=data["title"],
                        description=data["alt"],
                        color=Color.blurple(),
                    )
                    embed.set_image(url=data["img"])
                    embed.set_footer(
                        text=f"Comic date : [{day}/{month}/{year}] | Comic Number - {comic_num}"
                    )

                    await ctx.send(embed=embed)
                else:
                    url = "https://xkcd.com/info.0.json"
                    async with aiohttp.ClientSession() as csession:
                        async with csession.get(url) as req:
                            data = await req.json()
                            latest_comic_num = data["num"]

                    help_embed = Embed(
                        title="XKCD HELP",
                        description=f"""
                        **{config.COMMAND_PREFIX}xkcd latest** - (Get the latest comic)
                        **{config.COMMAND_PREFIX}xkcd <num>** - (Enter a comic number | range 1 to {latest_comic_num})
                        **{config.COMMAND_PREFIX}xkcd random** - (Get a random comic)
                        """,
                    )
                    await ctx.send(embed=help_embed)

    @command()
    async def mrls(self, ctx: Context) -> None:
        """Send a random 'Mr. Lovenstein' comic."""
        url = "http://www.mrlovenstein.com/shuffle"

        async with ctx.typing():
            async with self.session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

            img_url = f"http://www.mrlovenstein.com{soup.find(id='comic_main_image')['src']}"

            async with self.session.get(img_url) as response:
                img = io.BytesIO(await response.read())

            embed = Embed(title="Random Mr. Lovenstein", color=Color.blurple())
            embed.set_image(url="attachment://mrls.png")
            file = File(img, "mrls.png")
            await ctx.send(file=file, embed=embed)

    @command()
    async def chainsaw(self, ctx: Context) -> None:
        """Send a random 'Chainsawsuit' comic."""
        url = "http://chainsawsuit.com/comic/random/?random&nocache=1"

        async with ctx.typing():
            async with self.session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

            img_url = soup.find(property="og:image")["content"]

            async with self.session.get(img_url) as response:
                img = io.BytesIO(await response.read())

            embed = Embed(title="Random Chainsawsuit", color=Color.blurple())
            embed.set_image(url="attachment://chainsawsuit.png")
            file = File(img, "chainsawsuit.png")
            await ctx.send(file=file, embed=embed)

    @command()
    async def sarah(self, ctx: Context) -> None:
        """Send a random 'Sarah's Scribbles' comic."""
        url = "http://www.gocomics.com/random/sarahs-scribbles"

        async with ctx.typing():
            async with self.session.get(url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

            img_url = soup.find(property="og:image")["content"]

            async with self.session.get(img_url) as response:
                img = io.BytesIO(await response.read())

            embed = Embed(
                title="Random Sarah Scribbles", color=Color.blurple()
            )
            embed.set_image(url="attachment://sarahscribbles.png")
            file = File(img, "sarahscribbles.png")
            await ctx.send(file=file, embed=embed)


def setup(bot: Bot) -> None:
    """Load the Comics cog."""
    bot.add_cog(Comics(bot))
