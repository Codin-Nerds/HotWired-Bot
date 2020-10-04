import textwrap
import traceback
from datetime import datetime

from discord import Color, Embed, Guild, Message
from discord.ext.commands import Cog, Context

from discord.ext import commands
import discord

from bot import config
from bot.core.bot import Bot

PREFIX = config.COMMAND_PREFIX


class ArgumentError(commands.CommandError):
    pass


class ImageError(commands.CommandError):
    pass


class VoiceError(commands.CommandError):
    pass


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

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx: Context, error) -> None:

    #     error = getattr(error, 'original', error)

    #     if isinstance(error, commands.CommandNotFound):
    #         return

    #     elif isinstance(error, commands.CommandOnCooldown):

    #         cooldowns = {
    #             commands.BucketType.default: 'for the whole bot.',
    #             commands.BucketType.user: 'for you.',
    #             commands.BucketType.guild: 'for this server.',
    #             commands.BucketType.channel: 'for this channel.',
    #             commands.BucketType.member: 'cooldown for you.',
    #             commands.BucketType.category: 'for this channel category.',
    #             commands.BucketType.role: 'for your role.'
    #         }
    #         await ctx.send(
    #             f'The command `{ctx.command}` is on cooldown {cooldowns[error.cooldown.type]} You can retry in '
    #             f'`{self.bot.utils.format_time(error.retry_after, friendly=True)}`'
    #         )
    #         return

    #     elif isinstance(error, commands.MaxConcurrencyReached):
    #         cooldowns = {
    #             commands.BucketType.default: '.',
    #             commands.BucketType.user: ' per user.',
    #             commands.BucketType.guild: ' per server.',
    #             commands.BucketType.channel: ' per channel.',
    #             commands.BucketType.member: ' per member.',
    #             commands.BucketType.category: ' per channel category.',
    #             commands.BucketType.role: ' per role.'
    #         }
    #         await ctx.send(
    #             f'The command `{ctx.command}` is already being ran at its maximum of {error.number} time(s){cooldowns[error.per]} Retry a bit later.'
    #         )
    #         return

    #     elif isinstance(error, commands.BotMissingPermissions):
    #         permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
    #         message = Embed(
    #             title="Error!",
    #             description=f'I am missing the following permissions required to run the command `{ctx.command}`.\n{permissions}',
    #             color=Color.red()
    #         )

    #         try:
    #             await ctx.send(embed=message)
    #         except discord.Forbidden:
    #             try:
    #                 await ctx.author.send(embed=message)
    #             except discord.Forbidden:
    #                 pass
    #         return

    #     elif isinstance(error, commands.MissingPermissions):
    #         permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
    #         message = Embed(
    #             title="Error!",
    #             description=f'You are missing the following permissions required to run the command `{ctx.command}`.\n{permissions}',
    #             color=Color.red()
    #         )
    #         await ctx.send(embed=message)
    #         return

    #     elif isinstance(error, commands.MissingRequiredArgument):
    #         message = Embed(
    #             title="Error!",
    #             description=f'You missed the `{error.param.name}` parameter for the command `{ctx.command}`. '
    #                         f'Use `{ctx.prefix}help {ctx.command}` for more information on what parameters to use.',
    #             color=Color.red()
    #         )
    #         await ctx.send(embed=message)

    #         return

    #     error_messages = {
    #         ArgumentError: f'{error}',
    #         ImageError: f'{error}',
    #         VoiceError: f'{error}',
    #         commands.CheckFailure: f'{error}',
    #         commands.TooManyArguments: f'You used too many parameters for the command `{ctx.command}`. Use `{ctx.prefix}help '
    #                                    f'{ctx.command}` for '
    #                                    f'more information on what parameters to use.',
    #         commands.BadArgument: f'I was unable to understand a parameter that you used for the command `{ctx.command}`. '
    #                               f'Use `{ctx.prefix}help {ctx.command}` for more information on what parameters to use.',
    #         commands.BadUnionArgument: f'I was unable to understand a parameter that you used for the command `{ctx.command}`. '
    #                                    f'Use `{ctx.prefix}help {ctx.command}` for more information on what parameters to use.',
    #         commands.NoPrivateMessage: f'The command `{ctx.command}` can not be used in private messages.',
    #         commands.NotOwner: f'The command `{ctx.command}` is owner only.',
    #         commands.NSFWChannelRequired: f'The command `{ctx.command}` can only be ran in a NSFW channel.',
    #         commands.DisabledCommand: f'The command `{ctx.command}` has been disabled.',
    #         commands.ExpectedClosingQuoteError: f'You missed a closing quote in the parameters passed to the `{ctx.command}` command.',
    #         commands.UnexpectedQuoteError: f'There was an unexpected quote in the parameters passed to the `{ctx.command}` command.'
    #     }

    #     error_message = error_messages.get(type(error), None)
    #     if error_message is not None:
    #         await ctx.send(
    #             embed=Embed(
    #                 title="Error!",
    #                 description=error_message,
    #                 color=Color.red()
    #             )
    #         )
    #         return

    #     message = Embed(
    #         title="Error!",
    #         description=f'Something went wrong while executing that command. Please use `{ctx.prefix}support` for more help or information.',
    #         color=Color.red()
    #     )
    #     await ctx.send(embed=message)

    #     time = datetime.strftime(datetime.now())
    #     guild = f'`Guild:` {ctx.guild} `{ctx.guild.id}`\n' if ctx.guild else ''
    #     info = f'''
    #     Error in command `{ctx.command}`\n\n{guild}
    #     `Channel:` {ctx.channel} `{ctx.channel.id}`
    #     \n`Author:` {ctx.author}' `{ctx.author.id}`
    #     \n`Time:` {time}
    #     '''

    #     embed = discord.Embed(color=discord.Color.blurple(), description=f'{ctx.message.content}')
    #     embed.add_field(name='Info:', value=info)

    #     errorchannel = self.bot.get_channel(config.error_channel)

    #     await errorchannel.send(
    #         embed=embed,
    #         username=f'{ctx.author}',
    #         avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png'))
    #     )

    #     traceback = "".join(type(error), error, error.__traceback__).strip()

    #     if len(traceback) > 2000:
    #         async with self.bot.session.post('https://mystb.in/documents', data=traceback) as response:
    #             response = await response.json()
    #         traceback = f'https://mystb.in/{response["key"]}.python'
    #     else:
    #         traceback = f'```\n{traceback}\n```'

    #     await errorchannel.send(
    #         content=f'{traceback}',
    #         username=f'{ctx.author}',
    #         avatar_url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() else 'png'))
    #     )


def setup(bot: Bot) -> None:
    """Load the Events cog."""
    bot.add_cog(Events(bot))
