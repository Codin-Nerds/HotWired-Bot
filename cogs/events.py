import traceback
import textwrap

from discord import Color, Embed, Message, Guild
from discord.ext.commands import Bot, Cog

import re
import aiohttp

from .utils import constants

PREFIX = constants.COMMAND_PREFIX


class Events(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.dev_mode = constants.DEV_MODE
        self.session = aiohttp.ClientSession()

    @staticmethod
    def get_link_code(string: str) -> str:
        return string.split("/")[-1]

    @staticmethod
    async def is_our_invite(full_link: str, guild: Guild) -> bool:
        guild_invites = await guild.invites()
        for invite in guild_invites:
            # discord.gg/code resolves to https://discordapp.com/invite/code after using session.get(invite)
            if Events.get_link_code(invite.url) == Events.get_link_code(full_link):
                return True
        return False

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        # Check that the message is not from bot account
        if message.author.bot:
            return

        # DM Check.
        elif message.guild is None:
            return

        # Is an Admin.
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
                    if not await Events.is_our_invite(invite, message.guild):
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

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        logchannel = self.bot.get_channel(constants.log_channel)

        embed = Embed(
            title="Greetings",
            description=(
                f"""
                Thanks for adding HotWired in this server,
                **HotWired** is a multi purpose discord bot that has Moderation commands, Fun commands,
                Music commands and many more!.
                The bot is still in dev so you can expect more commands and features. To get a list of commands ,
                Use **{PREFIX}help**
                """
            ),
            color=0x2F3136,
        )

        embed.add_field(
            name="General information",
            value=textwrap.dedent(
                f"""
                    **► __Bot Id__**: {self.bot.user.id}
                    **► __Developer__**: **{constants.creator}**
                    **► __Prefix__**: {PREFIX}
                """
            ),
        )
        embed.add_field(
            name="**Links**",
            value=textwrap.dedent(
                f"""
                    **►** [Support Server]({constants.discord_server})
                    **►** [Invite link]({constants.invite_link})
                """
            ),
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        try:
            await guild.system_channel.send(embed=embed)
        except Exception:
            pass

        await logchannel.send(
            f"The bot has been added to **{guild.name}** , " f"We've reached our **{len(self.bot.guilds)}th** server! :champagne_glass: "
        )

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        logchannel = self.bot.get_channel(constants.log_channel)

        await logchannel.send(f"The bot has been removed from **{guild.name}** . It sucks! :sob: :sneezing_face: ")


def setup(bot: Bot) -> None:
    bot.add_cog(Events(bot))
