from discord import (
    Color,
    Embed,
    Role
)
from discord.ext.commands import (
    Cog,
    Context,
    command,
    has_permissions
)
from bot.core.bot import Bot


class Announcements(Cog):
    """Commands to get pinged while announcement commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    async def subscribe(self, ctx: Context) -> None:
        """Subscribe to pings."""
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.subscribe WHERE guild_id=$1",
                ctx.guild.id
            )

        if not row:
            await ctx.send("ERROR! The Announcement role hasn't been configured for this server!")

        role = discord.utils.find(lambda r: r.id == row["role_id"], ctx.guild.roles)
        if role in user.roles:
            await ctx.send("You're already subscribed!")
        else:
            user.add_roles(role)
            await ctx.send("You're Finally Subscribed!")

    @command()
    async def unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe from pings."""
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.subscribe WHERE guild_id=$1",
                ctx.guild.id
            )

        if not row:
            await ctx.send("ERROR! The Announcement role hasn't been configured for this server!")

        role = discord.utils.find(lambda r: r.id == row["role_id"], ctx.guild.roles)
        if role not in user.roles:
            await ctx.send("You're already unsubscribed!")
        else:
            user.remove_roles(role)
            await ctx.send("Oh No! You unsubscribed!")

    @command()
    @has_permissions(manage_roles=True)
    async def announcement_role(self, ctx: Context, role: Role) -> None:
        """Add the announcement role."""
        if isinstance(role, Role):
            role = role.id

        async with self.bot.pool.acquire() as database:
            await database.execute(
                "INSERT INTO public.subscribe (guild_id, role_id) VALUES ($1, $2)",
                ctx.guild.id,
                role
            )

        await ctx.send(f"The role has been Successfully to {role_id.mention}")


def setup(bot: Bot) -> None:
    """Load the Common cog."""
    bot.add_cog(Announcements(bot))
