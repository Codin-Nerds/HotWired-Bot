from discord import TextChannel, Role, User, utils
from discord.ext.commands import Cog, Context, group, check, guild_only

from bot.core.bot import Bot


class Dungeon(Cog):
    """Quarantine the users with an account less than specified days of creation."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(autohelp=True)
    @guild_only()
    @check(manage_guild=True)
    async def dungeon(self, ctx: Context) -> None:
        """Main dungeon commands."""
        pass

    @dungeon.command()
    async def toggle(self, ctx: Context) -> None:
        """Toggle the dungeon on or off."""
        async with self.pool.acquire(timeout=5) as database:
            for row in await database.fetch("SELECT * FROM public.lock"):
                kick_lock = row["kick_lock"]
                ban_lock = row["ban_lock"]

        if kick_lock and ban_lock:
            await ctx.send("Please disable the server locks, before toggling the dungeon lock!")
            return

        async with self.pool.acquire(timeout=5) as database:
            for row in await database.fetch("SELECT * FROM public.dungeon"):
                dungeon_enabled = row["dungeon_status"]

        if not dungeon_enabled:
            async with self.bot.pool.acquire() as database:
                await database.execute(
                    """
                    INSERT INTO public.dungeon (guild_id, dungeon_status) VALUES ($1, $2)
                    ON CONFLICT (guild_id) DO UPDATE SET dungeon_status=$2
                    """,
                    ctx.guild.id,
                    True
                )
        else:
            async with self.bot.pool.acquire() as database:
                await database.execute(
                    """
                    INSERT INTO public.dungeon (guild_id, dungeon_status) VALUES ($1, $2)
                    ON CONFLICT (guild_id) DO UPDATE SET dungeon_status=$2
                    """,
                    ctx.guild.id,
                    False
                )

        await ctx.send(f"Dungeon enabled: {dungeon_enabled}.")

    @dungeon.command()
    async def announce(self, ctx: Context, channel: TextChannel) -> None:
        """Sets the announcement channel for users moved to the dungeon."""
        async with self.bot.pool.acquire() as database:
            await database.execute(
                """
                INSERT INTO public.dungeon (guild_id, announcement_channel) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET announcement_channel=$2
                """,
                ctx.guild.id,
                channel.id
            )

        await ctx.send(
            f"Quarantined User announcement channel set to: {channel.mention}."
        )

    @dungeon.command()
    async def message(self, ctx: Context, message: str = None) -> None:
        """Message to be sent when kick or ban is enabled for Dungeoned users."""
        if not message:
            message = "You have been banned due to lack of required days, to join the Server."

        async with self.bot.pool.acquire() as database:
            await database.execute(
                """
                INSERT INTO public.dungeon (guild_id, mod_message) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET mod_message=$2
                """,
                ctx.guild.id,
                message
            )

        await ctx.send(f"Message has been turned on.\nMessage to send on ban:\n{message}")

    @dungeon.command()
    async def joindays(self, ctx: Context, days: int = None) -> None:
        """Set how old an account needs to be a trusted user."""
        if not days:
            days = 1

        if days <= 0:
            await ctx.send("The number of days must be atleast 1!")
            days = 1

        async with self.bot.pool.acquire() as database:
            await database.execute(
                """
                INSERT INTO public.dungeon (guild_id, minimum_days) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET minimum_days=$2
                """,
                ctx.guild.id,
                days
            )

        await ctx.send(
            f"Users must have accounts older than {days} day(s) to be awarded the member role instead of the dungeon role on join."
        )

    @dungeon.command()
    async def role(self, ctx: Context, role: Role = None) -> None:
        """Sets the role to use for the dungeon."""
        if not role:
            await ctx.send("Please specify a Role!")
            return

        if isinstance(role, Role):
            role = role.id

        async with self.bot.pool.acquire() as database:
            await database.execute(
                """
                INSERT INTO public.dungeon (guild_id, minimum_days) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET minimum_days=$2
                """,
                ctx.guild.id,
                role
            )

        dungeon_role = utils.get(ctx.guild.roles, role)

        await ctx.send(f"Dungeon role set to: {dungeon_role.name}.")

    @dungeon.command()
    async def add_bypass(self, ctx: Context, user: User) -> None:
        query = "SELECT * FROM public.dungeon"

        async with self.pool.acquire(timeout=5) as database:
            for row in await database.fetch(query):
                bypassers = row["bypass_list"]
                bypassers = set(bypassers)

        if isinstance(user, User):
            user = user.id

        bypassers.append(user)

        async with self.bot.pool.acquire() as database:
            await database.execute(
                """
                INSERT INTO public.dungeon (guild_id, bypass_list) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET bypass_list=$2
                """,
                ctx.guild.id,
                bypassers
            )

        await ctx.send(f"<@!{user}> Successfully added to the bypass list.")

    @dungeon.command()
    async def remove_bypass(self, ctx: Context, user: User) -> None:
        query = "SELECT * FROM public.dungeon"

        async with self.pool.acquire(timeout=5) as database:
            for row in await database.fetch(query):
                bypassers = row["bypass_list"]
                bypassers = set(bypassers)

        if isinstance(user, User):
            user = user.id

        bypassers.remove(user)

        async with self.bot.pool.acquire() as database:
            await database.execute(
                """
                INSERT INTO public.dungeon (guild_id, bypass_list) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET bypass_list=$2
                """,
                ctx.guild.id,
                bypassers
            )

        await ctx.send(f"<@!{user}> Successfully added to the bypass list.")

    @dungeon.command()
    async def show_bypass(self, ctx: Context, user: User) -> None:
        query = "SELECT * FROM public.dungeon"

        async with self.pool.acquire(timeout=5) as database:
            for row in await database.fetch(query):
                bypassers = row["bypass_list"]
                bypassers = set(bypassers)

        if isinstance(user, User):
            user = user.id

        bp_list = '\n'.join(bypassers)

        await ctx.send(f"Bypass List:\n```{bp_list}```")


def setup(bot: Bot) -> None:
    bot.add_cog(Dungeon(bot))
