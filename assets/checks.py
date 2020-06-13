from cogs.utils.constants import ids


async def perms(perms, g, c, m):
    for perm in perms:
        if not dict(g.me.guild_permissions).get(perm):
            await c.send(f'I must have the `{perm.upper()}` permission to do this.')
            return False
        if not dict(m.guild_permissions).get(perm):
            await c.send(f'You must have the `{perm.upper()}` permission to do this.')
            return False
    return True


async def owner(c, m):
    if m.id not in ids:
        await c.send('You must be an owner to use this command.')
    return m.id in ids


async def roles(auth, mem, g, c):
    if g.me.top_role < mem.top_role:
        await c.send('I am at a lower level on the role hierarchy than this member.')
    elif auth.top_role < mem.top_role:
        await c.send('This member has a higher role than you.')
    else:
        return True
    return False
