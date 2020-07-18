import hashlib
import re
import unicodedata
from typing import Tuple

from bot.core.bot import Bot

from discord import Color, Embed
from discord.ext.commands import Cog, Context, command


class Tools(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.hash_algos = sorted([h for h in hashlib.algorithms_available if h.islower()])

    @command()
    async def charinfo(self, ctx: Context, *, characters: str) -> None:
        """Shows you information on up to 25 unicode characters."""
        match = re.match(r"<(a?):(\w+):(\d+)>", characters)
        if match:
            embed = Embed(
                title="Non-Character Detected",
                description="Only unicode characters can be processed, but a custom Discord emoji " "was found. Please remove it and try again.",
            )
            embed.colour = Color.red()
            await ctx.send(embed=embed)
            return

        if len(characters) > 25:
            embed = Embed(title=f"Too many characters ({len(characters)}/25)")
            embed.colour = Color.red()
            await ctx.send(embed=embed)
            return

        def get_info(char: str) -> Tuple[str, str]:
            digit = f"{ord(char):x}"
            if len(digit) <= 4:
                u_code = f"\\u{digit:>04}"
            else:
                u_code = f"\\U{digit:>08}"
            url = f"https://www.compart.com/en/unicode/U+{digit:>04}"
            name = f"[{unicodedata.name(char, '')}]({url})"
            info = f"`{u_code.ljust(10)}`: {name} - {char}"
            return info, u_code

        charlist, rawlist = zip(*(get_info(c) for c in characters))

        embed = Embed(description="\n".join(charlist))
        embed.set_author(name="Character Info")

        if len(characters) > 1:
            embed.add_field(name="Raw", value=f"`{''.join(rawlist)}`", inline=False)

        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Tools(bot))
