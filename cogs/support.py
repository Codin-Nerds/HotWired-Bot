import discord
from discord.ext import commands

from .utils import constants


class Support(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def invite(self, ctx):
		"""
        Invite link for Bot
        """
		embed = discord.Embed(
			title="Inviting me to your Server?",
			description=f"❯❯ [Invite Link]({constants.invite_link})"
						f"\n❯❯ [Secondary Invite Link]({constants.admin_invite_link})",
			color=discord.Color.dark_green()
		)

		embed.set_thumbnail(url=self.client.user.avatar_url)

		await ctx.send(embed=embed)

	@commands.command(name='support')
	async def support(self, ctx):
		"""
        Get an invite link to the bots support server.
        """
		embed = discord.Embed(
			title="Need Support? OR Want to give Feedback?",
			description="If you have any **problems with the bot** or "
						"if you have any **suggestions/feedback** be sure to join the Support Server!"
						f"❯❯ [Support Server]({constants.discord_server})"
						f"❯❯ [Invite Link]({constants.invite_link})",
			color=discord.Color.dark_green()
		)

		embed.set_thumbnail(url=self.client.user.avatar_url)

		await ctx.send(embed=embed)


def setup(client):
	client.add_cog(Support(client))
