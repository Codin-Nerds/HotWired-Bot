import json
import textwrap
import typing as t
from collections import defaultdict
from contextlib import suppress

from discord import Color, Embed, Member, TextChannel, Forbidden
from discord.errors import HTTPException
from discord.ext.commands import Cog, ColourConverter, Context, group

from bot.core.bot import Bot
from bot.core.converters import Unicode


class EmbedData(t.NamedTuple):
    """Data for user embeds."""

    content: str
    embed: Embed


class JsonEmbedParser:
    """This class is used for converting json into embed and vice versa."""

    def __init__(self, ctx: Context, json_dict: dict) -> None:
        self.ctx = ctx
        self.json = JsonEmbedParser.process_dict(json_dict)

    @classmethod
    async def from_str(cls: "JsonEmbedParser", ctx: Context, json_string: str) -> t.Union["JsonEmbedParser", bool]:
        """Return class instance from json string.

        This will return either class instance (on correct json string),
        or False on incorrect json string.
        """
        json_dict = await cls.parse_json(ctx, json_string)
        if json_dict is False:
            return False
        return cls(ctx, json_dict)

    @classmethod
    def from_embed(cls: "JsonEmbedParser", ctx: Context, embed: t.Union[Embed, EmbedData]) -> "JsonEmbedParser":
        """Return class instance from embed."""
        if isinstance(embed, EmbedData):
            embed_dict = embed.embed.to_dict()
            json_dict = {"content": embed.content, "embed": embed_dict}
        else:
            json_dict = embed.to_dict()
        return cls(ctx, json_dict)

    @staticmethod
    async def parse_json(ctx: Context, json_code: str) -> t.Union[dict, bool]:
        """Parse given json code."""
        # Sanitize code (remove codeblocks if any)
        if "```" in json_code:
            json_code = json_code.replace("```json\n", "")
            json_code = json_code.replace("```\n", "")
            json_code = json_code.replace("```json", "")
            json_code = json_code.replace("```", "")

        # Parse the code into JSON
        try:
            return json.loads(json_code)
        except json.JSONDecodeError as error:
            lines = json_code.split("\n")

            embed = Embed(
                description=textwrap.dedent(
                    f"""
                    Sorry, I couldn't parse this JSON:
                    ```
                    {error}
                    ```
                    The error seems to be here *(`line: {error.lineno} col: {error.colno}`)*:
                    ```
                    {lines[error.lineno - 1]}
                    {" " * (int(error.colno) - 1)}^
                    ```
                    """
                ),
                color=Color.red(),
            )
            await ctx.send(f"Sorry {ctx.author.mention}", embed=embed)
            return False

    @staticmethod
    def process_dict(json_dct: dict) -> dict:
        """Set all values to Embed.Empty to avoid keyerrors."""
        try:
            content = json_dct["content"]
        except KeyError:
            content = ""

        try:
            new_json = json_dct["embed"]
        except KeyError:
            new_json = json_dct

        # Set default type to "rich"
        if "type" not in new_json:
            new_json["type"] = "rich"

        # TODO: Correctly implement timestampts
        # Current override will cause errors in make_json
        if "timestamp" in new_json:
            new_json["timestamp"] = Embed.Empty

        return {"content": content, "embed": new_json}

    def make_embed(self) -> EmbedData:
        """Produce an embed from the processed json."""
        embed = Embed.from_dict(self.json["embed"])
        return EmbedData(self.json["content"], embed)

    def make_json(self) -> str:
        """Make it json."""
        return json.dumps(self.json, indent=2)


class Embeds(Cog):
    """A Cog which provides the ability to build a custom embed."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        # Provide an empty embed for every member (key)
        self.embeds = defaultdict(lambda: EmbedData("", Embed()))
        # Provide a default ID of -1 for every member (key) for embed fields
        # setting it to -1 is necessary because adding embed only increments this
        # default value of -1 ensures start on 0
        self.embed_fields = defaultdict(lambda: -1)

    @group(invoke_without_command=True, name="embed", aliases=["embedset", "set_embed"])
    async def embed_group(self, ctx: Context) -> None:
        """Commands for configuring the Embed messages."""
        await ctx.send("This command is not meant to be used on its own!")

    # region: basic embed settings (title, description, footer, image, color, message)

    @embed_group.command(aliases=["set_title"])
    async def title(self, ctx: Context, *, title: Unicode) -> None:
        """Set Title for the Embed."""
        self.embeds[ctx.author].embed.title = title
        await ctx.send("Embeds title updated.")

    @embed_group.command(aliases=["set_description"], name="description")
    async def _description(self, ctx: Context, *, description: Unicode) -> None:
        """Set Description for the Embed."""
        self.embeds[ctx.author].embed.description = description
        await ctx.send("Embeds description updated.")

    @embed_group.command(aliases=["add_description"])
    async def append_description(self, ctx: Context, *, description: Unicode) -> None:
        """Add text into Description of the Embed."""
        self.embeds[ctx.author].embed.description += description
        await ctx.send("Embeds description appended.")

    @embed_group.command(aliases=["set_footer"])
    async def footer(self, ctx: Context, *, footer: Unicode) -> None:
        """Set Footer for the Embed."""
        self.embeds[ctx.author].embed.set_footer(text=footer)
        await ctx.send("Embeds footer updated.")

    @embed_group.command(aliases=["set_image"])
    async def image(self, ctx: Context, url: str) -> None:
        """Set image for the Embed."""
        self.embeds[ctx.author].embed.set_image(url=url)
        await ctx.send("Embeds image updated.")

    @embed_group.command(aliases=["set_color"])
    async def color(self, ctx: Context, color: ColourConverter) -> None:
        """Set color for the Embed.

        `color` can be HEX color code or some of the standard colors (red, blue, ...).
        """
        self.embeds[ctx.author].embed.colour = color
        await ctx.send("Embeds color updated.")

    @embed_group.command(aliases=["content", "msg"])
    async def message(self, ctx: Context, *, message: str) -> None:
        """Set message content for the Embed."""
        self.embeds[ctx.author] = EmbedData(message, self.embeds[ctx.author].embed)
        await ctx.send("Message content updated.")

    # endregion
    # region: author settings

    @embed_group.group(invoke_without_command=True, name="author", aliases=["authorset", "set_author"])
    async def author_group(self, ctx: Context) -> None:
        """Commands for configuring the author of Embed messages."""
        await ctx.send("This command is not meant to be used on its own!")

    @author_group.command(name="name", aliases=["set_name"])
    async def author_name(self, ctx: Context, *, author_name: str) -> None:
        """Set author's name for the Embed."""
        embed = self.embeds[ctx.author].embed
        embed.set_author(name=author_name, url=embed.author.url, icon_url=embed.author.icon_url)
        await ctx.send("Embeds author updated.")

    @author_group.command(name="url", aliases=["set_url"])
    async def author_url(self, ctx: Context, author_url: str) -> None:
        """Set author's URL for Embed."""
        embed = self.embeds[ctx.author].embed
        embed.set_author(name=embed.author.name, url=author_url, icon_url=embed.author.icon_url)
        await ctx.send("Embeds author URL updated.")

    @author_group.command(name="icon", aliases=["set_icon"])
    async def author_icon(self, ctx: Context, author_icon: t.Union[Member, str]) -> None:
        """Set author's icon in the Embed.

        `author_icon` can either be URL to the image or you can mention a user to get his avatar
        """
        if isinstance(author_icon, Member):
            author_icon = author_icon.avatar_url_as(format="png")

        embed = self.embeds[ctx.author].embed
        embed.set_author(name=embed.author.name, url=embed.author.url, icon_url=author_icon)
        await ctx.send("Embeds author icon updated.")

    # endregion
    # region: field settings

    @embed_group.group(invoke_without_command=True, name="field", aliases=["filedset", "set_field"])
    async def field_group(self, ctx: Context) -> None:
        """Group for field-related actions."""
        await ctx.send("This command is not meant to be used on its own!")

    @field_group.command(name="add")
    async def field_add(self, ctx: Context, *, title: t.Optional[Unicode] = None) -> None:
        """Create new field in Embed."""
        self.embeds[ctx.author].embed.add_field(name=title, value="")
        self.embed_fields[ctx.author] += 1
        await ctx.send(f"Embeds field **#{self.embed_fields[ctx.author]}** created")

    @field_group.command(name="remove", aliases=["delete", "rem", "del"])
    async def field_remove(self, ctx: Context, ID: int) -> None:
        """Remove field with specific `ID` from Embed."""
        if 0 <= ID <= self.embed_fields[ctx.author]:
            self.embeds[ctx.author].embed.remove_field(ID)
            self.embed_fields[ctx.author] -= 1
            await ctx.send(f"Embeds field **#{ID}** has been removed.")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    @field_group.command(name="description", aliases=["set_description", "value", "set_value"])
    async def field_description(self, ctx: Context, ID: int, *, description: Unicode) -> None:
        """Set a description for embeds field #`ID`."""
        if 0 <= ID <= self.embed_fields[ctx.author]:
            embed = self.embeds[ctx.author].embed
            embed.set_field_at(
                ID,
                name=embed.fields[ID].name,
                value=description,
                inline=embed.fields[ID].inline
            )
            await ctx.send(f"Embeds field **#{ID}** description updated.")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    @field_group.command(name="append_description", aliases=["add_description", "add_value"])
    async def field_append_description(self, ctx: Context, ID: int, *, description: Unicode) -> None:
        """Set a description for embeds field #`ID`."""
        if 0 <= ID <= self.embed_fields[ctx.author]:
            embed = self.embeds[ctx.author].embed
            embed.set_field_at(
                ID,
                name=embed.fields[ID].name,
                value=embed.fields[ID].value + description,
                inline=embed.fields[ID].inline
            )
            await ctx.send(f"Embeds field **#{ID}** description appended.")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    @field_group.command(name="title", aliases=["set_title", "name", "set_name"])
    async def field_title(self, ctx: Context, ID: int, *, title: Unicode) -> None:
        """Set a title for embeds field #`ID`."""
        if 0 <= ID <= self.embed_fields[ctx.author]:
            embed = self.embeds[ctx.author].embed
            embed.set_field_at(
                ID,
                name=title,
                value=embed.fields[ID].value,
                inline=embed.fields[ID].inline
            )
            await ctx.send(f"Embeds field **#{ID}** description updated.")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    @field_group.command(name="inline", aliases=["set_inline", "in_line", "set_in_line"])
    async def field_inline(self, ctx: Context, ID: int, inline_status: bool) -> None:
        """Choose if embed field #`ID` should be inline or not"""
        if 0 <= ID <= self.embed_fields[ctx.author]:
            embed = self.embeds[ctx.author].embed
            embed.set_field_at(
                ID,
                name=embed.fields[ID].name,
                value=embed.fields[ID].value,
                inline=inline_status
            )
            await ctx.send(f"Embeds field **#{ID}** is now {'' if inline_status else 'not'} inline")
        else:
            await ctx.send(f"Embeds field **#{ID}** doesn't exist.")

    # endregion
    # region: json

    @embed_group.command(aliases=["json_load", "from_json", "json", "import"])
    async def load(self, ctx: Context, *, json_code: str) -> None:
        """Generate Embed from given JSON code."""
        embed_parser = await JsonEmbedParser.from_str(ctx, json_code)
        if embed_parser is not False:
            self.embeds[ctx.author] = embed_parser.make_embed()
            await ctx.send("Embed updated accordingly to provided JSON")
        else:
            await ctx.send("Invalid embed JSON")

    @embed_group.command(aliases=["json_dump", "to_json", "get_json", "export"])
    async def dump(self, ctx: Context) -> None:
        """Export JSON from current Embed."""
        embed_parser = JsonEmbedParser.from_embed(ctx, self.embeds[ctx.author])
        json = embed_parser.make_json()
        await ctx.send(f"```json\n{json}```")

    @embed_group.command()
    async def message_dump(self, ctx: Context, channel: TextChannel, message_id: int) -> None:
        """Dump an embed with it's ID."""
        member = channel.server and channel.server.get_member(ctx.message.author.id)

        if channel != ctx.message.channel and not member:
            await ctx.send("Private Channel, or Invalid Server.")
            return

        with suppress(Forbidden):
            msg = await self.bot.get_message(channel, str(message_id))

        if msg.author.id != self.bot.user.id:
            await ctx.send("Invalid User's Message.")
            return
        elif not msg.embeds:
            await ctx.send("No embeds in The Message.")
            return

        embed_parser = JsonEmbedParser.from_embed(ctx, msg)
        json = embed_parser.make_json()
        await ctx.send(f"```json\n{json}```")

    # endregion
    # region: showing, sending, resetting

    async def send_embed(self, author: Member, channel: TextChannel) -> bool:
        """Send the Embed."""
        try:
            await channel.send(self.embeds[author].content, embed=self.embeds[author].embed)
            return True
        except HTTPException as error:
            embed = Embed(
                description=textwrap.dedent(
                    f"""
                    You're embed is causing an error (code: `{error.code}`):
                    ```{error.response.status}: {error.response.reason}```
                    With message:
                    ```{error.text}```

                    """
                ),
                color=Color.red(),
            )
            await channel.send(f"Sorry {author.mention}", embed=embed)
            return False

    @embed_group.command(aliases=["show"])
    async def preview(self, ctx: Context) -> None:
        """Take a look at the Embed before you post it."""
        await self.send_embed(ctx.author, ctx.channel)

    @embed_group.command()
    async def send(self, ctx: Context, channel: TextChannel) -> None:
        """Send the Embed to the given channel."""
        # Make sure author has permission to manage messages in specified channel
        # Note that the cog check only checks that permission in the channel
        # this message is sent to, not channel where the embed will be sent
        channel_perms = channel.permissions_for(ctx.author)
        if channel_perms.send_messages:
            await ctx.send(f"Your embed was send to {channel.mention}")
            await self.send_embed(ctx.author, channel)
        else:
            await ctx.send("Sorry, you can't send the embed here. You're missing **Manage Messages** permission")

    @embed_group.command()
    async def reset(self, ctx: Context) -> None:
        """Reset the Embed."""
        self.embeds[ctx.author] = EmbedData("", Embed())
        await ctx.send("Your saved embed was reset.")

    # endregion

    def cog_check(self, ctx: Context) -> bool:
        """Only allow users with manage messages permission to invoke commands in this cog.

        This is needed because Embeds can be much longer in comparison to regular messages,
        therefore it would be very easy to spam things and clutter the chat.
        """
        perms = ctx.author.permissions_in(ctx.channel)
        return perms.manage_messages


def setup(bot: Bot) -> Bot:
    """Load the Embeds cog."""
    bot.add_cog(Embeds(bot))
