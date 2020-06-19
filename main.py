import os
import textwrap
from itertools import cycle

import discord
from discord.ext import commands, tasks

from cogs.utils import constants

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = constants.COMMAND_PREFIX

SUPPORT_SERVER = "https://discord.gg/CgH6Sj6"
INVITE = "https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=980675863&scope=bot"

extensions = ["cogs.codesandbox", "cogs.commands", "cogs.converters", "cogs.custom", "cogs.emotes",
    "cogs.events", "cogs.fun", "cogs.games", "cogs.infog", "cogs.moderation", "cogs.study", "cogs.sudo",
    "cogs.support", "cogs.tools"]
# "cogs.coding"


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = cycle([
            "😁Working At The Codin' Hole! Join me at https://discord.gg/aYF76yY",
            "▶Check out My Creator's Youtube channel : https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ/",
            f"Ping me using {PREFIX}help",
            "Official Instagram of My Creator ❌ https://instagram.com/the.codin.hole/",
            "Ready To Work and Get Worked! My Github 🔆 https://github.com/janaSunrise",
        ])
        self.first_on_ready = True

    async def on_ready(self) -> None:
        if self.first_on_ready:
            self.change_status.start()
            self.fist_on_ready = False
            self.hw = self.get_user(715545167649570977)
            self.log_channel = self.get_channel(704197974577643550)
            await self.log_channel.send(f"Bot is ready.\nLogged in as {self.use.name} : {self.user.id}")
            for ext in extensions:
                self.load_extension(ext)
        else:
            await self.log_channel.send("I'm ready (again)")

    @tasks.loop(hours=3)
    async def change_status(self) -> None:
        await self.change_presence(activity=discord.Game(name=next(self.status)))

    async def on_guild_join(self, guild: discord.Guild) -> None:
        embed = discord.Embed(title="Greetings",
            description=textwrap.dedent(
                f"""
                Thanks for adding HotWired in this server,
                **HotWired** is a multi purpose discord bot that has Moderation commands, Fun commands, Music commands and many more!.
                The bot is still in dev so you can expect more commands and features.To get a list of commands , please use **{PREFIX}help**
                """), color=0x2F3136)

        embed.add_field(name="General information",
            value=textwrap.dedent(
                f"""
                **► __Bot Id__**: 715545167649570977
                **► __Developer__**: **{constants.creator}**
                **► __Prefix__**: {PREFIX}
                """))
        embed.add_field(name="**Links**",
            value=textwrap.dedent(
                f"""
                **►** [Support Server]({SUPPORT_SERVER})
                **►** [Invite link]({INVITE})
                """))

        embed.set_thumbnail(url=self.hw.avatar_url)

        await guild.system_channel.send(embed=embed)

        await self.logchannel.send(f"The bot has been added to **{guild.name}** ,"
            "We've reached our **{len(self.guilds)}th** server! <:PogChamp:528969510519046184> :champagne_glass: ")

bot = Bot(commands.when_mentioned_or(PREFIX), case_insensitive=True, owner_id=688275913535914014)


if __name__ == "__main__":
    bot.run(TOKEN)
