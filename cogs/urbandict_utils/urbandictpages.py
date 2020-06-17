import discord
import re
from discord.ext.commands import Context
from cogs.utils.paginator import Pages
import typing as t


class UrbanDictionaryPages(Pages):
    BRACKETED = re.compile(r"(\[(.+?)\])")

    def __init__(self, ctx: Context, data: t.List[str]) -> None:
        super().__init__(ctx, entries=data, per_page=1)

    def get_page(self, page: int) -> str:
        return self.entries[page - 1]

    def cleanup_definition(self, definition: str, *, regex: str = BRACKETED) -> str:
        def repl(m) -> str:
            word = m.group(2)
            return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'

        ret = regex.sub(repl, definition)
        if len(ret) >= 2048:
            return ret[0:2000] + " [...]"
        return ret

    def prepare_embed(self, entry: dict, page: int, *, first: bool = False) -> None:
        if self.maximum_pages > 1:
            title = f'{entry["word"]}: {page} out of {self.maximum_pages}'
        else:
            title = entry["word"]

        self.embed = e = discord.Embed(colour=0xE86222, title=title, url=entry["permalink"])
        e.set_footer(text=f'Author : {entry["author"]}')
        e.description = self.cleanup_definition(entry["definition"])

        try:
            date = discord.utils.parse_time(entry["written_on"][0:-1])
        except (ValueError, KeyError):
            pass
        else:
            e.timestamp = date
