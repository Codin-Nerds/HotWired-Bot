import asyncio
import os
import textwrap
from itertools import cycle

import discord
from discord.ext import commands
from discord.ext.commands import Bot

from cogs.utils import constants

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = constants.COMMAND_PREFIX

SUPPORT_SERVER = "https://discord.gg/CgH6Sj6"
INVITE = "https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=980675863&scope=bot"

client = commands.Bot(commands.when_mentioned_or(PREFIX), case_insensitivity=True, owner_id=688275913535914014)

status = [
    "😁Working At The Codin' Hole! Join me at https://discord.gg/aYF76yY",
    "▶Check out My Creator's Youtube channel : https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ/",
    f"Ping me using {PREFIX}help",
    "Official Instagram of My Creator ❌ https://instagram.com/the.codin.hole/",
    "Ready To Work and Get Worked! My Github 🔆 https://github.com/janaSunrise",
]


async def change_status() -> None:
    await client.wait_until_ready()
    msgs = cycle(status)

    while not client.is_closed():
        current_status = next(msgs)
        await client.change_presence(activity=discord.Game(name=current_status))
        await asyncio.sleep(10800)


@client.event
async def on_ready() -> None:
    print("Bot is Ready.")
    print(f"Logged in as: {client.user.name} : {client.user.id}")


@client.command()
async def shutoff(ctx):
    if ctx.author.id in constants.devs:
        await ctx.message.add_reaction("☑️")
        await client.logout()


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
            **► __Developer__**: **{constants.creator}**
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
    # bot.load_extension("cogs.coding")
    bot.load_extension("cogs.commands")
    bot.load_extension("cogs.custom")
    bot.load_extension("cogs.events")
    bot.load_extension("cogs.fun")
    bot.load_extension("cogs.games")
    bot.load_extension("cogs.infog")
    bot.load_extension("cogs.moderation")
    bot.load_extension("cogs.support")
    bot.load_extension("cogs.tools")
    bot.load_extension("cogs.converters")

    bot.run(TOKEN)


client.loop.create_task(change_status())

if __name__ == "__main__":
    setup_bot(client)
