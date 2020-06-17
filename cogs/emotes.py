import discord
from discord.ext.commands import Bot, Cog, Context, command
from discord.utils import get

from .utils import constants
import textwrap

from .emote_utils.emotes import Emote
from .emote_utils.exceptions import InvalidCommandException, EmoteNotFoundException


class Emotes(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def send_error(self, ctx: Context, error: str) -> None:
        """Sends the Error of Any functions as an Embed."""
        help_message = f"Type `{constants.COMMAND_PREFIX}help` for further assistance"
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name=f"Error: {error}", value=help_message)
        await ctx.send(embed=embed)

    @command(aliases=["addemote", "emotehow"])
    async def emote_add_help(self, ctx: Context) -> None:
        """Shows help on how to add emotes."""
        add_emote = textwrap.dedent(
            "Adds a twitch emote to the server\n\n"
            "**Usage:**\n"
            f"`{constants.COMMAND_PREFIX}add_emote twitch <emote_id>`\n"
            f"`{constants.COMMAND_PREFIX}add_emote btv <emote_id> <channel_name>`\n"
            f"`{constants.COMMAND_PREFIX}add_emote frf <emote_id>`\n\n"
            "To get an emote visit [twitchemotes.com](https://twitchemotes.com), "
            "[betterttv.com](https://betterttv.com/emotes/shared), or "
            "[frankerfacez.com](https://www.frankerfacez.com/emoticons/) and find "
            "an emote you like!.\n"
            "The channel name for BetterTTV emotes is found in the top right section "
            "of the web page for the emote\n"
            "The the ID of the emote is found at the end of the URL for a specific "
            "emote.\n"
            "twitchemotes.com/emotes/__**120232**__\n"
            "betterttv.com/emotes/__**5771aa498bbc1e572cb7ae4d**__\n"
            "frankerfacez.com/emoticon/__**261802**__-4Town"
        )
        emote = textwrap.dedent(
            "Send an animated emote\n\n"
            "**How To:**\n"
            f"`{constants.COMMAND_PREFIX}emote <emote_name>`\n\n"
            "Supply emote names as a comma-separated list to send multiple emotes in a single message"
        )
        embed = discord.Embed(colour=discord.Colour.dark_gold())
        embed.add_field(name=f"{constants.COMMAND_PREFIX}add_emote", value=add_emote)
        embed.add_field(name=f"{constants.COMMAND_PREFIX}emote", value=emote)
        await ctx.send(embed=embed)

    @command()
    async def add_emote(self, ctx: Context, *, content: str) -> None:
        """Adding Emotes."""
        server = ctx.message.guild

        try:
            emote = Emote.get_emote(content)
        except InvalidCommandException:
            await self.send_error(ctx, "Invalid command")
            return
        except EmoteNotFoundException:
            await self.send_error(ctx, "Emote not found")
            return

        await server.create_custom_emoji(name=emote.name, image=emote.image.read())
        discord_emote = get(server.emojis, name=emote.name)
        emote_string = f"<:{discord_emote.name}:{discord_emote.id}>"
        if discord_emote.animated:
            emote_string = f"<a:{discord_emote.name}:{discord_emote.id}>"
        await ctx.send(emote_string)

    @command()
    async def emote(self, ctx: Context, *, content: str) -> None:
        """Using the Emotes."""
        server = ctx.message.guild
        names = content.split(",")

        emote_string = ""
        for name in names:
            emote = get(server.emojis, name=name)
            if emote is None:
                await self.send_error(ctx, f"Emote {name} not found")
                return
            if emote.animated:
                emote_string += f"<a:{emote.name}:{emote.id}>"
            else:
                emote_string += f"<:{emote.name}:{emote.id}>"

        await ctx.send(emote_string)
        await ctx.message.delete()


def setup(bot: Bot) -> None:
    bot.add_cog(Emotes(bot))
