import asyncio
import textwrap
from itertools import cycle

import discord
import setup
from cogs.utils import constants
# from cogs.utils.embedHandler import error_embed
from discord.ext import commands

TOKEN = setup.BOT_TOKEN
PREFIX = constants.COMMAND_PREFIX
SUPPORT_SERVER = "https://discord.gg/CgH6Sj6"
INVITE = "https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=980675863&scope=bot"

client = commands.Bot(commands.when_mentioned_or(PREFIX), owner_id=688275913535914014)

status = [
    "😁Working At The Codin\' Hole! Join me at https://discord.gg/aYF76yY",
    "▶Check out My Creator\'s Youtube channel : https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ/",
    f"Ping me using {PREFIX}help",
    "Official Instagram of My Creator ❌ https://instagram.com/the.codin.hole/",
    "Ready To Work and Get Worked! My Github 🔆 https://github.com/janaSunrise",
]


async def change_status():
    await client.wait_until_ready()
    msgs = cycle(status)

    while not client.is_closed():
        current_status = next(msgs)
        await client.change_presence(activity=discord.Game(name=current_status))
        await asyncio.sleep(10800)


@client.event
async def on_ready():
    print('Bot is Ready.')
    print(f"Logged in as: {client.user.name} : {client.user.id}")


@client.event
async def on_message(message):
    pass


@client.event
async def on_guild_join(guild: discord.Guild):

    hw = client.get_user(715545167649570977)
    logchannel = client.get_channel(704197974577643550)

    embed = discord.Embed(
        title="Greetings",
        description=textwrap.dedent(f"""
            Thanks for adding HotWired in this server,
            **HotWired** is a multi purpose discord bot that has Moderation commands, Fun commands, Music commands and many more!.
            The bot is still in dev so you can expect more commands and features.To get a list of commands , please use **{PREFIX}help**
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
                              **►** [Support Server]({SUPPORT_SERVER})
                              **►** [Invite link]({INVITE})
        """)
    )

    embed.set_thumbnail(url=hw.avatar_url)

    await guild.system_channel.send(embed=embed)

    await logchannel.send(
        f"The bot has been added to **{guild.name}** , "
        f"We've reached our **{len(client.guilds)}th** server! <:PogChamp:528969510519046184> :champagne_glass: "
    )

# @client.event
# async def on_command_error(ctx, error):
#   if isinstance(error, commands.MissingRequiredArgument):
#     embed = error_embed(f"Please pass in All Required Arguments. for more help on that command,use__ **{PREFIX}help {ctx.command.name}**", "❌ERROR")
#     await ctx.send(embed=embed)

#   if isinstance(error, commands.CommandNotFound):
#     embed = error_embed("Command Not Found!", "❌ERROR")
#     await ctx.send(embed=embed)

#   if isinstance(error, commands.MissingPermissions):
#     embed = error_embed("You don't have Enough permissions to Execute this command!", "❌ERROR")
#     await ctx.send(embed=embed)

#   if isinstance(error, commands.BotMissingPermissions):
#    embed = error_embed(
#         "The Bot does not have Enough permissions to Execute this command! Please Give the required permissions", "❌ERROR"
#    )
#    await ctx.send(embed=embed)


def SetupBot(bot):
    bot.load_extension("cogs.codesandbox")
    bot.load_extension("cogs.coding")
    bot.load_extension("cogs.commands")
    bot.load_extension("cogs.custom")
    bot.load_extension("cogs.events")
    bot.load_extension("cogs.fun")
    bot.load_extension("cogs.games")
    bot.load_extension("cogs.hacking")
    bot.load_extension("cogs.moderation")
    bot.load_extension("cogs.study")
    bot.load_extension("cogs.sudo")
    bot.load_extension("cogs.support")
    bot.load_extension("cogs.tools")

    bot.run(TOKEN)


client.loop.create_task(change_status())

if __name__ == "__main__":
    SetupBot(client)
