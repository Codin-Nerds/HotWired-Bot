import asyncio
import discord
from discord.ext.commands import Paginator as CommandPaginator
from discord.ext.commands import Context
import typing as t


FIRST_EMOJI = "\u23EE"  # [:track_previous:]
LEFT_EMOJI = "\u2B05"  # [:arrow_left:]
RIGHT_EMOJI = "\u27A1"  # [:arrow_right:]
LAST_EMOJI = "\u23ED"  # [:track_next:]
PAGE_NUM_EMOJI = "\N{INPUT SYMBOL FOR NUMBERS}"
STOP_EMOJI = "\N{BLACK SQUARE FOR STOP}"
INFO_EMOJI = "\N{INFORMATION SOURCE}"


class CannotPaginate(Exception):
    pass


class Pages:
    """Implements a paginator that queries the user for the pagination interface."""

    def __init__(self, ctx: Context, entries: t.List[str], per_page: int = 12, show_entry_count: bool = True) -> None:
        self.bot = ctx.bot
        self.entries = entries
        self.message = ctx.message
        self.channel = ctx.channel
        self.author = ctx.author
        self.per_page = per_page
        pages, left_over = divmod(len(self.entries), self.per_page)
        if left_over:
            pages += 1
        self.maximum_pages = pages
        self.embed = discord.Embed(colour=discord.Colour.blurple())
        self.paginating = len(entries) > per_page
        self.show_entry_count = show_entry_count
        self.reaction_emojis = [
            (FIRST_EMOJI, self.first_page),
            (LEFT_EMOJI, self.previous_page),
            (RIGHT_EMOJI, self.next_page),
            (LAST_EMOJI, self.last_page),
            (PAGE_NUM_EMOJI, self.numbered_page),
            (STOP_EMOJI, self.stop_pages),
            (INFO_EMOJI, self.show_help),
        ]

        if ctx.guild is not None:
            self.permissions = self.channel.permissions_for(ctx.guild.me)
        else:
            self.permissions = self.channel.permissions_for(ctx.bot.user)

        if not self.permissions.send_messages:
            raise CannotPaginate("Bot cannot send messages.")

        if not self.permissions.embed_links:
            raise CannotPaginate("Bot does not have embed links permission.")

        if self.paginating:
            # verify we can actually use the pagination session
            if not self.permissions.add_reactions:
                raise CannotPaginate("Bot does not have add reactions permission.")

            if not self.permissions.read_message_history:
                raise CannotPaginate("Bot does not have Read Message History permission.")

    def get_page(self, page: int) -> t.List[str]:
        base = (page - 1) * self.per_page
        stop = base + self.per_page
        return self.entries[base:stop]

    def get_content(self, entries: t.List[str], page: int, *, first: bool = False) -> None:
        return None

    def get_embed(self, entries: t.List[str], page: int, *, first: bool = False) -> discord.Embed:
        self.prepare_embed(entries, page, first=first)
        return self.embed

    def prepare_embed(self, entries: t.List[str], page: int, *, first: bool = False) -> None:
        p = []
        for index, entry in enumerate(entries, 1 + ((page - 1) * self.per_page)):
            p.append(f"{index}. {entry}")

        if self.maximum_pages > 1:
            if self.show_entry_count:
                text = f"Page {page}/{self.maximum_pages} ({len(self.entries)} entries)"
            else:
                text = f"Page {page}/{self.maximum_pages}"

            self.embed.set_footer(text=text)

        if self.paginating and first:
            p.append("")
            p.append("Confused? React with \N{INFORMATION SOURCE} for more info.")

        self.embed.description = "\n".join(p)

    async def show_page(self, page: int, *, first: bool = False) -> None:
        self.current_page = page
        entries = self.get_page(page)
        content = self.get_content(entries, page, first=first)
        embed = self.get_embed(entries, page, first=first)

        if not self.paginating:
            await self.channel.send(content=content, embed=embed)
            return

        if not first:
            await self.message.edit(content=content, embed=embed)
            return

        self.message = await self.channel.send(content=content, embed=embed)
        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ("\u23ed", "\u23ee"):
                continue

            await self.message.add_reaction(reaction)

    async def checked_show_page(self, page: int) -> None:
        if page != 0 and page <= self.maximum_pages:
            await self.show_page(page)

    async def first_page(self) -> None:
        """goes to the first page"""
        await self.show_page(1)

    async def last_page(self) -> None:
        """goes to the last page"""
        await self.show_page(self.maximum_pages)

    async def next_page(self) -> None:
        """goes to the next page"""
        await self.checked_show_page(self.current_page + 1)

    async def previous_page(self) -> None:
        """goes to the previous page"""
        await self.checked_show_page(self.current_page - 1)

    async def show_current_page(self) -> None:
        if self.paginating:
            await self.show_page(self.current_page)

    async def numbered_page(self) -> None:
        """lets you type a page number to go to"""
        to_delete = []
        to_delete.append(await self.channel.send("What page do you want to go to?"))

        def message_check(msg) -> bool:
            return msg.author == self.author and self.channel == msg.channel and msg.content.isdigit()

        try:
            msg = await self.bot.wait_for("message", check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await self.channel.send("Took too long."))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            if page != 0 and page <= self.maximum_pages:
                await self.show_page(page)
            else:
                to_delete.append(await self.channel.send(f"Invalid page given. ({page}/{self.maximum_pages})"))
                await asyncio.sleep(5)
        try:
            await self.channel.delete_messages(to_delete)
        except Exception:
            pass

    async def show_help(self) -> None:
        """shows this message"""
        messages = ["Welcome to the interactive paginator!\n"]
        messages.append("This interactively allows you to see pages of text by navigating with " "reactions. They are as follows:\n")
        for (emoji, func) in self.reaction_emojis:
            messages.append(f"{emoji} {func.__doc__}")
        embed = self.embed.copy()
        embed.clear_fields()
        embed.description = "\n".join(messages)
        embed.set_footer(text=f"We were on page {self.current_page} before this message.")
        await self.message.edit(content=None, embed=embed)

        async def go_back_to_current_page() -> None:
            await asyncio.sleep(60.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def stop_pages(self) -> None:
        """stops the interactive pagination session"""
        await self.message.delete()
        self.paginating = False

    def react_check(self, payload: discord.RawReactionActionEvent) -> bool:
        if payload.user_id != self.author.id:
            return False
        if payload.message_id != self.message.id:
            return False
        to_check = str(payload.emoji)
        for (emoji, func) in self.reaction_emojis:
            if to_check == emoji:
                self.match = func
                return True
        return False

    async def paginate(self) -> None:
        """Actually paginate the entries and run the interactive loop if necessary."""
        first_page = self.show_page(1, first=True)
        if not self.paginating:
            await first_page
        else:
            # allow us to react to reactions right away if we're paginating
            self.bot.loop.create_task(first_page)
        while self.paginating:
            try:
                payload = await self.bot.wait_for("raw_reaction_add", check=self.react_check, timeout=120.0)
            except asyncio.TimeoutError:
                self.paginating = False
                try:
                    await self.message.clear_reactions()
                except Exception:
                    pass
                finally:
                    break
            try:
                await self.message.remove_reaction(payload.emoji, discord.Object(id=payload.user_id))
            except Exception:
                pass  # can't remove it so don't bother doing so
            await self.match()


class FieldPages(Pages):
    """Similar to Pages except entries should be a list of
    tuples having (key, value) to show as embed fields instead.
    """

    def prepare_embed(self, entries: t.List[str], page: int, *, first=False) -> None:
        self.embed.clear_fields()
        self.embed.description = discord.Embed.Empty

        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=False)

        if self.maximum_pages > 1:
            if self.show_entry_count:
                text = f"Page {page}/{self.maximum_pages} ({len(self.entries)} entries)"
            else:
                text = f"Page {page}/{self.maximum_pages}"

            self.embed.set_footer(text=text)


class TextPages(Pages):
    """Uses a commands.Paginator internally to paginate some text."""

    def __init__(self, ctx, text, *, prefix="```", suffix="```", max_size=2000) -> None:
        paginator = CommandPaginator(prefix=prefix, suffix=suffix, max_size=max_size - 200)
        for line in text.split("\n"):
            paginator.add_line(line)

        super().__init__(ctx, entries=paginator.pages, per_page=1, show_entry_count=False)

    def get_page(self, page: int) -> t.List[str]:
        return self.entries[page - 1]

    def get_embed(self, entries: t.List[str], page: int, *, first=False) -> None:
        return None

    def get_content(self, entry: t.List[str], page: int, *, first: bool = False) -> t.Union[str, t.List[str]]:
        if self.maximum_pages > 1:
            return f"{entry}\nPage {page}/{self.maximum_pages}"
        return entry
