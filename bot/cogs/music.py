from discord import Color, Embed, FFmpegPCMAudio, User
from discord.ext.commands import Context, Bot, Cog, command
from discord.utils import get

from youtube_dl import YoutubeDL
from asyncio import run_coroutine_threadsafe
import requests


# TODO: add a status command, that shows the music status

class Music(Cog):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.song_queue = {}
        self.message = {}

    @staticmethod
    def parse_duration(duration: int) -> str:
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)
        return f'{h:d}:{m:02d}:{s:02d}'

    @staticmethod
    def search(author: User, name: str) -> None:
        with YoutubeDL(Music.YDL_OPTIONS) as ydl:
            try:
                requests.get(name)
            except Exception:
                info = ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0]
            else:
                info = ydl.extract_info(name, download=False)

        embed = Embed(title='Let\'s listen to Music 🎵', description=f"[{info['title']}]({info['webpage_url']})", color=Color.blurple())
        embed.add_field(name='Duration', value=Music.parse_duration(info['duration']))
        embed.add_field(name='Requested by: ', value=author)
        embed.add_field(name='Uploader', value=f"[{info['uploader']}]({info['channel_url']})")
        embed.add_field(name="Queue", value="No song queued")
        embed.set_thumbnail(url=info['thumbnail'])

        return {'embed': embed, 'source': info['formats'][0]['url'], 'title': info['title']}

    async def edit_message(self, ctx: Context) -> None:
        embed = self.song_queue[ctx.guild][0]['embed']
        content = "\n".join([f"({self.song_queue[ctx.guild].index(i)}) {i['title']}"
                             for i in self.song_queue[ctx.guild][1:]]) if len(self.song_queue[ctx.guild]) > 1 else "No song queued"

        embed.set_field_at(index=3, name="Queue :", value=content, inline=False)
        # TODO: add delete and resend
        await self.message[ctx.guild].edit(embed=embed)

    def next_song(self, ctx: Context) -> None:
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if len(self.song_queue[ctx.guild]) > 1:
            del self.song_queue[ctx.guild][0]
            run_coroutine_threadsafe(self.edit_message(ctx), self.bot.loop)
            voice.play(FFmpegPCMAudio(self.song_queue[ctx.guild][0]['source'], **Music.FFMPEG_OPTIONS), after=lambda e: self.next_song(ctx))
            voice.is_playing()
        else:
            run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)
            run_coroutine_threadsafe(self.message[ctx.guild].delete(), self.bot.loop)

    # TODO: play random song using spotify's recommendation api if no name is given
    @command(aliases=['p'])
    async def play(self, ctx: Context, *, video: str) -> None:
        """Play a music by searching it."""
        channel = ctx.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        song = Music.search(ctx.author.mention, video)
        await ctx.channel.purge(limit=1)

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        if not voice.is_playing():
            self.song_queue[ctx.guild] = [song]
            self.message[ctx.guild] = await ctx.send(embed=song['embed'])
            voice.play(FFmpegPCMAudio(song['source'], **Music.FFMPEG_OPTIONS), after=lambda e: self.next_song(ctx))
            voice.is_playing()
        else:
            self.song_queue[ctx.guild].append(song)
            await self.edit_message(ctx)

    @command()
    async def pause(self, ctx: Context) -> None:
        """Pause a running song playlist."""
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await ctx.channel.purge(limit=1)
            if voice.is_playing():
                await ctx.send('⏸️ Music paused', delete_after=5.0)
                voice.pause()
            else:
                await ctx.send('⏯️ Music resumed', delete_after=5.0)
                voice.resume()

    @command()
    async def skip(self, ctx: Context) -> None:
        """Skip a song in the playlist."""
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            await ctx.channel.purge(limit=1)
            await ctx.send('⏭️ Music skipped', delete_after=5.0)
            voice.stop()

    @command()
    async def remove(self, ctx: Context, *, num: int) -> None:
        """Remove a song from the playlist using number."""
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            del self.song_queue[ctx.guild][num]
            await ctx.channel.purge(limit=1)
            await self.edit_message(ctx)

    @command()
    async def stop(self, ctx: Context) -> None:
        """Stop a Song playlist."""
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)
        run_coroutine_threadsafe(self.message[ctx.guild].delete(), self.bot.loop)
        await ctx.send(":stop_button: Music Stopped!", delete_after=5.0)

    @command()
    async def music_status(self, ctx: Context) -> None:
        pass


def setup(bot: Bot) -> None:
    bot.add_cog(Music(bot))
