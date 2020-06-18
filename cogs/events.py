import traceback

from discord import Color, Embed, Message, Guild, Member
from discord.ext.commands import Bot, Cog

import re
import aiohttp


class Custom(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    def get_link_code(string: str) -> str:
        return string.split("/")[-1]

    @staticmethod
    async def check_our_invite(full_link: str, guild: Guild) -> bool:
        guild_invites = await guild.invites()
        for invite in guild_invites:
            # discord.gg/code resolves to https://discordapp.com/invite/code after using session.get(invite)
            if Custom.get_link_code(invite.url) == Custom.get_link_code(full_link):
                return True
        return False

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        # Check that the message is not from bot account
        if message.author.bot:
            return

        elif not isinstance(message.author, Member):
            return

        elif message.author.guild_permissions.administrator:
            return

        if "https:" in message.content or "http:" in message.content:
            base_url = re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.content)

            for invite in base_url:
                try:
                    async with self.session.get(invite) as response:
                        invite = str(response.url)
                except aiohttp.ClientConnectorError:
                    continue

                if "discordapp.com/invite/" in invite or "discord.gg/" in invite:
                    if not await Custom.check_our_invite(invite, message.guild):
                        await message.channel.send(f"{message.author.mention} You are not allowed to post other Server's invites!")

    @Cog.listener()
    async def on_error(self, event: str, *args, **kwargs) -> None:
        error_message = f"```py\n{traceback.format_exc()}\n```"
        if len(error_message) > 2000:
            async with self.session.post("https://www.hastebin.com/documents", data=error_message) as resp:
                error_message = "https://www.hastebin.com/" + (await resp.json())["key"]

        embed = Embed(color=Color.red(), description=error_message, title=event)

        if not self.dev_mode:
            await self.error_hook.send(embed=embed)
        else:
            traceback.print_exc()


def setup(bot: Bot) -> None:
    bot.add_cog(Custom(bot))
