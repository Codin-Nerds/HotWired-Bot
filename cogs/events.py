import discord
from discord.ext import commands
import traceback

import setup

class Custom(commands.Cog):
  
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.id == self.client.user.id:
        return

    if message.content.lower().startswith("help"):
        await message.channel.send(f"Hey! Why don't you run the help command with `{setup.COMMAND_PREFIX}help`")

    await self.client.process_commands(message)

  @commands.Cog.listener()
  async def on_error(self, event, *args, **kwargs):
    error_message = f"```py\n{traceback.format_exc()}\n```"
    if len(error_message) > 2000:
        async with self.session.post('https://www.hastebin.com/documents', data=error_message) as resp:
            error_message = 'https://www.hastebin.com/' + (await resp.json())['key']

    em = discord.Embed(
        color=discord.Color.red(),
        description=error_message,
        title=event
    )

    if not self.dev_mode:
        await self.error_hook.send(embed=em)
    else:
        traceback.print_exc()

def setup(client):
  client.add_cog(Custom(client))
