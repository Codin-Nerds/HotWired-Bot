import discord
import os
from discord.ext import commands, tasks
import random
from itertools import cycle

client = commands.Bot(command_prefix = '21/')
status = cycle(['Waiting for 21/help', 'Hi', '9+10=21', '''hi
hi''', "21"])




@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready')


# Background Tasks

@tasks.loop(seconds = 10)
async def change_status():
    await client.change_presence(status = discord.Status.online, activity = discord.Game(next(status)))


# Events

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid command used.')


# Extension related stuff
@client.command()
@commands.check_any(commands.is_owner())
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
@commands.check_any(commands.is_owner())
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command()
@commands.check_any(commands.is_owner())
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a cog to load.')

@unload.error
async def unload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a cog to unload.')

@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a cog to reload.')



for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# Run
client.run('NzA3NDEyOTY3NzA4NDI2MjUx.XsdW2g.QWoMQlKhV0pJ7mbmy8o8yWT-7tY')
