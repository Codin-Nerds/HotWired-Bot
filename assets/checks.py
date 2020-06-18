from cogs.utils.constants import ids
import typing as t


async def perms(perms, guild, ctx, member) -> bool:
    for perm in perms:
        if not dict(guild.me.guild_permissions).get(perm):
            await ctx.send(f'I must have the `{perm.upper()}` permission to do this.')
            return False
        if not dict(member.guild_permissions).get(perm):
            await ctx.send(f'You must have the `{perm.upper()}` permission to do this.')
            return False
    return True


async def owner(ctx, member) -> int:
    if member.id not in ids:
        await ctx.send('You must be an owner to use this command.')
    return member.id in ids


async def roles(auth, mem, guild, ctx) -> t.Union[bool, None]:
    if guild.me.top_role < mem.top_role:
        await ctx.send('I am at a lower level on the role hierarchy than this member.')
    elif auth.top_role < mem.top_role:
        await ctx.send('This member has a higher role than you.')
    else:
        return True
    return False
