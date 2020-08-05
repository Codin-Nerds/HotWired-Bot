from contextlib import suppress
from os.path import splitext

import aiohttp
from discord import Color, Embed, Message, NotFound
from discord.ext.commands import Cog

from bot import config
from bot.core.bot import Bot

FILE_EMBED_DESCRIPTION = (
    f"""
    **Oh No!** Your message got zapped by our spam filter.
    We currently don't allow `.txt` attachments or any source files, so here are some tips you can use: \n
    • Try shortening your message, if it exceeds 2000 character limit
    to fit within the character limit or use a pasting service (see below) \n
    • If you're showing code, you can use codeblocks or use a pasting service like :
    {config.paste_link} or {config.paste_link_2}
    """
)


with open("bot/assets/allowed_filetypes.txt", "r") as f:
    whitelist = []
    for line in f:
        if "#" not in line:
            whitelist.append(line.replace("\n", ""))


class Security(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Find messages with blacklisted attachments."""
        if not message.attachments or not message.guild:
            return

        elif message.author.permissions_in(message.channel).manage_messages:
            return

        file_extensions = {splitext(attachment.filename.lower())[1] for attachment in message.attachments}
        is_blocked = file_extensions - set(whitelist)

        file_pastes = []

        if is_blocked:
            embed = Embed(description=FILE_EMBED_DESCRIPTION, color=Color.dark_blue())

            with suppress(NotFound, ConnectionError):
                for attachment in message.attachments:
                    content = await attachment.read()

                    async with self.session.post("https://hasteb.in/documents", data=content) as resp:
                        key = (await resp.json())['key']
                        file_paste = 'https://www.hasteb.in/' + key

                    file_pastes.append(file_paste)

                await message.delete()
                await message.channel.send(f"Hey {message.author.mention}!", embed=embed)

                paste_embed = Embed(
                    color=Color.gold(),
                    description=f"The Paste(s) of the File(s) Can be found at {', '.join(file_pastes)}",
                    title="File Pastes!"
                )
                await message.channel.send(embed=paste_embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Security(bot))
