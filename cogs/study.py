import asyncio
import json
from io import BytesIO
from urllib import parse

import aiohttp
import discord
from discord.ext import commands

import setup as s
from PIL import Image, ImageChops, ImageDraw, ImageFont

from .utils import constants


url = 'http://api.mathjs.org/v4/'

ENDPOINT = "http://api.wolframalpha.com/v2/query?"
WEB = "https://www.wolframalpha.com/"

FONT = ImageFont.truetype("assets/wolf_font.ttf", 15, encoding="unic")


class Study(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pcalc(self, ctx):
        pass

    @commands.command()
    async def calc(self, ctx: commands.Context, *equations: str) -> None:
        """Calculate an equation."""
        if not equations:
            await ctx.reply("Please give me something to evaluate. See help for usage details.")
            return

        exprs = equations.split('\n')
        request = {
            "expr": exprs,
            "precision": 14
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(request)) as resp:
                answer = await resp.json()

        if "error" not in answer or "result" not in answer:
            emb = discord.Embed(
                description="Something unknown went wrong, sorry! Could not complete your request.",
                color=discord.Color.red()
            )
            await ctx.send(embed=emb)
            return

        if answer["error"]:
            emb = discord.Embed(
                title="The following error occured while calculating",
                description=f"{answer['error']}",
                color=discord.Color.red()
            )
            emb.set_footer(text=f'Invoked by {str(ctx.message.author)}')
            await ctx.send(embed=emb)
            return

        ctr = 0
        for eq in equations:
            embed = discord.Embed(title="Equation Results")

            embed.add_field(name="**❯❯ Question**", value=eq, inline=False)
            embed.add_field(name="**❯❯ Result**", value=answer['result'][ctr], inline=False)

            embed.set_footer(text=f'Invoked by {str(ctx.message.author)}')

            await ctx.send(embed=embed)
            ctr += 1

    def build_web_url(self, query: str):
        """Returns the url for Wolfram Alpha search for this query."""
        return f"{WEB}input/?i={parse.quote_plus(query)}"

    async def get_query(self, query: str, appid: str, **kwargs):
        """Fetches the provided query from the Wolfram Alpha computation engine."""
        params = {
            "input": query,
            "appid": appid,
            "format": "image,plaintext",
            "reinterpret": "true",
            "units": "metric",
            "output": "json"
        }
        params.update(kwargs)

        async with aiohttp.get(ENDPOINT, params=params) as r:
            if r.status == 200:
                data = await r.read()
                return json.loads(data.decode('utf8'))

    async def assemble_pod_image(self, atoms, dimensions):
        """Draws the given atoms onto a canvas of the given dimensions."""
        im = Image.new('RGB', dimensions, color=(255, 255, 255))
        draw = ImageDraw.Draw(im)

        for atom in atoms:
            if "text" in atom:
                draw.text(atom["coord"], atom["text"], fill=(0, 0, 0), font=FONT)
            if "image" in atom:
                im.paste(atom["image"], atom["coord"])
        return im

    async def glue_pods(self, flat_pods):
        """Turns a complete list of flattened pods into a list of images, split appropriately."""
        indent_width = 10
        image_border = 5
        margin = 5

        split_height = 300

        splits = []
        atoms = []
        y_coord = 5
        max_width = 0

        for pod in flat_pods:
            if y_coord > split_height:
                splits.append((atoms, (max_width, y_coord)))
                max_width = 0
                y_coord = 5
                atoms = []

            indent = pod[2] * indent_width
            if pod[0]:
                atoms.append({"coord": (margin + indent, y_coord), "text": pod[0]})
                text_width, text_height = FONT.getsize(pod[0])
                y_coord += text_height
                max_width = max(text_width + indent + 2 * margin, max_width)
            if pod[1]:
                y_coord += image_border
                atoms.append({"coord": (margin + indent + indent_width, y_coord), "image": pod[1]})
                y_coord += pod[1].height
                y_coord += image_border
                max_width = max(pod[1].width + indent + indent_width + image_border + margin, max_width)
        splits.append((atoms, (max_width, y_coord)))
        split_images = []
        for split in splits:
            split_images.append(await self.assemble_pod_image(*split))
        return split_images

    async def flatten_pods(self, pod_data, level=0, text=False, text_field="plaintext"):
        """Takes the list of pods formatted as in wolf output and returns flattened pods."""
        flat_pods = []
        for pod in pod_data:
            if "img" in pod and not text:
                flat_pods.append((pod["title"], await self.handle_image(pod["img"]), level))
            elif text_field in pod and text:
                flat_pods.append((pod["title"], pod[text_field], level))
            elif "title" in pod:
                flat_pods.append((pod["title"], None, level))
            if "subpods" in pod:
                flat_pods.extend(await self.flatten_pods(pod["subpods"], level=level + 1, text=text))
        return flat_pods

    async def handle_image(self, image_data):
        """Takes an image dict as given by the wolf. Retrieves, trims and returns an Image object."""
        target = image_data["src"]
        async with aiohttp.ClientSession() as session:
            async with session.get(target, allow_redirects=False) as resp:
                response = await resp.read()
        image = Image.open(BytesIO(response))
        return self.smart_trim(image, border=10)

    def smart_trim(self, im, border=0):
        bg = Image.new(im.mode, im.size, border)
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

    async def pods_to_filedata(self, pod_data):
        flat_pods = await self.flatten_pods(pod_data)
        images = await self.glue_pods(flat_pods)
        output_data = []
        for result in images:
            output = BytesIO()
            result.save(output, format="PNG")
            output.seek(0)
            output_data.append(output)
        return output_data

    async def pods_to_textdata(self, pod_data):
        flat_pods = await self.flatten_pods(pod_data, text=True)
        tabchar = "​ "
        tab = tabchar * 2

        fields = []
        current_name = ""
        current_lines = []
        for title, text, level in flat_pods:
            if level == 0:
                if current_lines:
                    fields.append((current_name if current_name else "Pod", "\n".join(current_lines), 0))
                current_name = title
                current_lines = []
            elif title:
                current_lines.append(f"{tab * level}**{title}**")
            if text:
                current_lines.append(f"{tab * (level + 1)}{text}")
        return fields

    def triage_pods(self, pod_list):
        if "primary" in pod_list[0] and pod_list[0]["primary"]:
            return ([pod_list[0]], pod_list[1:])
        else:
            important = [pod_list[0]]
            important.extend([pod for pod in pod_list if ("primary" in pod and pod["primary"])])
            if len(important) == 1 and len(pod_list) > 1:
                important.append(pod_list[1])
            extra = [pod for pod in pod_list[1:] if pod not in important]
            return (important, extra)
        
    @commands.command()
    @commands.execute("flags", flags=["text"])
    async def cmd_query(self, ctx, *query):
        """Get the Answer to the Query."""
        if query == "":
            await ctx.send(f"Please submit a valid query! Like, `{constants.COMMAND_PREFIX}ask differentiate x+y^2 with respect to x`.")
            return

        temp_msg = await ctx.reply("Sending query, please wait.")

        appid = s.WOLFRAM_APPID

        try:
            result = await self.get_query(query, appid)
        except Exception:
            await ctx.send("An unknown exception occurred while fetching query.")
            return
        if not result:
            await ctx.soft_delete(temp_msg)
            await ctx.send("Failed to get a response.")
            return
        if "queryresult" not in result:
            await ctx.soft_delete(temp_msg)
            await ctx.send("Did not get a valid response.")
            return

        link = f"[Display results online and refine query]({self.build_web_url(ctx.arg_str)})"
        if not result["queryresult"]["success"] or result["queryresult"]["numpods"] == 0:
            desc = f"Wolfram Alpha doesn't understand your query!\n Perhaps try rephrasing your question?\n{link}"
            embed = discord.Embed(description=desc)
            embed.set_footer(icon_url=ctx.author.avatar_url, text="Requested by {ctx.author}")
            await ctx.soft_delete(temp_msg)
            await ctx.offer_delete(await ctx.reply(embed=embed))
            return

        if ctx.flags["text"]:
            fields = await self.pods_to_textdata(result["queryresult"]["pods"])
            embed = discord.Embed(description=link)
            embed.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author}")
            await ctx.emb_add_fields(embed, fields)
            await ctx.soft_delete(temp_msg)
            out_msg = await ctx.send(embed=embed)
            await ctx.offer_delete(out_msg)
            return

        important, extra = self.triage_pods(result["queryresult"]["pods"])

        data = (await self.pods_to_filedata(important))[0]
        output_data = [data]

        embed = discord.Embed(description=link)
        embed.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author}")

        await ctx.safe_delete_msgs([temp_msg])
        out_msg = await ctx.send(file_data=data, file_name="wolf.png", embed=embed)
        asyncio.ensure_future(ctx.offer_delete(out_msg))

        if extra:
            try:
                await ctx.bot.add_reaction(out_msg, ctx.bot.objects["emoji_more"])
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
            else:
                res = await ctx.bot.wait_for_reaction(
                    message=out_msg,
                    user=ctx.author,
                    emoji=ctx.bot.objects["emoji_more"],
                    timeout=300
                )
                if res is None:
                    try:
                        await ctx.bot.remove_reaction(out_msg, ctx.bot.objects["emoji_more"], ctx.me)
                    except discord.NotFound:
                        pass
                    except Exception:
                        pass
                elif res.reaction.emoji == ctx.bot.objects["emoji_more"]:
                    temp_msg = await ctx.send("Processing results, please wait.")

                    output_data[0].seek(0)
                    output_data.extend(await self.pods_to_filedata(extra))
                    try:
                        await ctx.soft_delete(out_msg)
                        await ctx.soft_delete(temp_msg)
                    except discord.NotFound:
                        pass

                    out_msgs = []
                    for file_data in output_data[:-1]:
                        out_msgs.append(await ctx.reply(file_data=file_data, file_name="wolf.png"))
                    out_msgs.append(await ctx.reply(file_data=output_data[-1], file_name="wolf.png", embed=embed))
                    out_msg = out_msgs[-1]
                    asyncio.ensure_future(ctx.offer_delete(out_msg, to_delete=out_msgs))

        for output in output_data:
            output.close()


def setup(client):
    client.add_cog(Study(client))
