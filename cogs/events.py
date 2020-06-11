import traceback
import textwrap
from .utils import constants

import discord
from discord.ext import commands

PREFIX = constants.COMMAND_PREFIX


class Custom(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.dev_mode = constants.DEV_MODE

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            return

        if message.author.bot:  # make sure the bot doesn't respond to other bots
            return

        await self.client.process_commands(message)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        hw = self.client.get_user(715545167649570977)
        logchannel = self.client.get_channel(704197974577643550)

        embed = discord.Embed(
            title="Greetings",
            description=textwrap.dedent(f"""
                Thanks for adding HotWired in this server,
                **HotWired** is a multi purpose discord bot that has Moderation commands, Fun commands, Music commands 
                and many more!. 
                The bot is still in dev so you can expect more commands and features.To get a list of commands , 
                please use **{PREFIX}help** 
            """),
            color=0x2f3136
        )

        embed.add_field(
            name="General information",
            value=textwrap.dedent(f"""
                                  **► __Bot Id__**: 715545167649570977
                                  **► __Developer__**: **TheOriginalDude#0585**
                                  **► __Prefix__**: {PREFIX}
            """)
        )
        embed.add_field(
            name="**Links**",
            value=textwrap.dedent(f"""
                                  **►** [Support Server]({constants.SUPPORT_SERVER})
                                  **►** [Invite link]({constants.invite_link})
                                  **►** [Substitute Invite link]({constants.admin_invite_link})
            """)
        )

        embed.set_thumbnail(url=hw.avatar_url)

        try:
            await guild.system_channel.send(embed=embed)
        except:
            pass

        await logchannel.send(
            f"The bot has been added to **{guild.name}** , "
            f"We've reached our **{len(self.client.guilds)}th** server! <:PogChamp:528969510519046184> :champagne_glass: "
        )


    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        logchannel = self.client.get_channel(704197974577643550)

        await logchannel.send(
            f"The bot has been Removed From **{guild.name}** ! It Sucks! :sob: :sneezing_face: "
        )


    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        error_message = f"```\n{traceback.format_exc()}\n```"
        if len(error_message) > 2000:
            async with self.session.post('https://www.hastebin.com/documents', data=error_message) as resp:
                error_message = 'https://www.hastebin.com/' + (await resp.json())['key']

        em = discord.Embed(
            color=discord.Color.red(),
            description=error_message,
            title=event
        )

        if not self.dev_mode:
            # await self.error_hook.send(embed=em)
            await self.client.send_message(embed=em)
        else:
            traceback.print_exc()


def setup(client):
    client.add_cog(Custom(client))
