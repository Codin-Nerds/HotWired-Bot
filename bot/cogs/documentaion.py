from discord.ext import commands
import discord
from aiohttp import ClientSession
import typing
import zlib
import re
import os
import io

def to_pages_by_lines(content: str, max_size: int):
    pages = ['']
    i = 0
    for line in content.splitlines(keepends=True):
        if len(pages[i] + line) > max_size:
            i += 1
            pages.append('')
        pages[i] += line
    return pages

def finder(text, collection, *, key=None, lazy=True):
    """Credits to github.com/Rapptz"""
    suggestions = []
    text = str(text)
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else item
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup):
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]


class SphinxObjectFileReader:
    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode('utf-8')

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(16 * 1024)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1:]
                pos = buf.find(b'\n')


def parse_object_inv(stream, url):
    result = {}
    inv_version = stream.readline().rstrip()  # version info

    if inv_version != '# Sphinx inventory version 2':
        raise RuntimeError('Invalid objects.inv file version.')
    projname = stream.readline().rstrip()[11:]  # Project name; "# Project: <name>"
    version = stream.readline().rstrip()[11:]  # Version name; "# Version: <version>"

    line = stream.readline()  # says if it's a zlib header
    if 'zlib' not in line:
        raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

    # This code mostly comes from the Sphinx repository.
    entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
    for line in stream.read_compressed_lines():
        match = entry_regex.match(line.rstrip())
        if not match:
            continue

        name, directive, prio, location, dispname = match.groups()
        domain, _, subdirective = directive.partition(':')
        if directive == 'py:module' and name in result:
            # From the Sphinx Repository:
            # due to a bug in 1.1 and below,
            # two inventory entries are created
            # for Python modules, and the first
            # one is correct
            continue

        if directive == 'std:doc':  # Most documentation pages have a label
            subdirective = 'label'

        if location.endswith('$'):
            location = location[:-1] + name

        key = name if dispname == '-' else dispname
        prefix = f'{subdirective}:' if domain == 'std' else ''

        if projname == 'discord.py':
            key = key.replace('discord.ext.commands.', '').replace('discord.', '')

        result[f'{prefix}{key}'] = os.path.join(url, location)

    return result

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._docs_cache = None
        self.session = ClientSession(loop=self.bot.loop)
    
    async def build_docs_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            async with self.session.get(page + '/objects.inv') as resp:
                if resp.status != 200:
                    raise RuntimeError('Cannot build docs lookup table, try again later.')

                stream = SphinxObjectFileReader(await resp.read())
                cache[key] = parse_object_inv(stream, page)

        self._docs_cache = cache

    async def get_docs(self, ctx, key, obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'python': 'https://docs.python.org/3'
        }

        if obj is None:
            await ctx.send(page_types[key])
            return

        if self._docs_cache is None:
            await self.build_docs_lookup_table(page_types)

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            q = obj.lower()  # point the abc.Messageable types properly:
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._docs_cache[key].items())

        matches = finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        if len(matches) == 0:
            return await ctx.send('Could not find anything. Sorry Babe')

        e = discord.Embed(colour=discord.Colour.blue())

        author = {
            "latest": "discord.py",
            "python": "python"
        }.get(key)

        e.set_author(name=f"{author} docs result", url=page_types.get(key, 'unknown'))
        e.description = '\n'.join(f'[`{key}`]({url})' for key, url in matches)
        await ctx.send(embed=e)

    @commands.group(name='docs', aliases=['d','doc'],invoke_without_command=True)
    async def docs(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity.
        Events, objects, and functions are all supported through a
        a cruddy fuzzy algorithm.
        Props to github.com/Rapptz
        """
        if ctx.invoked_subcommand is None:
            await self.get_docs(ctx, 'latest', obj)

    @docs.command(name='python', aliases=['py'])
    async def python_docs(self, ctx, *, obj: str = None):
        """Gives you a documentation link for a Python entity.
        Props to github.com/Rapptz"""
        await self.get_docs(ctx, 'python', obj)



def setup(bot):
    bot.add_cog(Commands(bot))