import os

from discord import Game
from discord.ext.commands import when_mentioned_or

from bot import config
from bot.core.bot import Bot

TOKEN = os.getenv("BOT_TOKEN")

extensions = [
    "bot.cogs.codesandbox",
    "bot.cogs.commands",
    "bot.cogs.conversion",
    "bot.cogs.common",
    "bot.cogs.emotes",
    "bot.cogs.events",
    "bot.cogs.fun",
    "bot.cogs.games",
    "bot.cogs.moderation",
    "bot.cogs.study",
    "bot.cogs.sudo",
    "bot.cogs.support",
    "bot.cogs.tools",
    "bot.cogs.search",
    "bot.cogs.security",
    "bot.cogs.embeds",
    "bot.cogs.comics",
    "bot.cogs.coding",
    "bot.cogs.documentation",
    "bot.cogs.reddit",
    "bot.cogs.translate",
    "bot.cogs.github",
    "bot.cogs.nasa",
    "bot.cogs.nsfw",
]

bot = Bot(
    extensions,
    command_prefix=when_mentioned_or(config.COMMAND_PREFIX),
    activity=Game(name=f"Ping me using {config.COMMAND_PREFIX}help"),
    case_insensitive=True,
)

bot.remove_command('help')


@bot.command(help="Shows this message.")
async def help(ctx, cmd=None):
    cmds = bot.all_commands

    def format_cmd_help(cmd):
        def format_params(params):
            return params

        return "    {} {}\n        {}\n\n".format(
            ", ".join([cmd.name] + cmd.aliases),
            format_params(cmd.params),
            cmd.help
        )

    if not cmd:
        cogs = {}

        for cmd_name in cmds:
            cmd_obj = cmds[cmd_name]
            cog_name = cmd_obj.cog_name if cmd_obj.cog_name is not None else 'Others'

            try:
                cogs[cog_name].append(cmd_obj)

            except KeyError:
                cogs[cog_name] = []
                cogs[cog_name].append(cmd_obj)

            except AttributeError:
                cogs[cog_name] = []
                cogs[cog_name].append(cmd_obj)

        bot_help = []

        for cog in cogs:
            cog_help = "\n{}:\n".format(cog)
            for cmd in cogs[cog]:
                cog_help += format_cmd_help(cmd)

            bot_help += [cog_help]

        bot_help.reverse()

        await ctx.send(f"```{''.join(bot_help)}```")
    else:
        await ctx.send("```\n{}\n```".format(format_cmd_help(cmd)))

if __name__ == "__main__":
    bot.run(TOKEN)
