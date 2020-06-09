import asyncio
import datetime
import os
import platform
import random
import string
import sys
import traceback

import discord
from discord.ext import commands


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        try:
            self.dev_mode = platform.system() != 'Linux' and sys.argv[1] != '-d'
        except IndexError:
            self.dev_mode = True

    @commands.command()
    async def invite(self, ctx):
        """
        Invite link for Bot
        """
        await ctx.send('Invite Me to Your server ! **THE INVITE LINK IS** : https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=980675863&scope=bot')

    @commands.command(name='serverinfo', aliases=['server'])
    async def serverinfo(self, ctx):
        """
        Get information about the server.
        """

        embed = discord.Embed(colour=discord.Color.gold())
        embed.title = f"{ctx.guild.name}'s stats and information."
        embed.description = ctx.guild.description if ctx.guild.description else None
        embed.add_field(name='__**General information:**__',
                        value=f'**Owner:** {ctx.guild.owner}\n'
                              f'**Created at:** {datetime.datetime.strftime(ctx.guild.created_at, "%A %d %B %Y at %H:%M")}\n'
                              f'**Members:** {ctx.guild.member_count} | '
                              f'**Nitro Tier:** {ctx.guild.premium_tier} | '
                              f'**Boosters:** {ctx.guild.premium_subscription_count}\n'
                              f'**File Size:** {round(ctx.guild.filesize_limit / 1048576)} MB | '
                              f'**Bitrate:** {round(ctx.guild.bitrate_limit / 1000)} kbps | '
                              f'**Emoji:** {ctx.guild.emoji_limit}\n')

        embed.add_field(name='__**Channels:**__',
                        value=f'**AFK timeout:** {int(ctx.guild.afk_timeout / 60)}m | '
                              f'**AFK channel:** {ctx.guild.afk_channel}\n'
                              f'**Text channels:** {len(ctx.guild.text_channels)} | '
                              f'**Voice channels:** {len(ctx.guild.voice_channels)}\n', inline=False)

        embed.set_footer(text=f'ID: {ctx.guild.id}')

        return await ctx.send(embed=embed)

    @commands.command(name='userinfo', aliases=['user'])
    async def userinfo(self, ctx, *, member: discord.Member = None):
        """
        Get information about you, or a specified member.
        `member`: The member to get information from. Can be a Mention, Name or ID.
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(colour=discord.Color.gold())
        embed.title = f"{member}'s stats and information."
        embed.add_field(name='__**General information:**__',
                        value=f'**Discord Name:** {member}\n'
                              f'**Created at:** {datetime.datetime.strftime(member.created_at, "%A %d %B %Y at %H:%M")}\n', inline=False)

        embed.add_field(name='__**Server-related information:**__',
                        value=f'**Nickname:** {member.nick}\n'
                              f'**Joined server:** {datetime.datetime.strftime(member.joined_at, "%A %d %B %Y at %H:%M")}\n'
                              f'**Top role:** {member.top_role.mention}', inline=False)

        embed.set_thumbnail(url=member.avatar_url_as(format='png'))
        embed.set_footer(text=f'ID: {member.id}')

        return await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def spam(self, ctx, times=100000, text=None):
        def randomString(stringLength=8):
            letters = string.ascii_lowercase
            return ''.join(random.choice(letters) for i in range(stringLength))
        if text == None:
            num = random.randint(4, 16)
            for i in range(times):
                await ctx.send(randomString(num))
                await asyncio.sleep(1)
        else:
            num = random.randint(4, 16)
            for i in range(times):
                await ctx.send(text)
                await asyncio.sleep(1)

    @commands.command(aliases=['cembed', 'emb', 'new'])
    async def create(self, ctx, *, msg):
        """Create an embed"""
        await ctx.send(msg)

    @commands.command(hidden=True)
    async def load(self, ctx, *, extension):
        """Loads a cog"""
        try:
            self.bot.load_extension(f'cogs.{extension}')
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{SQUARED OK}')

    @commands.command(name='reload', hidden=True)
    async def _reload(self, ctx, *, extension):
        """Reloads a module."""
        try:
            self.bot.unload_extension(f'cogs.{extension}')
            self.bot.load_extension(f'cogs.{extension}')
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{SQUARED OK}')

    @commands.command(hidden=True)
    async def restart(self, ctx):
        """Restart The bot"""
        await self.bot.logout()
        os.system("python main.py")


def setup(client):
    client.add_cog(Commands(client))
