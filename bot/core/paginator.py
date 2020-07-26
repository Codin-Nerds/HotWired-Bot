import asyncio
import logging
import typing as t
from textwrap import dedent

import discord
from discord import Embed
from discord.abc import Messageable
from discord.ext import commands
from discord.ext.commands import Context, Paginator

logger = logging.getLogger(__name__)


class PaginatorError(Exception):
    """
    Exception Class for Custom error PaginatorError.
    Raised if the bot is unable to create/process a paginator.
    """
    pass


def check_permissions(channel: Messageable, bot: commands.Bot) -> bool:
    """
    Checks if the bot has required permissions to send or process
    the paginator

    Args:
        channel (Messageable): The Context
        bot (commands.Bot): The bot object, used for using bot.user if there is no guild

    Returns:
        bool: Whether the bot has all of the required permissions
    """
    perms: discord.Permissions = channel.permissions_for(
        channel.guild.me if channel.guild is not None else bot.user
    )

    necessary_permissions = [
        perms.send_messages,
        perms.embed_links,
        perms.add_reactions,
        perms.read_message_history
    ]

    return all(necessary_permissions)


class _BasePaginator:
    """
    An embed can be added to the embeds list
    if the paginator class is inheriting from
    this class
    """
    def __init__(self, embeds: t.List[Embed]) -> None:
        self.embeds = embeds

    def __add__(self, other: Embed) -> None:
        self.embeds.append(other)


class FieldPaginator(_BasePaginator):
    """
    A class which creates a list of embeds and configures their
    fields according to the parameters.

    Parameters
    ----------
        *args : t.Union[str, Embed]
            Brief Explanation: The arguments can be a list,
            representing a page or it can be an embed.

            Example:
            Key-Value is required. Inline is optional since its
            set to True as a default value.
            To insert an embed (creating a new page),
            create a new value on the list as shown below.

            FieldPaginator([{'Page': '1', 'inline': True}, discord.Embed(title="Page 2")])
    """
    def __init__(self, *args) -> None:
        self.embeds = []
        super().__init__(self.embeds)

        for index, arg in enumerate(args):
            if isinstance(arg, Embed):
                self.embeds.append(arg)
            elif isinstance(arg, list):
                _embed = discord.Embed()
                for element in arg:
                    if isinstance(element, dict):
                        # If element is an empty dictionary
                        if element == {}:
                            raise PaginatorError(
                                "FieldPaginator argument is a nested dictionary but does not have the mandatory "
                                "key-value pair".strip()
                            )
                        elif len(element.items()) > 2:
                            raise PaginatorError(
                                "FieldPaginator argument is supposed to be a dictionary of "
                                "2 key-value pair (key: value, inline: bool), but found " + len(element.items())
                            )

                        _embed.add_field(
                            name=list(element.keys())[0],
                            value=list(element.values())[0],
                            inline=True if 'inline' not in element.keys() else bool(element['inline'])
                        )
                    else:
                        raise PaginatorError(
                            "\n"
                            "Field paginator nested embed is not accepted\n"
                            "Eg: FieldPaginator([{'Name': 'John', 'inline': False}, ->Embed().set_footer('Name', 'Sarah')<-])\n"
                            "Accepted type to create an embed for FieldPaginator (note that this will create a new page):\n"
                            "FieldPaginator([{'Name': 'John', 'inline': False}], Embed().set_footer('Name', 'Sarah'))"
                        )
                self.embeds.append(_embed)
            else:
                raise PaginatorError(
                    "FieldPaginator argument given "
                    f"at index {index} is invalid.\n"
                    "The supported types are:\n"
                    "Embed and list"
                )


class ListPaginator(_BasePaginator):
    """
    A class which creates a list of embeds and configures
    their descriptions according to the parameters.

    Parameters
    ----------
        entries : List[str]
            List of entries to add to the paginator
            Length of every entry must be lower than
            the max_size argument.
        individual_paging : bool
            Whether to make a new paginator page for every
            entry.
        prefix : str
            A string that is added to the beginning to every
            paginator page.
        suffix : str
            A string that is added to the end of every paginator
            page.
        max_size : int
            Maximum amount of characters allowed per entry.
    """
    def __init__(
        self,
        entries: t.Optional[t.List[str]] = None,
        individual_paging=True,
        prefix='',
        suffix='',
        max_size=2000
    ) -> None:

        entries = entries if entries is not None else []

        for entry in entries:
            if isinstance(entry, Embed) and not individual_paging:
                raise PaginatorError(
                    "List paginator entry cannot be an embed if parameter individual_paging is False."
                )

        if not individual_paging:
            paginator = Paginator(prefix, suffix, max_size)

            for entry in entries:
                paginator.add_line(entry)

            self.embeds = [Embed(description=description) for description in paginator.pages]
        else:
            self.embeds = []
            for index, entry in enumerate(entries):
                if isinstance(entry, str):
                    self.embeds.append(Embed(description=entry))
                elif isinstance(entry, Embed):
                    self.embeds.append(entry)
                else:
                    raise PaginatorError(
                        "ImagePaginator argument given "
                        f"at index {index} is invalid."
                        "The supported types are: "
                        "Embed and str"
                    )

        super().__init__(self.embeds)


class ImagePaginator(_BasePaginator):
    """
    A class which creates a list of embeds and configures their
    image urls according to the parameters.

    Parameters
    ----------
        *args : t.Union[str, Embed]

            Brief Explanation: The *args can be a string, representing
            an image url or it can be an Embed, representing a raw embed.
    """
    def __init__(self, *args) -> None:
        self.embeds = []
        super().__init__(self.embeds)

        for index, arg in enumerate(args):
            if isinstance(arg, str):
                _embed = Embed()
                _embed.set_image(url=arg)
                self.embeds.append(_embed)
            elif isinstance(arg, Embed):
                self.embeds.append(arg)
            else:
                raise PaginatorError(
                    "ImagePaginator argument given "
                    f"at index {index} is invalid."
                    "The supported types are: "
                    "Embed and str"
                )


class EmbedPaginator(_BasePaginator):
    """
    A class which creates a list of embeds and configures their
    embeds according to the parameters.

    This can be directly passed to process_paginator for further
    processing.

    Parameters
    ----------
        *args : Embed
            Embeds to append to self.embeds
    """
    def __init__(self, *args) -> None:
        self.embeds = [arg for arg in args]
        super().__init__(self.embeds)


async def process_paginator(
    paginator: t.Union[ImagePaginator, ListPaginator, EmbedPaginator, FieldPaginator],
    context: t.Union[Context, discord.Message],
    bot: commands.Bot,
    show_page_length: bool = True,
    timeout: t.Union[int, float] = 300.0,
    **kwargs: t.Optional[t.Union[str, discord.Emoji]],
) -> None:
    """
    The main function that is responsible for doing all of the following:
    - Send the first paginator page as a message.
    - Add reactions to it.
    - Reply to the reactions by the user in the form of changing the page.
    - Keep on waiting for another reaction until the timeout is reached.

    Parameters
    ----------
        paginator : t.Union[ImagePaginator, ListPaginator, EmbedPaginator, FieldPaginator]
            The paginator itself.
            This can be an image, list, embed or a field paginator.
            Note that it MUST be one of those.
            If you want to process a normal paginator from discord.py,
            use this:

            paginator = ListPaginator(entries=['Hello World!'], individual_paging=False)
            await process_paginator(paginator, ...)

        context: t.Union[commands.Context, discord.Message]
            The context, used for sending a message to the channel, getting the author etc.

        bot: commands.Bot
            Used to run 'bot.wait_for' and other things
        show_page_length: bool
            Whether to show the page ('Page 1/4') in the footer
        timeout: float
            For how long to respond to a new reaction.
            If this time limit is reached, all of the reactions clear
            and the function exits, breaking the loop.
        **kwargs: t.Optional[t.Union[discord.Emoji, str]]
            Used to override reaction emojis.
            For example, process_paginator(..., first_page_emoji=😂'<:emoji:192391292319>')
            This will replace the emoji that indicates the first page (by default
            set to ⏮) with the emoji that we gave to that kwarg.
    """
    if not check_permissions(context.channel, bot):
        raise PaginatorError("Bot lacks a permission to paginate")

    supported_types = (ImagePaginator, ListPaginator, EmbedPaginator, FieldPaginator)

    if isinstance(context, Context):
        send = context.send
    elif isinstance(context, discord.Message):
        send = context.channel.send
    else:
        raise PaginatorError(
            "The context argument given to process_paginator "
            "must be a commands.Context or a discord.Message object."
        )

    if not type(paginator) in supported_types:
        raise PaginatorError(dedent(
            "The paginator must be an instance of one of these:\n"
            f"{', '.join([type_.__name__ for type_ in supported_types])}\n"
            "If you want to process commands.Paginator, try out "
            "ListPaginator like so:\n"
            "Paginator = ListPaginator(['Hello World'])"
        ))

    page = 0

    embed = paginator.embeds[page]

    # Reaction emojis. Can be overridden by kwargs.
    reaction_emojis = {
        "first_page_emoji": "⏮️",  # First page
        "prev_page_emoji": "⬅️",  # Previous Page
        "next_page_emoji": "➡️",  # Next Page
        "last_page_emoji": "⏭️",  # Last Page
        "exit_emoji": "<:trashcan:722035312238526505>",  # Stop paginator and delete message (trashcan)
    }

    for key in reaction_emojis.keys():
        if key in [_ for _ in kwargs]:
            reaction_emojis[key] = kwargs[key]

    def update_footer(embed_: discord.Embed, page_: int) -> None:
        if show_page_length:
            footer = f"Page {page_ + 1}/{len(paginator.embeds)}"
            embed_.set_footer(text=footer)

    async def update(page_: int) -> None:
        embed_ = paginator.embeds[page_]
        update_footer(embed_, page_)
        await message.edit(embed=embed_)

    update_footer(embed, page)

    # Sending the initial message
    message: discord.Message = await send(embed=embed)

    if not len(paginator.embeds) == 1:
        for value in reaction_emojis.values():
            await message.add_reaction(value)
    else:
        await message.add_reaction(reaction_emojis['exit_emoji'])

    # Reaction checker
    def check(
        reaction_: discord.Reaction, user_: t.Union[discord.Member, discord.User]
    ) -> bool:
        return all(
            (
                reaction_.message.id == message.id,
                str(reaction_.emoji) in reaction_emojis.values(),
                user_.bot is False,
                user_.id == context.author.id,
            )
        )

    # Looping over to see if the user responds with a reaction before the timeout.
    # Will break if the timeout is reached.
    while True:
        try:
            reaction, user = await bot.wait_for(
                event="reaction_add", timeout=timeout, check=check
            )
        except asyncio.TimeoutError:
            # Time's up!
            # Clearing all the reactions on the initial messages and breaking out
            await message.clear_reactions()
            break

        if str(reaction.emoji) == reaction_emojis["exit_emoji"]:
            # Delete the message and exit if the reaction is trashcan
            return await message.delete()

        if not len(paginator.embeds) == 1:
            if reaction.emoji == reaction_emojis["first_page_emoji"]:
                # Changes the page to the first page of the paginator and updates the initial message
                await message.remove_reaction(reaction.emoji, user)

                # Don't edit the message if the current page is the first page
                if page == 0:
                    continue

                page = 0

                await update(page)

            if reaction.emoji == reaction_emojis["last_page_emoji"]:
                # Changes the page to the last page of the paginator and updates the initial message
                await message.remove_reaction(reaction.emoji, user)

                # Don't edit the message if the current page is the first page
                if page == len(paginator.embeds) - 1:
                    continue

                page = len(paginator.embeds) - 1

                await update(page)

            if reaction.emoji == reaction_emojis["prev_page_emoji"]:
                # Goes back a page and updates the initial message

                await message.remove_reaction(reaction.emoji, user)
                if page == 0:
                    continue
                page -= 1

                await update(page)

            if reaction.emoji == reaction_emojis["next_page_emoji"]:
                # Goes forward a page and updates the initial message

                await message.remove_reaction(reaction.emoji, user)
                if page == len(paginator.embeds) - 1:
                    continue
                page += 1

                await update(page)
