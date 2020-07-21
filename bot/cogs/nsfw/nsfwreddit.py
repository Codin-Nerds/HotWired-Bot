from random import choice, randint

import discord
import requests
from discord.ext import commands
import aiohttp
from aiocache import cached, SimpleMemoryCache

cache = SimpleMemoryCache()

subreddits = {
    "fourk": ["HighResNSFW", "UHDnsfw",
              "nsfw_hd", "NSFW_Wallpapers", "closeup"],
    "ass": ["ass", "pawg", "AssholeBehindThong", "girlsinyogapants", "girlsinleggings", "bigasses", "asshole", "AssOnTheGlass", "TheUnderbun", "asstastic", "booty",
            "AssReveal", "beautifulbutt", "Mooning", "BestBooties", "brunetteass", "assinthong", "paag", "asstastic", "GodBooty", "Underbun", "datass", "ILikeLittleButts", "datgap"],
    "anal":  ["MasterOfAnal", "analgonewild", "anal", "buttsex",
              "buttsthatgrip", "AnalGW", "analinsertions", "AnalGW", "assholegonewild"],
    "bdsm": ["BDSMGW", "bdsm", "ropeart", "shibari"],
    "blowjob": ["blowjobsandwich", "Blowjobs", "BlowjobGifs", "BlowjobEyeContact",
                "blowbang", "AsianBlowjobs", "SuckingItDry", "OralCreampie", "SwordSwallowers"],
    "boobs": ["boobs", "TheHangingBoobs", "bigboobs", "BigBoobsGW", "hugeboobs", "pokies", "ghostnipples", "PiercedNSFW", "piercedtits", "PerfectTits", "BestTits", "Boobies", "JustOneBoob", "tits", "naturaltitties", "smallboobs", "Nipples",
              "homegrowntits", "TheUnderboob", "BiggerThanYouThought", "fortyfivefiftyfive", "Stacked", "BigBoobsGonewild", "AreolasGW", "TittyDrop", "Titties", "Boobies", "boobbounce", "TinyTits", "cleavage", "BoobsBetweenArms", "BustyNaturals", "burstingout"],
    "cunnilingus": ["cunnilingus", "CunnilingusSelfie", "Hegoesdown"],
    "bottomless": ["upskirt", "Bottomless",
                   "nopanties", "Pantiesdown"],
    "cumshots": ["OralCreampie", "cumfetish", "cumontongue", "cumshots", "CumshotSelfies", "facialcumshots", "pulsatingcumshots", "gwcumsluts",
                 "ImpresssedByCum", "GirlsFinishingTheJob", "amateurcumsluts", "unexpectedcum", "bodyshots", "ContainTheLoad", "bodyshots"],
    "dick": ["DickPics4Freedom", "mangonewild",
             "MassiveCock", "penis", "cock", "ThickDick"],
    "doublepenetration":  ["doublepenetration", "dp_porn", "Technical_DP"],
    "deepthroat": ["DeepThroatTears", "deepthroat", "SwordSwallowers"],
    "gay":  ["gayporn", "ladybonersgw", "mangonewild"],
    "hentai": ["hentai", "thick_hentai", "HQHentai", "AnimeBooty",
               "thighdeology", "ecchigifs", "nsfwanimegifs", "oppai_gif"],
    "lesbian": ["lesbians", "HDLesbianGifs", "amateurlesbians", "Lesbian_gifs"],
    "public": ["RealPublicNudity", "FlashingAndFlaunting", "FlashingGirls", "PublicFlashing",
               "Unashamed", "NudeInPublic", "publicplug", "casualnudity"],
    "rule34": ["rule34", "rule34cartoons", "Rule_34", "Rule34LoL",
               "AvatarPorn", "Overwatch_Porn", "Rule34Overwatch", "WesternHentai"],
    "trap": ["Transex", "DeliciousTraps", "traps", "trapgifs", "GoneWildTrans", "SexyShemales",
             "Shemales", "shemale_gifs", "Shemales", "ShemalesParadise", "Shemale_Big_Cock", "ShemaleGalleries"]
}


class NSFW(commands.Cog):
    conf = {}

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.session = aiohttp.ClientSession()
    
    
    async def fetch_from_reddit(self, urlstr, rating, provider):
        async with self.session.get(urlstr, headers={'User-Agent': "NSFW (https://github.com/The-Codin-Hole/HotWired-Bot)"}) as resp:
            try:
                content = await resp.json(content_type=None)
            except (ValueError, aiohttp.ContentTypeError) as ex:
                print("Pruned by exception, error below:")
                print(ex)
                content = []
        
        if not content or content == [] or (isinstance(content, dict) and "success" in content.keys() and not content["success"]):
            return []
        
        
        good_content = []
        for item in content["data"]["children"]:
            IMGUR_LINKS = "https://imgur.com/", "https://i.imgur.com/", "http://i.imgur.com/", "http://imgur.com", "https://m.imgur.com"
            GOOD_EXTENSIONS = ".png", ".jpg", ".jpeg", ".gif"
            url = item["data"]["url"]
            if url.startswith(IMGUR_LINKS):
                if url.endswith(".mp4"):
                    item["file_url"] = url[:-3] + "gif"
                elif url.endswith(".gifv"):
                    item["file_url"] = url[:-1]
                elif url.endswith(GOOD_EXTENSIONS):
                    item["file_url"] = url
                else:
                    item["file_url"] = url + ".png"
                        
            elif url.startswith("https://gfycat.com/"):
                url_cut = url.strip("https://gfycat.com/")
                if url_cut.islower():
                    continue
                item["file_url"] = "https://thumbs.gfycat.com/" + \
                    url_cut + "-size_restricted.gif"
            elif url.endswith(GOOD_EXTENSIONS):
                    item["file_url"] = url
            else:
                continue
            
            good_content.append(item)
        content = good_content

            
        for item in content:
            item["provider"] = provider
            item["rating"] = rating
            item["post_link"] = "https://reddit.com" + \
                item["data"]["permalink"]
            item["score"] = item["data"]["score"]
            item["tags"] = item["data"]["title"]
            item["author"] = item["data"]["author"]
            
        return content

    async def generic_specific_source(self, ctx, board):
        async with ctx.typing():
            data = await getattr(self, f"fetch_{board}")(ctx)

        data = await self.filter_posts(ctx, data)

        await self.show_nsfw(ctx, data)

    async def filter_posts(self, ctx, data):
        filtered_data = []

        for nsfw in data:
            if nsfw.get("is_deleted"):
                continue

            filtered_data.append(nsfw)

        return filtered_data

    async def show_nsfw(self, ctx, data):
        mn = len(data)
        if mn == 0:
            await ctx.send("No results.")
        else:
            i = randint(0, mn - 1)
            nsfw = data[i]

            # Set colour for each board
            embed = discord.Embed()
            embed.set_image(url=nsfw["file_url"])
            try:
                await ctx.send(embed=embed)
            except discord.client.DiscordException:
                print(data[i])

    @commands.group()
    @commands.guild_only()
    async def reddit(self, ctx):
        pass

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def tags(self, ctx):
        await ctx.send("Reddits tags :\n`4k`, `ass`, `anal`, `bdsm`, `blowjob`, `cunnilingus`, `bottomless`, `cumshots`, `deepthroat`, `dick`, `doublepenetration`, `gay`, `hentai`, `lesbian`, `public`, `rule34`, `hentai`, `boobs`")

    @reddit.command(name="4k")
    @commands.guild_only()
    @commands.is_nsfw()
    async def _4k(self, ctx):
        sub = "4k"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def ass(self, ctx):
        sub = "ass"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def anal(self, ctx):
        sub = "anal"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def bdsm(self, ctx):
        sub = "bdsm"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def blowjob(self, ctx):
        sub = "blowjob"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def cunnilingus(self, ctx):
        sub = "cunnilingus"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def bottomless(self, ctx):
        sub = "bottomless"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def cumshots(self, ctx):

        sub = "cumshots"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def deepthroat(self, ctx):

        sub = "deepthroat"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def dick(self, ctx):

        sub = "dick"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def doublepenetration(self, ctx):

        sub = "double_penetration"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def gay(self, ctx):

        sub = "gay"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def hentai(self, ctx):

        sub = "hentai"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def lesbian(self, ctx):

        sub = "lesbian"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def public(self, ctx):

        sub = "public"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def rule34(self, ctx):

        sub = "rule34"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def trap(self, ctx):

        sub = "trap"
        await self.generic_specific_source(ctx, sub)

    @reddit.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def boobs(self, ctx):

        sub = "boobs"
        await self.generic_specific_source(ctx, sub)

    @cached(ttl=3600, cache=SimpleMemoryCache, key="4k")
    async def fetch_4k(self, ctx):  # 4k fetcher
        all_content = []
        for subreddit in subreddits["fourk"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="ass")
    async def fetch_ass(self, ctx):  # ass fetcher
        all_content = []
        for subreddit in subreddits["ass"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="anal")
    async def fetch_anal(self, ctx):  # anal fetcher
        all_content = []
        for subreddit in subreddits["anal"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="bdsm")
    async def fetch_bdsm(self, ctx):  # bdsm fetcher
        all_content = []
        for subreddit in subreddits["bdsm"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="blowjob")
    async def fetch_blowjob(self, ctx):  # blowjob fetcher
        all_content = []
        for subreddit in subreddits["blowjob"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="boobs")
    async def fetch_boobs(self, ctx):  # boobs fetcher
        all_content = []
        for subreddit in subreddits["boobs"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="cunnilingus")
    async def fetch_cunnilingus(self, ctx):  # cunnilingus fetcher
        all_content = []
        for subreddit in subreddits["cunnilingus"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"

            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="bottomless")
    async def fetch_bottomless(self, ct):  # bottomless fetcher
        all_content = []
        for subreddit in subreddits["bottomless"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="cumshots")
    async def fetch_cumshots(self, ctx):  # cumshots fetcher
        all_content = []
        for subreddit in subreddits["cumshots"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="deepthroat")
    async def fetch_deepthroat(self, ctx):  # deepthroat fetcher

        all_content = []
        for subreddit in subreddits["deepthroat"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="dick")
    async def fetch_dick(self, ctx):  # dick fetcher

        all_content = []
        for subreddit in subreddits["dick"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    # double penetration fetcher
    @cached(ttl=3600, cache=SimpleMemoryCache, key="double_pen")
    async def fetch_double_penetration(self, ctx):
        all_content = []
        for subreddit in subreddits["doublepenetration"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="gay")
    async def fetch_gay(self, ctx):  # gay fetcher
        all_content = []
        for subreddit in subreddits["gay"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="hentai")
    async def fetch_hentai(self, ctx):  # hentai fetcher
        all_content = []
        for subreddit in subreddits["hentai"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="lesbian")
    async def fetch_lesbian(self, ctx):  # lesbian fetcher

        all_content = []
        for subreddit in subreddits["lesbian"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="public")
    async def fetch_public(self, ctx):  # public fetcher

        all_content = []
        for subreddit in subreddits["public"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="rule34")
    async def fetch_rule34(self, ctx):  # rule34 fetcher
        all_content = []
        for subreddit in subreddits["rule34"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="thigh")
    async def fetch_thigh(self, ctx):  # thigh fetcher
        all_content = []
        for subreddit in subreddits["thigh"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content

    @cached(ttl=3600, cache=SimpleMemoryCache, key="trap")
    async def fetch_trap(self, ctx):  # trap fetcher
        all_content = []
        for subreddit in subreddits["trap"]:
            urlstr = "https://reddit.com/r/" + subreddit + "/new.json?limit=100"
            content = await self.fetch_from_reddit(urlstr, "explicit", "Reddit")
            all_content.extend(content)
        return all_content


def setup(bot):
    bot.add_cog(NSFW(bot))
