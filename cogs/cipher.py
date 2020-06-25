import base64
import hashlib
import string

from discord.ext import commands

from assets.context import Command, argument, example, usage_info


class Ciphers(commands.Cog):
    character_set = [string.ascii_lowercase, string.ascii_uppercase, string.digits]

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return self.bot.is_ready():

    @commands.command(cls=Command,
                      description="Shifts the letters within a message",
                      syntax=[argument(True, "Shift defaults to 3"), argument(True, "Message")],
                      usage_information=[
                          usage_info("", "If a shift value is not found at the start "
                                         "of the message it would try and find it at the end")
                      ],
                      examples=[argument("Hello", "Returns Khoor"), argument("10 Hello", "Returns Rovvy")])
    async def shift(self, ctx, shift: typing.Optional[int], *, message):
        if not shift:
            M = message.split()
            try:
                shift = int(M[-1])
                message = " ".join(M[:-1])
            except ValueError:
                shift = 3

        if not message:
            return await ctx.send(f"I need some text to shift by {shift} places!")

        # If the shift is higher than 25 then this would convert the shift to a value that is lower than 25
        shift %= 26

        shifted_characters = list(map(lambda m: m[shift:] + m[:shift], self.character_set))
        translation_rules = str.maketrans("".join(self.character_set), "".join(shifted_characters))
        await ctx.send(message.translate(translation_rules))

    @commands.command(cls=Command,
                      description="Flips the alphabet, turns A to Z, B to Y...",
                      syntax=[argument(True, "Message")],
                      examples=[example("Hello", "Returns \"Svool\"")])
    async def atbash(self, ctx, *, message):
        # Reverses the character set
        reversed_characters = list(map(lambda m: m[::-1], self.character_set))
        translation_rules = str.maketrans("".join(self.character_set), "".join(reversed_characters))
        await ctx.send(message.translate(translation_rules))

    @commands.command(cls=Command,
                      description="Encode a message in base64!",
                      syntax=[argument(True, "Message")],
                      usage_information=[
                          usage_info("", "Conversion is done via encoding the UTF-8 "
                                         "codepoint to base64 for each letter in the message")
                      ],
                      examples=[example("Hello", "Return SGVsbG8=")])
    async def encode64(self, ctx, *, message):
        b64msg = base64.b64encode(message.encode("utf-8")).decode("utf-8")
        await ctx.send(b64msg)

    @commands.command(cls=Command,
                      description="Decodes a message in base64",
                      syntax=[argument(True, "Message")],
                      usage_information=[
                          usage_info("", "Conversion is done via encoding the UTF-8 "
                                         "codepoint to base64 for each letter in the message")
                      ],
                      examples=[example("SGVsbG8=", "Returns \"Hello\"")])
    async def decode64(self, ctx, *, message):
        """Decodes a message in base64
        [prefix]decode64 [Required: message]
        Conversion is done via decoding a base64 UTF-8
        codepoint for each letter in the message
        **Example**:
          • `!decode64 SGVsbG8=` Returns "Hello"
        """
        try:
            normal_text = base64.b64decode(message.encode("utf-8")).decode("utf-8")
            await ctx.send(normal_text)
        except base64.binascii.Error:
            await ctx.send("Padding error")

    @commands.command(cls=Command,
                      description="Hashes a message using SHA3-256",
                      syntax=[argument(True, "Message")],
                      example=[example("hello", "Returns 3338be694f50c5f338814986cdf0686453a888b84f424d792af4b9202398f392")])
    async def sha256(self, ctx, *, message):
        sha256_msg = hashlib.sha3_256(message.encode("utf-8")).hexdigest()
        await ctx.send(sha256_msg)

    @commands.command(cls=Command,
                      description="Hashes a message using SHA3-512",
                      syntax=[argument(True, "Message")],
                      examples=[
                          example("hello", "75d527c368f2efe848ecf6b073a36767800805e9eef2b1857d5f984f036"
                                           "eb6df891d75f72d9b154518c1cd58835286d1da9a38deba3de98b5a53e5ed78a84976")
                      ])
    async def sha512(self, ctx, *, message):
        sha256_msg = hashlib.sha3_512(message.encode("utf-8")).hexdigest()
        await ctx.send(sha256_msg)


def setup(bot):
    bot.add_cog(Ciphers(bot))
