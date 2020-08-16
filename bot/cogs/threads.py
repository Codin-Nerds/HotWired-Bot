import asyncio
import discord
from discord.ext import commands, tasks


class Threads(commands.Cog):
    """Commands for threading, implementing forum-like functionalities."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ensure_data.start()

    def cog_check(self, ctx: commands.Context) -> bool:
        """Make threads usable only in guilds."""
        if not ctx.guild:
            raise commands.NoPrivateMessage()
        return True

    @tasks.loop(hours=2)
    async def ensure_data(self):
        """Remove all database reference to deleted threads."""
        async with self.bot.pool.acquire() as database:
            rows = await database.fetchall(
                "SELECT * FROM public.threads"
            )
            for row in rows:
                try:
                    await self.bot.fetch_channel(row["channel_id"])
                except discord.NotFound:
                    await database.execute(
                        "DELETE FROM public.threads WHERE channel_id=$1",
                        row["channel_id"],
                    )

    @commands.group(invoke_without_command=True)
    async def thread(self, ctx: commands.Context) -> None:
        """Group for threading commands."""
        await ctx.send_help("thread")

    @thread.command(name="delete")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def thread_delete(self, ctx: commands.Context, *, reason: str = None) -> None:
        """Delete the thread after confirmation."""
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.threads WHERE channel_id=$1",
                ctx.channel.id,
            )
        if not row:
            await ctx.send("This channel isn't a thread. Aborting.")
            return
        await ctx.send("Do you really want to delete this thread ? (y/n)")

        def check(message: discord.Message) -> bool:
            return message.content.lower() in (
                "y",
                "yes"
                "n",
                "no",
                "true",
                "false",
                "abort",
                "continue",
            )
        try:
            message = await self.bot.wait_for(
                "message",
                check=check,
                timeout=30,
            )
        except asyncio.TimeoutError:
            await ctx.send("You took too long to answer. Aborting.")
            return
        if message.content.lower() in ("n", "no", "false", "abort"):
            await ctx.send("Aborting.")
            return
        await ctx.channel.delete(reason=reason)
        async with self.bot.pool.acquire() as database:
            await database.execute(
                "DELETE FROM public.threads WHERE channel_id=$1",
                ctx.channel.id,
            )

    @thread.command(name="edit")
    async def thread_edit(self, ctx: commands.Context, part: str, *, content: str = "None") -> None:
        """Edit a part of the thread's original message.

        The part can be `title`, `description` or `image`.
        Pass `None` to delete the part.
        For `image`, you can attach the image you want to set.
        You need to be the thread author or have `manage_messages` permissions.
        """
        perms = ctx.channel.permissions_for(ctx.author)
        async with self.bot.pool.acquire() as database:
            if perms.manage_messages:
                row = await database.fetchrow(
                    "SELECT * FROM public.threads WHERE channel_id=$1",
                    ctx.channel.id,
                )
                if not row:
                    await ctx.send(
                        "Sorry, but this channel isn't a thread."
                    )
                    return
            else:
                row = await database.fetchrow(
                    "SELECT * FROM public.threads WHERE author_id=$1 AND "
                    "channel_id=$2",
                    ctx.author.id,
                    ctx.channel.id,
                )
                if not row:
                    await ctx.send(
                        "Sorry, but this channel isn't a thread you own."
                    )
                    return

        if content.lower() == "none":
            content = discord.Embed.Empty

        if not row["message_id"]:
            await ctx.send(
                "Sorry, but this thread wasn't created with a message associated"
            )
            return

        try:
            message = await ctx.channel.fetch_message(row["message_id"])
        except discord.NotFound:
            await ctx.send(
                "Sorry, but the message associated to this thread was deleted."
            )
            return

        embed = message.embeds[0]

        if part.lower() == "description":
            embed.description = content
        elif part.lower() == "title":
            if len(content) > 256:
                await ctx.send(
                    "The title must be 256 characters or fewer in length."
                )
                return
            embed.title = content
        elif part.lower() == "image":
            if ctx.message.attachments:
                content = ctx.message.attachments[0].url
            embed.set_image(url=content)
        else:
            await ctx.send(
                "The part must be one of `description`, `title`, `image`."
            )
            return
        try:
            await message.edit(embed=embed)
            await ctx.send("Message edited successfully")
        except discord.HTTPException:
            await ctx.send("Wrong URL for the image")

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True, manage_channels=True)
    @thread.command(name="lock")
    async def thread_lock(self, ctx: commands.Context, *, reason: str = None):
        """Deny `send_messages` permissions for each member / role that doesn't have `manage_messages` permissions."""
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.threads WHERE channel_id=$1",
                ctx.channel.id,
            )
        if not row:
            await ctx.send(
                "This channel isn't a thread. Aborting the command."
            )
            return

        if row["locked"]:
            await ctx.send("This thread is already locked. Aborting.")
            return

        await ctx.send("Thread locked")
        if ctx.channel.overwrites:
            overwrites = [
                [
                    role.id,
                    ctx.channel.overwrites[role].pair()[0].value,
                    ctx.channel.overwrites[role].pair()[1].value,
                ] for role in ctx.channel.overwrites
            ]
            async with self.bot.pool.acquire() as database:
                await database.execute(
                    "UPDATE public.threads SET overwrites=$1, "
                    "locked=$2 "
                    "WHERE channel_id=$3",
                    overwrites,
                    True,
                    ctx.channel.id,
                )
            for role in ctx.channel.overwrites:
                if not role.permissions.manage_messages and role != ctx.guild.default_role:
                    await ctx.channel.set_permissions(
                        role,
                        send_messages=False,
                        read_messages=True,
                        reason=reason,
                    )
        else:
            await ctx.channel.set_permissions(
                ctx.guild.default_role,
                send_messages=False,
                reason=reason,
            )

    @thread.command(name="make")
    @commands.bot_has_guild_permissions(manage_channels=True, manage_messages=True)
    @commands.cooldown(2, 3600, commands.BucketType.member)
    async def thread_make(self, ctx: commands.Context) -> None:
        """Create a new thread channel in the `threads` category.

        The category created (if I create one) will have the same permissions as the category the command's run in (if any).
        The channel will have the same permissions as the channel the command's run in.
        """
        category = discord.utils.get(
            ctx.guild.categories,
            name="threads",
        )
        if not category:
            category = await ctx.guild.create_category(
                name="threads",
                reason="Threads setup",
            )

        await ctx.send(
            "How should I name the new channel ? (2-100 characters)"
        )
        try:
            answer = await self.bot.wait_for(
                "message",
                check=lambda message: message.author == ctx.author and (
                    message.channel == ctx.channel
                ) and 2 < len(message.content) <= 100,
                timeout=60,
            )
            channel_name = answer.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to answer. Aborting.")
            return

        if discord.utils.get(category.channels, name=channel_name):
            await ctx.send(
                "There already is a channel with that name. Aborting."
            )
            return

        await ctx.send(
            "Neat. Now what will be the title of the thread ? (Enter `None`"
            "if you don't want a title, or up to 256 characters)"
        )

        try:
            answer = await self.bot.wait_for(
                "message",
                check=lambda message: message.author == ctx.author and (
                    message.channel == ctx.channel
                ) and len(message.content) < 256,
                timeout=60,
            )
            title = answer.content
            if title.lower() == "none":
                title = discord.Embed.Empty
        except asyncio.TimeoutError:
            await ctx.send("You took too long to answer. Aborting.")
            return

        await ctx.send(
            "Okay. Now what about the description ? (Enter `None` if you"
            "don't want a title)"
        )

        try:
            answer = await self.bot.wait_for(
                "message",
                check=lambda message: message.author == ctx.author and (
                    message.channel == ctx.channel
                ),
                timeout=60,
            )
            description = answer.content
            if description.lower() == "none":
                description = discord.Embed.Empty
        except asyncio.TimeoutError:
            await ctx.send("You took too long to answer. Aborting.")
            return

        if not category:
            category = await ctx.guild.create_category(
                "threads",
                reason=f"Thread {channel_name} setup",
                overwrites=ctx.channel.category.overwrites if ctx.channel.category else None,
            )

        channel = await category.create_text_channel(
            channel_name,
            reason=f"Thread {channel_name} setup",
            overwrites=ctx.channel.overwrites,
        )
        if title or description:
            embed = discord.Embed(
                title=title,
                description=description,
            )
            message = await channel.send(embed=embed)
            await message.pin(reason=f"Thread {channel_name} setup")
            await ctx.send("I created the channel and sent the message")
        else:
            message = None
            await ctx.send(
                "I created the channel but didn't send the message as I had "
                "no description and no title."
            )

        async with self.bot.pool.acquire() as database:
            await database.execute(
                "INSERT INTO public.threads VALUES ($1, $2, $3)",
                ctx.author.id,
                channel.id,
                message.id if message else None,
            )

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True, manage_channels=True)
    @thread.command(name="unlock")
    async def thread_unlock(self, ctx: commands.Context, *, reason: str = None):
        """Unlock the thread, restoring the permissions to their state before `lock` was invoked."""
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.threads WHERE channel_id=$1",
                ctx.channel.id,
            )
        if not row:
            await ctx.send("This channel isn't a thread. Aborting.")
            return
        if not row["locked"]:
            await ctx.send("This thread isn't locked. Aborting.")
            return
        if row["overwrites"]:
            overwrites = {}
            for role_id, allow, deny in row["overwrites"]:
                try:
                    role = ctx.guild.get_role(role_id) or ctx.guild.get_member(
                        role_id
                    ) or await ctx.guild.fetch_member(role_id)
                except discord.NotFound:
                    continue
                overwrites[role] = discord.PermissionOverwrite.from_pair(
                    discord.Permissions(permissions=allow),
                    discord.Permissions(permissions=deny)
                )
            await ctx.channel.edit(overwrites=overwrites)
        else:
            await ctx.channel.set_permissions(
                ctx.guild.default_role,
                send_messages=True,
                reason=reason,
            )

        async with self.bot.pool.acquire() as database:
            await database.execute(
                "UPDATE public.threads SET overwrites=$1, "
                "locked=$2 "
                "WHERE channel_id=$3",
                None,
                False,
                ctx.channel.id,
            )
        await ctx.send("Thread unlocked")


def setup(bot: commands.Bot) -> None:
    """Load the Threads cog."""
    bot.add_cog(Threads(bot))
