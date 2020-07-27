import base64
import hashlib
import textwrap

from discord import Embed
from discord.ext.commands import Cog, Context, command

from bot import config
from bot.core.bot import Bot


class Conversion(Cog):
    """This is a Cog for converting and encoding strings."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.hash_algos = sorted([h for h in hashlib.algorithms_available if h.islower()])

    @command(name="ascii")
    async def _ascii(self, ctx: Context, *, text: str) -> None:
        """Convert a string to ascii."""
        ascii_text = " ".join(str(ord(letter)) for letter in text)
        description = textwrap.dedent(
            f"""
            • **Text:** `{text}`
            • **ASCII:** `{ascii_text}`
            """
        )
        embed = Embed(title="ASCII Convertor", description=description)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command()
    async def unascii(self, ctx: Context, *, ascii_text: str) -> None:
        """Convert ascii to string."""
        try:
            text = "".join(chr(int(i)) for i in ascii_text.split(" "))
            description = textwrap.dedent(
                f"""
                • **ASCII:** `{ascii_text}`
                • **Text:** `{text}`
                """
            )
            embed = Embed(title="ASCII Convertor", description=description)
            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

            await ctx.send(embed=embed)
        except ValueError:
            await ctx.send(f"Invalid sequence. Example usage : `{config.COMMAND_PREFIX}unascii 104 101 121`")

    @command()
    async def byteconvert(self, ctx: Context, value: int, unit: str = "Mio") -> None:
        """Convert into Bytes.

        Accepted units are: `O`, `Kio`, `Mio`, `Gio`, `Tio`, `Pio`, `Eio`, `Zio`, `Yio`
        """
        units = ("O", "Kio", "Mio", "Gio", "Tio", "Pio", "Eio", "Zio", "Yio")
        unit = unit.capitalize()

        if unit not in units:
            return await ctx.send(f"Available units are `{'`, `'.join(units)}`.")

        embed = Embed(title="Binary Convertor")
        # TODO: Look into this code
        index = units.index(unit)

        for i, u in enumerate(units):
            result = round(value / 2 ** ((i - index) * 10), 14)
            embed.add_field(name=u, value=result)

            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command(name="hash")
    async def _hash(self, ctx: Context, algorithm: str, *, text: str) -> None:
        """Hash a string using specified algorithm."""
        algo = algorithm.lower()

        if algo not in self.hash_algos:
            # TODO: `self.algos` doesn't seem to be defined
            matches = "\n".join([supported for supported in self.hash_algos if algo in supported][:10])
            message = f"`{algorithm}` not available."
            if matches:
                message += f" Did you mean:\n{matches}"
            await ctx.send(message)
            return

        try:
            hash_object = getattr(hashlib, algo)(text.encode("utf-8"))
        except AttributeError:
            hash_object = hashlib.new(algo, text.encode("utf-8"))

        description = textwrap.dedent(
            f"""
            • **Text:** `{text}`
            • **Hashed:** `{hash_object.hexdigest()}`
            """
        )

        embed = Embed(title=f"{algorithm} hash", description=description)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command()
    async def encode(self, ctx: Context, *, text: str) -> None:
        """Convert a string to binary."""
        message_bytes = text.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode("ascii")

        embed = Embed(title="Base64 Encode", description=base64_message)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command()
    async def decode(self, ctx: Context, *, text: str) -> None:
        """Convert a binary to string."""
        base64_bytes = text.encode("ascii")
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode("ascii")

        embed = Embed(title="Base64 Decode", description=message)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Load the Conversion cog"""
    bot.add_cog(Conversion(bot))
