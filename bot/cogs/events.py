import textwrap
import traceback

from discord import Color, Embed, Guild, Message
from discord.ext.commands import Cog

from bot import config
from bot.core.bot import Bot

PREFIX = config.COMMAND_PREFIX


class Events(Cog):
    """Some events, packed in a cog."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.dev_mode = config.DEV_MODE

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Prevent people from posting other servers' invites."""
        # Check that the message is not from bot account
        if message.author.bot:
            return

        # DM Check.
        if not message.guild:
            return

        # Is an Admin.
        if message.author.guild_permissions.administrator:
            return

        # if self.bot.mention in message:
        #     prefix = self.bot.prefix_dict.get(
        #         self.bot.get_id(message),
        #         self.bot.default_prefix
        #     )

        #     await message.channel.send(f"Hey {message.author.mention}! My prefix here is `{prefix}`")

        # await self.bot.process_commands(message)

    @Cog.listener()
    async def on_error(self, event: str, *args, **kwargs) -> None:
        """Error manager."""
        logchannel = self.bot.get_channel(config.log_channel)
        error_message = f"```py\n{traceback.format_exc()}\n```"
        if len(error_message) > 2000:
            async with self.bot.session.post("https://www.hasteb.in/documents", data=error_message) as resp:
                error_message = "https://www.hasteb.in/" + (await resp.json())["key"]

        embed = Embed(color=Color.red(), description=error_message, title=event)

        if not self.dev_mode:
            # self.error_hook is undefined
            await self.error_hook.send(embed=embed)
        else:
            traceback.print_exc()
            await logchannel.send(embed=embed)

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        """Send message upon joining a guild, and log it."""
        logchannel = self.bot.get_channel(config.log_channel)

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
                    **► __Developer__**: **{config.creator}**
                    **► __Prefix__**: {PREFIX}
                """
            ),
        )
        embed.add_field(
            name="**Links**",
            value=textwrap.dedent(
                f"""
                    **►** [Support Server]({config.discord_server})
                    **►** [Invite link]({config.invite_link})
                """
            ),
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        try:
            await guild.system_channel.send(embed=embed)
        except Exception:
            pass

        log_embed = Embed(
            title=f"The bot has been added to {guild.name}",
            description=textwrap.dedent(
                f"""
                **We've reached our {len(self.bot.guilds)}th server!** :champagne_glass:
                Guild Id: **{guild.id}** | Guild Owner: {guild.owner.mention}
                Member Count: **{guild.member_count}**
                """
            ),
            color=Color.green(),
        )
        embed.set_thumbnail(url=str(guild.icon_url))

        await logchannel.send(embed=log_embed)

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        logchannel = self.bot.get_channel(config.log_channel)

        await logchannel.send(f"The bot has been removed from **{guild.name}** . It sucks! :sob: :sneezing_face: ")


def setup(bot: Bot) -> None:
    """Load the Events cog."""
    bot.add_cog(Events(bot))
