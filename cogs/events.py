import traceback
import textwrap
from .utils import constants

from discord import Color, Embed, Guild, Message
from discord.ext.commands import Bot, Cog

PREFIX = constants.COMMAND_PREFIX


class Custom(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.dev_mode = constants.DEV_MODE

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        # Check that the message is not from bot account
        if message.author.bot:
            return

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

        hw = self.client.user
        logchannel = self.client.get_channel(constants.log_channel)

        embed = Embed(
            title="Greetings",
            description=(
                f"""
                Thanks for adding HotWired in this server,
                **HotWired** is a multi purpose discord bot that has Moderation commands, Fun commands,
                Music commands and many more!.
                The bot is still in dev so you can expect more commands and features.To get a list of commands ,
                """
            ),
            color=0x2F3136,
        )

        embed.add_field(
            name="General information",
            value=textwrap.dedent(
                f"""
                **► __Bot Id__**: {self.client.user.id}
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

        embed.set_thumbnail(url=hw.avatar_url)

        try:
            await guild.system_channel.send(embed=embed)
        except Exception:
            pass

        await logchannel.send(
            f"The bot has been added to **{guild.name}** , " f"We've reached our **{len(self.client.guilds)}th** server! :champagne_glass: "
        )

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        logchannel = self.client.get_channel(constants.log_channel)

        await logchannel.send(f"The bot has been removed from **{guild.name}** . It sucks! :sob: :sneezing_face: ")


def setup(bot: Bot) -> None:
    bot.add_cog(Custom(bot))
