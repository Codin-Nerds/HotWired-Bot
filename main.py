import asyncio
import os
from itertools import cycle

import discord
from discord.ext import commands
from discord.ext.commands import Bot

from cogs.utils import constants

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = constants.COMMAND_PREFIX

client = commands.Bot(commands.when_mentioned_or(PREFIX), case_insensitivity=True, owner_id=688275913535914014)

status = [
    "😁Working At The Codin' Hole! Join me at https://discord.gg/aYF76yY",
    "▶Check out My Creator's Youtube channel : https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ/",
    f"Ping me using {PREFIX}help",
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


# @client.event
# async def on_command_error(ctx, error):
#   if isinstance(error, commands.MissingRequiredArgument):
#     embed = error_embed(f"Please pass in All Required Arguments. for more help on that command,use__ **{PREFIX}help {ctx.command.name}**", "❌ERROR")
#     await ctx.send(embed=embed)

#   if isinstance(error, commands.CommandNotFound):
#     pass

#   if isinstance(error, commands.MissingPermissions):
#     embed = error_embed("You don't have Enough permissions to Execute this command!", "❌ERROR")
#     await ctx.send(embed=embed)

#   if isinstance(error, commands.BotMissingPermissions):
#    embed = error_embed(
#         "The Bot does not have Enough permissions to Execute this command! Please Give the required permissions", "❌ERROR"
#    )
#    await ctx.send(embed=embed)


def setup_bot(bot: Bot) -> None:
    bot.load_extension("cogs.codesandbox")
    # bot.load_extension("cogs.coding")
    bot.load_extension("cogs.commands")
    bot.load_extension("cogs.converters")
    bot.load_extension("cogs.common")
    bot.load_extension("cogs.emotes")
    bot.load_extension("cogs.events")
    bot.load_extension("cogs.fun")
    bot.load_extension("cogs.games")
    bot.load_extension("cogs.github")
    bot.load_extension("cogs.infog")
    bot.load_extension("cogs.malware_protection")
    bot.load_extension("cogs.moderation")
    bot.load_extension("cogs.search")
    bot.load_extension("cogs.study")
    bot.load_extension("cogs.sudo")
    bot.load_extension("cogs.support")
    bot.load_extension("cogs.tools")
    bot.load_extension("cogs.embeds")
    bot.load_extension("cogs.translate")

    bot.run(TOKEN)


client.loop.create_task(change_status())

if __name__ == "__main__":
    setup_bot(client)
