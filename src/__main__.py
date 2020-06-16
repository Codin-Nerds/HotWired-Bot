import asyncio
import os
import textwrap

import discord
from discord.ext import commands
from discord.ext.commands import Bot

from utils import config
envs = config.envs

TOKEN = envs("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX
SUPPORT_SERVER = "https://discord.gg/CgH6Sj6"
INVITE = "https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=980675863&scope=bot"

client = commands.Bot(command_prefix=PREFIX, case_insensitivity=True, owner_id=688275913535914014)


@client.event
async def on_ready() -> None:
    print("Bot is Ready.")
    print(f"Logged in as: {client.user.name} : {client.user.id}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for stranded peeps"))


@client.event
async def on_guild_join(guild: discord.Guild) -> None:

    hw = client.get_user(715545167649570977)
    logchannel = client.get_channel(704197974577643550)

    embed = discord.Embed(
        title="Greetings",
        description=textwrap.dedent(
            f"""
            Thanks for adding HotWired in this server,
            **HotWired** is a multi purpose discord bot that has Moderation commands, Fun commands, Music commands and many more!.
            The bot is still in dev so you can expect more commands and features.To get a list of commands , please use **{PREFIX}help**
            """
        ),
        color=0x2F3136,
    )

    embed.add_field(
        name="General information",
        value=textwrap.dedent(
            f"""
            **► __Bot Id__**: 715545167649570977
            **► __Developer__**: **TheOriginalDude#0585**
            **► __Prefix__**: {PREFIX}
            """
        ),
    )
    embed.add_field(
        name="**Links**",
        value=textwrap.dedent(
            f"""
            **►** [Support Server]({SUPPORT_SERVER})
            **►** [Invite link]({INVITE})
            """
        ),
    )

    embed.set_thumbnail(url=hw.avatar_url)

    await guild.system_channel.send(embed=embed)

    await logchannel.send(
        f"The bot has been added to **{guild.name}** , "
        f"We've reached our **{len(client.guilds)}th** server! <:PogChamp:528969510519046184> :champagne_glass: "
    )


def setup_bot(bot: Bot) -> None:
    bot.load_extension("cogs.codesandbox")
    bot.load_extension("cogs.coding")
    bot.load_extension("cogs.commands")
    bot.load_extension("cogs.custom")
    bot.load_extension("cogs.events")
    bot.load_extension("cogs.fun")
    bot.load_extension("cogs.games")
    bot.load_extension("cogs.infog")
    bot.load_extension("cogs.moderation")
    bot.load_extension("cogs.sudo")
    bot.load_extension("cogs.support")
    bot.load_extension("cogs.tools")
    bot.load_extension("cogs.converters")

    bot.run(TOKEN)



if __name__ == "__main__":
    setup_bot(client)
