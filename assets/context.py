import asyncio
from collections import namedtuple

import discord
from discord.ext import commands

from cogs.utils import misc, check
from cogs.utils.embeds import ConfirmEmbed, ConfirmEmbedAnother

argument = namedtuple("Usage", ["required", "text"])
example = namedtuple("Examples", ["args", "text"])
sub_desc = namedtuple("subcommands", "desc")
others = namedtuple("others", ["name", "text"])
usage_info = namedtuple("usage_information", ["command", "value"])
keyword = namedtuple("keywords", ["keyword", "desc"])


class InvokeError(commands.CommandError):
    def __init__(self, message):
        self.message = message


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.InvokeError = InvokeError

    async def confirm(self, title, content, color=misc.random_color()):
        instance = ConfirmEmbed(self, content, color=color, title=title)
        confirmation = await instance.start()
        return confirmation

    async def confirm_another(self, user, title, content, color=misc.random_color()):
        instance = ConfirmEmbedAnother(ctx=self, user=user, content=content,
                                       color=color, title=title, dm=True)
        confirmation = await instance.start()
        return confirmation

    async def get_response(self, question, check_func=None, delete=True):
        def validate_response(message):
            if message.author == self.author and message.channel == self.channel and \
               True if check_func is None else check_func(message.content):
                return True
            else:
                return False

        question_msg = await self.send(content=question)
        try:
            msg = await self.bot.wait_for("message", check=validate_response, timeout=30)
        except asyncio.TimeoutError:
            return None

        if delete is True:
            return msg, question_msg
        else:
            return msg

    def error(self, message):
        raise InvokeError(message)

    async def group_delete(self, *args):
        try:
            for msg in args:
                await msg.delete()
        except discord.Forbidden:
            if self.guild:
                raise commands.BotMissingPermissions("Delete messages!")
        except (discord.NotFound, discord.HTTPException):
            pass

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        if self.guild:
            if not await check.bot_has_ch_perm(self.guild.me, self.channel, send_messages=True):
                return
            elif embed and not await check.bot_has_ch_perm(self.guild.me, self.channel, embed_links=True):
                return await self.send("I don't have permissions to send embeds!")

        return await super().send(content, tts=tts, embed=embed, file=file,
                                  files=files, delete_after=delete_after,
                                  nonce=nonce)


class Command(commands.Command):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        self._usage = None
        self.help_ = kwargs.get("help_")

        possible_help_kwargs = ["description", "syntax", "keywords", "others", "usage_information", "examples"]
        self.help_kwargs = {name: value for name, value in kwargs.items() if name in possible_help_kwargs}

    async def create_help(self, prefix):
        fields = {}
        for name, value in self.help_kwargs.items():
            name = name.replace("_", " ")
            if name == "syntax":
                base = f"{prefix}{self.qualified_name}"
                if isinstance(value, list):
                    translator = {False: "Optional: ", True: "Required: "}
                    fields[name.title()] = f'{base} {" ".join([f"[{translator[required]}{desc}]" for required, desc in value])}'
                else:
                    fields[name.title()] = base
            elif name == "keywords":
                kw_field_data = []
                for kw, desc in value:
                    if isinstance(desc, list):
                        kw_field_data.append("**{}**: {}".format(kw, '\n'.join(desc)))
                        print(kw_field_data)
                    else:
                        kw_field_data.append(f"**{kw}**: {desc}")
                fields[name.title()] = '\n'.join(kw_field_data).strip("\n")
            elif name == "others":
                fields[value.name] = value.text
            elif name == "usage information":
                product = []
                for command, data in value:
                    if command == "GET PREFIX REPLACE":
                        data = data.replace("[prefix]", prefix)
                    product.append(data)
                fields[name.title()] = "".join(product)
            elif name == "examples":
                examples_list = []
                base = f"`{prefix}{self.qualified_name}"
                for arg, explain in value:
                    # If there is enough characters to be wrapped to a new line...
                    if len(base + arg + explain) > 73:
                        examples_list.append(f" • {base}{' ' if arg else ''}{arg}`\n{explain}\n")
                    else:
                        examples_list.append(f" • {base}{' ' if arg else ''}{arg}` {explain}\n")
                fields[name.title()] = "".join(examples_list)
            else:
                fields[name.title()] = value
        return fields


class Group(commands.Group):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        self._usage = None
        self.help_ = kwargs.get("help_")

        possible_help_kwargs = ["description", "syntax", "subcommands", "keywords", "others", "usage_information", "examples"]
        self.help_kwargs = {name: value for name, value in kwargs.items() if name in possible_help_kwargs}

    async def create_help(self, prefix):
        fields = {}
        for name, value in self.help_kwargs.items():
            name = name.replace("_", " ")
            if name == "syntax":
                base = f"{prefix}{self.qualified_name}"
                if isinstance(value, list):
                    translator = {False: "Optional: ", True: "Required: "}
                    fields[name.title()] = f'{base} {" ".join([f"[{translator[required]}{desc}]" for required, desc in value])}'
                else:
                    fields[name.title()] = base
            elif name == "keywords":
                kw_field_data = []
                for kw, desc in value:
                    if isinstance(desc, list):
                        kw_field_data.append("**{}**: {}".format(kw, '\n'.join(desc)))
                    else:
                        kw_field_data.append(f"**{kw}**: {desc}")
                fields[name.title()] = '\n'.join(kw_field_data).strip("\n")
            elif name == "subcommands":
                fields[name.title()] = '\n'.join([f"**{cmd.name}**: {desc}" for cmd, desc in zip(self.commands, value[0])])
            elif name == "others":
                fields[value.name] = value.text
            elif name == "usage information":
                product = []
                for command, data in value:
                    if command == "GET PREFIX REPLACE":
                        data = data.replace("[prefix]", prefix)
                    product.append(data)
                fields[name.title()] = "".join(product)
            elif name == "examples":
                examples_list = []
                base = f"`{prefix}{self.qualified_name}"
                for arg, explain in value:
                    # If there is enough characters to be wrapped to a new line...
                    if len(base + arg + explain) > 73:
                        examples_list.append(f" • {base}{' ' if arg else ''}{arg}`\n{explain}\n")
                    else:
                        examples_list.append(f" • {base}{' ' if arg else ''}{arg}` {explain}\n")
                fields[name.title()] = "".join(examples_list)
            else:
                fields[name.title()] = value
        return fields
