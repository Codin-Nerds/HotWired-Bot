import discord
from discord.ext import commands, tasks

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client


       
    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog Moderation is working.')
    
    @commands.command()
    @commands.check_any(commands.is_owner())
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        await member.kick(reason = reason)
        await ctx.send(f'Kicked {member.mention}')

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        await member.ban(reason = reason)
        await ctx.send(f'Banned {member.mention}')

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return


def setup(client):
    client.add_cog(Moderation(client))

