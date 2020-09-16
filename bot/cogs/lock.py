import re
import textwrap
import typing

from discord import Color, Embed, Guild, Member, Message, TextChannel
from discord.ext.commands import Cog, Context, command, has_permissions, Greedy

from bot.core.bot import Bot


class Lock(Cog):
    """Lock your server to avoid raiding."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.lock_cache = {}  # guild_id: lock_state
        self.link_cache = {}  # guild_id: link_state

    # STATICMETHODS

    @staticmethod
    def get_codes(string: str) -> typing.List[str]:
        """Get the invite codes codes from a link."""
        return re.findall(
            r"(?:https?:\/\/)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|(?:discordapp|discord)\.com\/invite)\/([a-z\-\_]+)",
            string,
        )

    @staticmethod
    async def is_our_invite(fragment: str, guild: Guild) -> bool:
        """Check if the invite code is an invite for the given guild."""
        return fragment in [invite.code for invite in await guild.invites()]

    # DATABASE METHODS

    async def get_lock(self, guild_id: int) -> int:
        """Ensure that the given guild_id is in the database."""
        if guild_id in self.lock_cache:
            return self.lock_cache[guild_id]

            async with self.bot.pool.acquire() as database:
                row = await database.fetchrow(
                    "SELECT * FROM public.lock WHERE guild_id=$1",
                    guild_id
                )
                if row:
                    self.lock_cache[guild_id] = row["lock_state"]
                    return row["lock_state"]

                await database.execute(
                    "INSERT INTO public.lock VALUES ($1, 0)",
                    guild_id,
                )
                self.lock_cache[guild_id] = 0

    async def get_link(self, guild_id: int) -> int:
        """Ensure that the given guild_id is in the database."""
        if guild_id in self.link_cache:
            return self.link_cache[guild_id]

        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.lock WHERE guild_id=$1",
                guild_id
            )

            if row:
                self.lock_cache[guild_id] = row["link_state"]
                return row["link_state"]

            await database.execute(
                "INSERT INTO public.lock (guild_id, link_state) VALUES ($1, 0)",
                guild_id,
            )
            self.link_cache[guild_id] = 0

    # COG EVENTS

    @Cog.listener("on_member_join")
    async def apply_lock(self, member: Member) -> None:
        """Apply the lock status if there is one."""
        status = await self.get_lock(member.guild.id)

        if status == 2:
            await member.ban()

        elif status == 1:
            await member.kick()

    @Cog.listener("on_message")
    async def apply_link(self, message: Message) -> None:
        """Apply the link_lock status."""
        status = await self.get_link(message.guild.id)

        if status >= 2:
            for code in self.get_codes(message.content):
                if not await self.is_our_invite(code, message.guild):
                    await message.channel.send(
                        f"{message.author.mention}, you are not allowed to post other servers' invites!"
                    )
                    await message.delete()
            return

        if status == 1:
            if "http://" in message or "https://" in message:
                await message.channel.send(
                    f"{message.author.mention}, you are not allowed to post any links here!"
                )
                await message.delete()
            return

    # -------COMMANDS--------
    @command(name="link-lock", aliases=["linklock", "l-lock"])
    @has_permissions(kick_members=True)
    async def link_lock(self, ctx: Context) -> None:
        """Prevent everybody from posting other server's invites."""
        status = await self.get_link(ctx.guild.id)

        if status:
            link_status = 'Link' if status == 1 else 'Discord Invite'

            embed = Embed(
                title="Link Lock Error!",
                description=(
                    f"⚠️ {link_status} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}link-unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        self.link_cache[ctx.guild.id] = 1

        async with self.bot.pool.acquire() as database:
            await database.execute(
                "UPDATE public.lock SET link_state=1 WHERE guild_id=$1",
                ctx.guild.id,
            )

        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Discord Link Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: No user can now post any link on the server.
            """
        )
        embed = Embed(
            title="Link Lock Enabled",
            description=desc,
            color=Color.blue()
        )
        await ctx.send(embed=embed)

    @command(name="invite-lock", aliases=["invitelock", "i-lock"])
    @has_permissions(kick_members=True)
    async def invite_lock(self, ctx: Context) -> None:
        """Lock invites on the server."""
        status = await self.get_link(ctx.guild.id)

        if status:
            link_status = 'Link' if status == 1 else 'Discord Invite'

            embed = Embed(
                title="Link Lock Error!",
                description=(
                    f"⚠️ {link_status} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}link-unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        self.link_cache[ctx.guild.id] = 2

        async with self.bot.pool.acquire() as database:
            await database.execute(
                "UPDATE public.lock SET link_state=2 WHERE guild_id=$1",
                ctx.guild.id,
            )

        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Discord Invite Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: All users sending other servers' invited's messages will be removed and warned.
            """
        )
        embed = Embed(
            title="Link Lock Enabled",
            description=desc,
            color=Color.blue()
        )
        await ctx.send(embed=embed)

    @command(name="link-unlock", aliases=["linkunlock", "l-unlock"])
    @has_permissions(kick_members=True)
    async def link_unlock(self, ctx: Context) -> None:
        """Remove the link lock."""
        status = await self.get_link(ctx.guild.id)

        if not status:
            embed = Embed(
                title="Link Lock Error!",
                description=(
                    "⚠️ Link Lock is already disabled on this server!"
                ),
            )
            await ctx.send(embed=embed)
            return

        self.link_cache[ctx.guild.id] = 0

        async with self.bot.pool.acquire() as database:
            await database.execute(
                "UPDATE public.lock SET link_state=0 WHERE guild_id=$1",
                ctx.guild.id,
            )

        embed = Embed(
            title="Link Lock Disabled",
            description="Link Lock has been successfully.",
            color=Color.blue()
        )
        await ctx.send(embed=embed)

    @command(name="ban-lock", aliases=["b-lock", "banlock"])
    @has_permissions(kick_members=True)
    async def ban_lock(self, ctx: Context) -> None:
        """Ban all new members."""
        status = await self.get_lock(ctx.guild.id)

        if status:
            lock_status = 'Kick' if status == 1 else 'Ban'

            embed = Embed(
                title="Server Lock Error!",
                description=(
                    f"⚠️ {lock_status} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}server-unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        self.lock_cache[ctx.guild.id] = 2

        async with self.bot.pool.acquire() as database:
            await database.execute(
                "UPDATE public.lock SET lock_state=2 WHERE guild_id=$1",
                ctx.guild.id,
            )

        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Ban Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: All users joining while the lock is on will be banned until it is lifted.
            """
        )
        embed = Embed(
            title="Server Lock Enabled",
            description=desc,
            color=Color.blue()
        )
        await ctx.send(embed=embed)

    @command(name="kick-lock", aliases=["k-lock", "kicklock"])
    @has_permissions(kick_members=True)
    async def kick_lock(self, ctx: Context) -> None:
        """Kick all new members."""
        status = await self.get_lock(ctx.guild.id)

        if status:
            lock_type = 'Kick' if status == 1 else 'Ban'
            embed = Embed(
                title="Server Lock Error!",
                description=(
                    f"⚠️ {lock_type} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}server-unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        self.lock_cache[ctx.guild.id] = 1

        async with self.bot.pool.acquire() as database:
            await database.execute(
                "UPDATE public.lock SET lock_state=1 WHERE guild_id=$1",
                ctx.guild.id,
            )

        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Kick Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: All users joining while the lock is on will be kicked until it is lifted.
            """
        )
        embed = Embed(
            title="Server Lock Enabled",
            description=desc,
            color=Color.blue()
        )
        await ctx.send(embed=embed)

    @command(name="server-unlock", aliases=["s-unlock", "serverunlock"])
    @has_permissions(kick_members=True)
    async def server_unlock(self, ctx: Context) -> None:
        """Unlock the server."""
        status = await self.get_lock(ctx.guild.id)

        if not status:
            embed = Embed(
                description="⚙️The server is already unlocked! ",
                color=Color.red(),
            )
            await ctx.send(embed=embed)
            return

        self.lock_cache[ctx.guild.id] = 0
        async with self.bot.pool.acquire() as database:
            await database.execute(
                "UPDATE public.lock set lock_state=0 WHERE guild_id=$1",
                ctx.guild.id,
            )
        embed = Embed(
            description="Server Locks Are Successfully Disabled! You can now invite your friends :D",
            color=Color.blue()
        )
        await ctx.send(embed=embed)

    @command(name="channel-lock", aliases=["channellock", "c-lock"])
    @has_permissions(manage_channels=True)
    async def channel_lock(self, ctx: Context, channels: Greedy[TextChannel] = None, reason: str = 'Not Specified') -> None:
        """Disable @everyone's permission to send message on given channel or current channel if not specified."""
        if channels is None:
            channels = [ctx.channel]

        channel_count = 0
        for channel in channels:
            if channel.permissions_for(ctx.author).manage_channels:
                await channel.set_permissions(
                    channel.guild.default_role,
                    send_messages=False,
                    reason=f"Reason: {reason} | Requested by {ctx.author}."
                )
                channel_count += 1
            else:
                continue
            await channel.send("🔒 Locked down this channel.")
        if channels != [ctx.channel]:
            await ctx.send(f"Locked down {channel_count} channel{'s' if channel_count > 1 else ''}.")

    @command(name="channel-unlock", aliases=["channelunlock", "c-unlock"])
    @has_permissions(manage_channels=True)
    async def channel_unlock(self, ctx: Context, channels: Greedy[TextChannel] = None, reason: str = 'Not specified') -> None:
        """Reset @everyone's permission to send message on given channel or current channel if not specified."""
        if channels is None:
            channels = [ctx.channel]

        channel_count = 0
        for channel in channels:
            if channel.permissions_for(ctx.author).manage_channels:
                await channel.set_permissions(
                    channel.guild.default_role,
                    send_messages=None,
                    reason=f"Reason: {reason} | Requested by {ctx.author}."
                )
                channel_count += 1
            else:
                continue
        await ctx.send(f"Unlocked {channel_count} channel{'s' if channel_count > 1 else ''}.")

    @command(name="maintenance-lock", aliases=["maintenancelock", "m-lock"])
    @has_permissions(manage_channels=True)
    async def maintenance_lock(self, ctx: Context) -> None:
        """Disable @everyone's permission to send message on all channels."""
        channel_count = 0

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(
                channel.guild.default_role,
                send_messages=False,
                reason=f"Reason: Server Under Maintenance | Requested by {ctx.author}."
            )
            channel_count += 1
            await channel.send("🔒 Locked down this channel.")

        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(
                channel.guild.default_role,
                connect=False,
                reason=f"Reason: Server Under Maintenance | Requested by {ctx.author}."
            )
            channel_count += 1

        await ctx.send(f"Locked down {channel_count} channel{'s' if channel_count > 1 else ''}. Server Under Maintenance.")

    @command(name="maintenance-unlock", aliases=["maintenanceunlock", "m-unlock"])
    @has_permissions(manage_channels=True)
    async def maintenance_unlock(self, ctx: Context) -> None:
        """Enable @everyone's permission to send message on all channels."""
        channel_count = 0

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(
                channel.guild.default_role,
                send_messages=None,
                reason=f"Reason: Server Maintenance Lifted | Requested by {ctx.author}."
            )
            channel_count += 1
            await channel.send("🔒 Unlocked down this channel.")

        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(
                channel.guild.default_role,
                connect=None,
                reason=f"Reason: Server Maintenance Lifted | Requested by {ctx.author}."
            )
            channel_count += 1

        await ctx.send(f"Unlocked down {channel_count} channel{'s' if channel_count > 1 else ''}. Server Maintenance Lifted.")


def setup(bot: Bot) -> None:
    """Load the Lock cog."""
    bot.add_cog(Lock(bot))
