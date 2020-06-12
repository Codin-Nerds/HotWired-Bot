import traceback

import discord
from discord.ext import commands

import re
import aiohttp


class Custom(commands.Cog):

    def __init__(self, client):
        self.client = client

    @staticmethod
    def get_link_code(string: str):
        return string.split("/")[-1]

    @staticmethod
    async def check_our_invite(full_link, guild):
        guild_invites = await guild.invites()
        for invite in guild_invites:
            # discord.gg/code resolves to https://discordapp.com/invite/code after using session.get(invite)
            if Custom.get_link_code(invite.url) == Custom.get_link_code(full_link):
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = message.channel
        if message.author.id == self.client.user.id:
            return

        elif not isinstance(message.author, discord.Member):
            return

        elif message.author.guild_permissions.administrator:
            return

        if "https:" in message.content or "http:" in message.content:
            base_url = re.findall(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                message.content
            )

            for invite in base_url:
                try:
                    async with self.session.get(invite) as response:
                        invite = str(response.url)
                except aiohttp.ClientConnectorError:
                    continue

                if "discordapp.com/invite/" in invite or "discord.gg/" in invite:
                    if not await Custom.check_our_invite(invite, message.guild):
                        await ctx.send(f"{message.author.mention} You are not allowed to post other Server's invites!")
                        await message.delete()


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
