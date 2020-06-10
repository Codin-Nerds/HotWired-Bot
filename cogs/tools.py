import hashlib
import base64

import discord
from discord.ext import commands


class Tools(commands.Cog):

	def __init__(self, client):
		self.bot = client
		self.hash_algos = sorted([h for h in hashlib.algorithms_available if h.islower()])

	@commands.command()
	async def ascii(self, ctx, *, text: str):
		"""Convert a String to ascii."""

		emb = discord.Embed(
			title="Unicode convert",
			description=' '.join([str(ord(letter)) for letter in text])
		)
		emb.set_footer(text=f'Invoked by {str(ctx.message.author)}')

		await ctx.send(embed=emb)

	@commands.command()
	async def unascii(self, ctx, *, text: str):
		"""Convert ascii to String."""
		try:
			codes = [chr(int(i)) for i in text.split(' ')]
			emb = discord.Embed(
				title="Unicode convert",
				description=''.join(codes)
			)
			emb.set_footer(text=f'Invoked by {str(ctx.message.author)}')

			await ctx.send(embed=emb)

		except ValueError:
			embed = discord.Embed(
				title="Error!",
				description=f"Invalid sequence. Example usage : `{self.bot.config['PREFIX']}unascii 104 101 121`",
				color=discord.Color.red()
			)

			await ctx.send(embed=embed)

	@commands.command()
	async def byteconvert(self, ctx, value: int, unit='Mio'):
		"""Convert into Bytes."""
		units = ('o', 'Kio', 'Mio', 'Gio', 'Tio', 'Pio', 'Eio', 'Zio', 'Yio')
		unit = unit.capitalize()

		if not unit in units and unit != 'O':
			embed = discord.Embed(
				title="Unit not Found!",
				description=f"Available units are `{'`, `'.join(units)}`.",
				color=discord.Color.red()
			)
			return await ctx.send(embed=embed)

		emb = discord.Embed(title="Binary conversions")
		index = units.index(unit)

		for i, u in enumerate(units):
			result = round(value / 2 ** ((i - index) * 10), 14)
			emb.add_field(name=u, value=result)

		await ctx.send(embed=emb)

	@commands.command(name='hash')
	async def _hash(self, ctx, algorithm, *, text: str):
		"""Hash a String"""
		algo = algorithm.lower()

		if not algo in self.hash_algos:
			matches = '\n'.join([supported for supported in self.algos if algo in supported][:10])
			message = f"`{algorithm}` not available."
			if matches:
				message += f" Did you mean:\n{matches}"

			embed = discord.Embed(
				title="Algorithm Error",
				description=message,
				color=discord.Color.red()
			)
			return await ctx.send(embed=embed)

		try:
			hash_object = getattr(hashlib, algo)(text.encode('utf-8'))

		except AttributeError:
			hash_object = hashlib.new(algo, text.encode('utf-8'))

		emb = discord.Embed(title=f"{algorithm} hash", description=hash_object.hexdigest())
		emb.set_footer(text=f'Invoked by {str(ctx.message.author)}')

		await ctx.send(embed=emb)

	@commands.command()
	async def encode(self, ctx, *, text: str):
		"""Convert a String to binary"""
		message_bytes = text.encode('ascii')
		base64_bytes = base64.b64encode(message_bytes)
		base64_message = base64_bytes.decode('ascii')

		emb = discord.Embed(title="Base64 Encode", description=base64_message)
		emb.set_footer(text=f'Invoked by {str(ctx.message.author)}')

		await ctx.send(embed=emb)

	@commands.command()
	async def decode(self, ctx, *, text: str):
		"""Convert a binary to String"""
		base64_bytes = text.encode('ascii')
		message_bytes = base64.b64decode(base64_bytes)
		message = message_bytes.decode('ascii')

		emb = discord.Embed(title="Base64 Decode", description=message)
		emb.set_footer(text=f'Invoked by {str(ctx.message.author)}')

		await ctx.send(embed=emb)


def setup(bot):
	bot.add_cog(Tools(bot))
