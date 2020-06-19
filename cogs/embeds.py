import json
import textwrap
import typing as t
from collections import defaultdict

from discord import Color, Embed, Member, TextChannel
from discord.errors import HTTPException
from discord.ext.commands import Bot, Cog, ColourConverter, Context, group


class JsonEmbedParser:
    def __init__(self, ctx: Context, json_dict: dict) -> None:
        self.ctx = ctx
        self.json = JsonEmbedParser.fill_empty_values(json_dict)

    @classmethod
    async def from_str(cls: "JsonEmbedParser", ctx: Context, json_string: str) -> t.Union["JsonEmbedParser", bool]:
        """
        Return class instance from json string

        This will return either class instance (on correct json string),
        or False on incorrect json string.
        """
        json_dict = await cls.parse_json(ctx, json_string)
        if json_dict is False:
            return False
        else:
            return cls(ctx, json_dict)

    @staticmethod
    async def parse_json(ctx: Context, json_code: str) -> t.Union[dict, bool]:
        # Sanitize code (remove codeblocks if any)
        if "```" in json_code:
            json_code = json_code.replace("```json\n", "")
            json_code = json_code.replace("```\n", "")
            json_code = json_code.replace("```json", "")
            json_code = json_code.replace("```", "")

        try:
            return json.loads(json_code)
        except json.JSONDecodeError as e:
            lines = json_code.split("\n")

            embed = Embed(
                description=textwrap.dedent(
                    f"""
                    Sorry, I couldn't parse this JSON:
                    ```
                    {e}
                    ```
                    The error seems to be here *(`line: {e.lineno} col: {e.colno}`)*:
                    ```
                    {lines[e.lineno - 1]}
                    {" " * (int(e.colno) - 1)}^
                    ```
                    """
                ),
                color=Color.red(),
            )
            await ctx.send(f"Sorry {ctx.author.mention}", embed=embed)
            return False

    @staticmethod
    def fill_empty_values(json_dct: dict) -> defaultdict:
        """Set all values to Embed.Empty to avoid keyerrors."""
        new_json = defaultdict(lambda: Embed.Empty, json_dct)

        # Some of the values needs to be subscriptable, set those explicitly here
        subscriptable = ["image", "thumbnail", "author", "footer"]
        for param in subscriptable:
            try:
                new_json["embed"][param] = defaultdict(lambda: Embed.Empty, new_json["embed"][param])
            except KeyError:
                new_json["embed"][param] = defaultdict(lambda: Embed.Empty)

        try:
            for field in new_json["embed"]["fields"]:
                field = defaultdict(lambda: Embed.Empty, field)
        except KeyError:
            new_json["embed"]["fields"] = []

        print(new_json)
        return new_json

    def make_embed(self) -> t.Tuple[str, Embed]:
        jsonc = self.json["embed"]

        content = self.json["content"]

        embed = Embed(
            title=jsonc["title"],
            description=jsonc["description"],
            colour=jsonc["color"],
            url=jsonc["url"],
            # TODO: Fix timestamp
            # timestamp=datetime.datetime.utcformattimestamp()
        )

        # Setting URLs with no value would result in HTTPException on send
        if jsonc["image"]["url"] is not Embed.Empty:
            embed.set_image(url=jsonc["image"]["url"])
        if jsonc["thumbnail"]["url"] is not Embed.Empty:
            embed.set_thumbnail(url=jsonc["thumbnail"]["url"])
        # Author's name can't be Embed.Empty (it will result in string "Embed.Empty" as the name)
        if jsonc["author"]["name"] is not Embed.Empty:
            embed.set_author(name=jsonc["author"]["name"], url=jsonc["author"]["url"], icon_url=jsonc["author"]["icon_url"])

        embed.set_footer(text=jsonc["footer"]["text"], icon_url=jsonc["footer"]["icon_url"])

        for field in jsonc["fields"]:
            embed.add_field(name=field["name"], value=field["value"])

        return (content, embed)

    async def send_embed(self, ctx: Context) -> None:
        content, embed = self.make_embed()
        await ctx.send(content, embed=embed)


class Embeds(Cog):
    """A Cog which provides the ability to build a custom embed."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        # Provide an empty embed for every member (key)
        self.embeds = defaultdict(lambda: Embed())
        # Provide a default ID of -1 for every member (key) for embed fields
        # setting it to -1 is necessary because adding embed only increments this
        # default value of -1 ensures start on 0
        self.embed_fields = defaultdict(lambda: -1)

    @group(invoke_without_command=True, name="embed", aliases=["embedset", "set_embed"])
    async def embed_group(self, ctx: Context) -> None:
        """Commands for configuring the Embed messages."""
        await ctx.send("This command is not meant to be used on its own!")

    # region: basic embed settings (title, description, footer, image, color)

    @embed_group.command(aliases=["set_title"])
    async def title(self, ctx: Context, *, title: str) -> None:
        """Set Title for the Embed."""
        self.embeds[ctx.author].title = title
        await ctx.send("Embeds title updated.")

    @embed_group.command(aliases=["set_description"])
    async def description(self, ctx: Context, *, description: str) -> None:
        """Set Description for the Embed."""
        self.embeds[ctx.author].description = description
        await ctx.send("Embeds description updated.")

    @embed_group.command(aliases=["add_description"])
    async def append_description(self, ctx: Context, *, description: str) -> None:
        """Add text into Description of the Embed."""
        self.embeds[ctx.author].description += description
        await ctx.send("Embeds description appended.")

    @embed_group.command(aliases=["set_footer"])
    async def footer(self, ctx: Context, *, footer: str) -> None:
        """Set Footer for the Embed."""
        self.embeds[ctx.author].set_footer(text=footer)
        await ctx.send("Embeds footer updated.")

    @embed_group.command(aliases=["set_image"])
    async def image(self, ctx: Context, url: str) -> None:
        """Set image for the Embed."""
        self.embeds[ctx.author].set_image(url=url)
        await ctx.send("Embeds image updated.")

    @embed_group.command(aliases=["set_color"])
    async def color(self, ctx: Context, color: ColourConverter) -> None:
        """
        Set color for the Embed.

        `color` can be HEX color code or some of the standard colors (red, blue, ...).
        """
        self.embeds[ctx.author].colour = color
        await ctx.send("Embeds color updated.")

    # endregion
    # region: author settings

    @embed_group.group(invoke_without_command=True, name="author", aliases=["authorset", "set_author"])
    async def author_group(self, ctx: Context) -> None:
        """Commands for configuring the author of Embed messages."""
        await ctx.send("This command is not meant to be used on its own!")

    @author_group.command(name="name", aliases=["set_name"])
    async def author_name(self, ctx: Context, author_name: str) -> None:
        """Set authors name for the Embed."""
        self.embeds[ctx.author].set_author(name=author_name, url=self.embeds[ctx.author].author.url, icon_url=self.embeds[ctx.author].author.icon_url)
        await ctx.send("Embeds author updated.")

    @author_group.command(name="url", aliases=["set_url"])
    async def author_url(self, ctx: Context, author_url: str) -> None:
        """Set authors URL for Embed."""
        self.embeds[ctx.author].set_author(name=self.embeds[ctx.author].author.name, url=author_url, icon_url=self.embeds[ctx.author].author.icon_url)
        await ctx.send("Embeds author URL updated.")

    @author_group.command(name="icon", aliases=["set_icon"])
    async def author_icon(self, ctx: Context, author_icon: t.Union[Member, str]) -> None:
        """
        Set authors icon in the Embed.

        `author_icon` can either be URL to the image or you can mention a user to get his avatar
        """
        if not isinstance(author_icon, str):
            author_icon = author_icon.avatar_url_as(format="png")

        self.embeds[ctx.author].set_author(name=self.embeds[ctx.author].author.name, url=self.embeds[ctx.author].author.url, icon_url=author_icon)
        await ctx.send("Embeds author icon updated.")

    # endregion
    # region: field settings

    @embed_group.group(invoke_without_command=True, name="field", aliases=["filedset", "set_field"])
    async def field_group(self, ctx: Context) -> None:
        await ctx.send("This command is not meant to be used on its own!")

    @field_group.command(name="add")
    async def field_add(self, ctx: Context, *, title: t.Optional[str] = None) -> None:
        """Create new field in Embed."""
        self.embeds[ctx.author].add_field(name=title, value="")
        self.embed_fields[ctx.author] += 1
        await ctx.send(f"Embeds field **#{self.embed_fields[ctx.author]}** created")

    @field_group.command(name="remove", aliases=["delete", "rem", "del"])
    async def field_remove(self, ctx: Context, ID: int) -> None:
        """Remove filed with specific `ID` from Embed."""
        if ID >= 0 and ID <= self.embed_fields[ctx.author]:
            self.embeds[ctx.author].remove_field(ID)
            self.embed_fields[ctx.author] -= 1
            await ctx.send(f"Embeds field **#{ID}** has been removed.")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    @field_group.command(name="description", aliases=["set_description", "value", "set_value"])
    async def field_description(self, ctx: Context, ID: int, *, description: str) -> None:
        """Set a description for embeds field #`ID`."""
        if ID >= 0 and ID <= self.embed_fields[ctx.author]:
            self.embeds[ctx.author].set_field_at(ID, name=self.embeds[ctx.author].fields[ID].name, value=description)
            await ctx.send(f"Embeds field **#{ID}** description updated.")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    @field_group.command(name="append_description", aliases=["add_description"])
    async def field_append_description(self, ctx: Context, ID: int, *, description: str) -> None:
        """Set a description for embeds field #`ID`."""
        if ID >= 0 and ID <= self.embed_fields[ctx.author]:
            self.embeds[ctx.author].set_field_at(
                ID, name=self.embeds[ctx.author].fields[ID].name, value=self.embeds[ctx.author].fields[ID].value + description
            )
            await ctx.send(f"Embeds field **#{ID}** description appended.")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    @field_group.command(name="title", aliases=["set_title", "name", "set_name"])
    async def field_title(self, ctx: Context, ID: int, *, title: str) -> None:
        """Set a title for embeds field #`ID`."""
        if ID >= 0 and ID <= self.embed_fields[ctx.author]:
            self.embeds[ctx.author].set_field_at(ID, name=title, value=self.embeds[ctx.author].fields[ID].value)
            await ctx.send(f"Embeds field **#{ID}** description updated.")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    @field_group.command(name="inline", aliases=["set_inline", "in_line", "set_in_line"])
    async def field_inline(self, ctx: Context, ID: int, inline_status: bool) -> None:
        """Choose if embed field #`ID` should be inline or not"""
        if ID >= 0 and ID <= self.embed_fields[ctx.author]:
            self.embeds[ctx.author].set_field_at(
                ID, name=self.embeds[ctx.author].fields[ID].name, value=self.embeds[ctx.author].fields[ID].value, inline=inline_status
            )
            await ctx.send(f"Embeds field **#{ID}** is now {'' if inline_status else 'not'} inline")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    # endregion
    # region: sending and displaying embed

    async def send_embed(self, author: Member, channel: TextChannel) -> bool:
        try:
            await channel.send(embed=self.embeds[author])
            return True
        except HTTPException as e:
            embed = Embed(
                description=textwrap.dedent(
                    f"""
                    You're embed is causing an error (code: `{e.code}`):
                    ```{e.response.status}: {e.response.reason}```
                    With message:
                    ```{e.text}```

                    """
                ),
                color=Color.red(),
            )
            await channel.send(f"Sorry {author.mention}", embed=embed)
            return False

    @embed_group.command()
    async def preview(self, ctx: Context) -> None:
        """Take a look at the Embed before you post it"""
        await self.send_embed(ctx.author, ctx.channel)

    @embed_group.command()
    async def send(self, ctx: Context, channel: TextChannel) -> None:
        # Make sure author has permission to manage messages in specified channel
        # Note that the cog check only checks that permission in the channel
        # this message is sent to, not channel where the embed will be sent
        channel_perms = channel.permissions_for(ctx.author)
        if channel_perms.send_messages:
            await ctx.send(f"Your embed was send to {channel.mention}")
            await self.send_embed(ctx.author, channel)
        else:
            await ctx.send("Sorry, you can't send the embed here. You're missing **Manage Messages** permission")

    # endregion
    # region: json

    @embed_group.command(aliases=["json_load", "from_json", "json"])
    async def load(self, ctx: Context, *, json_code: str) -> None:
        """Generate Embed from given JSON code"""
        embed_parser = await JsonEmbedParser.from_str(ctx, json_code)
        if embed_parser is not False:
            await embed_parser.send_embed(ctx)

    # endregion

    def cog_check(self, ctx: Context) -> bool:
        """
        Only allow users with manage messages permission to invoke commands in this cog.

        This is needed because Embeds can be much longer in comparison to regular messages,
        therefore it would be very easy to spam things and clutter the chat.
        """
        perms = ctx.author.permissions_in(ctx.channel)
        return perms.manage_messages


def setup(bot: Bot) -> Bot:
    bot.add_cog(Embeds(bot))
