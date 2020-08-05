import os
import random

import aiohttp
from discord import Color, Embed
from discord.ext.commands import (Bot, BucketType, Cog, Context, command,
                                  cooldown)

NASA_API = os.getenv("NASA_API")


def remove_tags(text: str) -> None:
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


class Nasa(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()
        if NASA_API is None:
            self.cog_unload()

    @command(aliases=["apod"])
    @cooldown(16, 60, BucketType.guild)
    async def astronomy_picture(self, ctx: Context) -> None:
        """Gives you the astronomy picture of the day."""
        async with self.session.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API}") as resp:
            data = await resp.json()

        if len(data["explanation"]) > 2048:
            description = f"{data['explanation'][:2045].strip()}..."
        else:
            description = data["explanation"]
        embed = Embed(
            title=data["title"],
            description=description,
            color=Color.blurple()
        )
        embed.set_image(url=data["hdurl"])
        embed.set_footer(text=f"Taken on {data['date']} by {data['copyright']} | Powered by HotWired")

        await ctx.send(embed=embed)

    @command(aliases=["nsearch"])
    async def nasa_search(self, ctx: Context, *, query: str) -> None:
        """Search for a query on NASA's website."""
        async with self.session.get(f"https://images-api.nasa.gov/search?q={query}") as resp:
            data = await resp.json()

        items = data["collection"]["items"]
        if len(items) > 0:
            rand_item = random.randint(0, len(items) - 1)
            item = items[rand_item]

            embed = Embed(
                title=item["data"][0]["description"],
                color=Color.blurple()
            )
            embed.set_image(url=item["links"][0]["href"])
            embed.set_footer(text=f"ID: {item['data'][0]['nasa_id']} | Powered by HotWired")

            await ctx.send(embed=embed)
        else:
            await ctx.send("No results found!")

    @command(aliases=["nid"])
    async def nasa_id(self, ctx: Context, id: str) -> None:
        """Search for a picture on NASA's website with an id."""
        async with self.session.get(f"https://images-api.nasa.gov/asset/{id}") as resp:
            data = await resp.json()

        try:
            items = data["collection"]["items"][0]["href"]
            embed = Embed(color=Color.blurple())
            embed.set_image(url=items)
            embed.set_footer(text=f"ID: {id} | Powered by HotWired")
        except KeyError:
            await ctx.send("No results found!")

        await ctx.send(embed=embed)

    @command(aliases=["nasapatent"])
    async def nasa_patent(self, ctx: Context, *, patent: str) -> None:
        """Search for a NASA patent."""
        async with self.session.get(f"https://api.nasa.gov/techtransfer/patent/?{patent}&api_key={NASA_API}") as resp:
            data = await resp.json()

        items = data["results"]
        if len(items) > 0:
            rand_item = random.randint(0, len(items) - 1)
            item = items[rand_item]

            if len(remove_tags(item[3][:2000])) > 2048:
                description = f"{item[3][:2000][:2045].strip()}..."
            else:
                description = item[3][:2000]

            embed = Embed(
                title=remove_tags(item[2]),
                description=remove_tags(description),
                color=Color.blurple()
            )
            embed.set_footer(text="Powered by HotWired")

            await ctx.send(embed=embed)
        else:
            await ctx.send("No results Found!")

    @command()
    async def epic(self, ctx: Context, max: int = 1) -> None:
        """Get images from DSCOVR's Earth Polychromatic Imaging Camera. can specify a maximum number of images to retrieve."""
        async with self.session.get("https://epic.gsfc.nasa.gov/api/images.php") as response:
            json = await response.json()

            for i in range(min(max, len(json))):
                embed = Embed(
                    ittle="EPIC image",
                    description=json[i].get("caption"),
                    colour=Color.blurple()
                )
                embed.set_image(url="https://epic.gsfc.nasa.gov/epic-archive/jpg/" + json[i]["image"] + ".jpg")

                await ctx.send(embed=embed)

    @command()
    async def mars(self, ctx: Context, date: str, rover: str = None, number: int = 1) -> None:
        """Get images from Mars. must specify the date (in the form YYYY-MM-DD),and you can specify the rover and the number of images to retrieve."""
        if rover is None:
            rover = random.choice(["curiosity", "opportunity", "spirit"])

        if not rover.lower() in ("curiosity", "opportunity", "spirit"):
            await ctx.send("Sorry but this rover doesn't exist")
            return

        async with self.session.get(
            "https://api.nasa.gov/mars-photos/api/v1/rovers/" + rover.lower() + "/photos", params={"earth_date": date, "api_key": NASA_API}
        ) as response:
            images = await response.json()
            if images.get("photos", []) == []:
                await ctx.send(f"Couldn't Find anything! Invalid Rover : {rover.capitalize()}")
                return

            for i in range(min(number, len(images["photos"]))):
                embed = Embed(
                    title="Picture from " + rover.capitalize(),
                    description="Picture taken from the " + images["photos"][i]["camera"]["full_name"],
                    colour=Color.blurple()
                )
                embed.set_image(url=images["photos"][i]["img_src"])
                embed.set_footer(text="Picture taken on" + images["photos"][i]["earth_date"])
                await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Nasa(bot))
