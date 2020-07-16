from contextlib import suppress
from os.path import splitext

import aiohttp
from discord import Color, Embed, Message, NotFound
from discord.ext.commands import Cog

from bot import config
from bot.core.bot import Bot
from loguru import logger

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


# TODO : add token protection, to stop playing with any type of discord tokens
class Security(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Find messages with blacklisted attachments."""
        if not message.attachments or not message.guild:
            return
        # elif message.author.permissions_in(message.channel).manage_messages:
        #     return

        # TODO: Adjust the message and remove only filtered attachments instead of deleting the whole message
        file_extensions = {splitext(attachment.filename.lower())[1] for attachment in message.attachments}
        is_blocked = file_extensions - set(whitelist)

        if is_blocked:
            log_message = f"User <@{message.author.id}> posted a message on {message.guild.id} with protected attachments"

            if message.author.permissions_in(message.channel).manage_messages:
                logger.trace(f"{log_message}, but he has override roles.")
                return

            logger.debug(f"{log_message}.")
            embed = Embed(description=FILE_EMBED_DESCRIPTION, color=Color.dark_blue())

            with suppress(NotFound, ConnectionError):
                await message.delete()
            await message.channel.send(f"Hey {message.author.mention}!", embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Security(bot))
