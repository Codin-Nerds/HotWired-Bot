async def author_has_ch_perm(ctx, channel, **perms):
    user_perm_for_channel = channel.permissions_for(ctx.author)

    check = [has_perm for has_perm, value in perms.items() if not getattr(user_perm_for_channel, has_perm) != value]

    if not check:
        return False
    else:
        return True


async def return_all_permissions_for_author(ctx, channel):
    user_perm_for_channel = channel.permissions_for(ctx.author)
    results = {}
    for perms, value in iter(user_perm_for_channel):
        if perms is not None and value is not None:
            results[perms] = value
    return results


async def return_all_permissions_for_bot(bot_guild_me, channel):
    user_perm_for_channel = channel.permissions_for(bot_guild_me)
    results = {}
    for perms, value in iter(user_perm_for_channel):
        if perms is not None and value is not None:
            results[perms] = value
    return results


async def user_has_ch_perm(user, channel, **perms):
    user_perm_for_channel = channel.permissions_for(user)

    check = [has_perm for has_perm, value in perms.items() if not getattr(user_perm_for_channel, has_perm) != value]

    if not check:
        return False
    else:
        return True


async def bot_has_ch_perm(bot_guild_me, channel, **perms):
    bot_perm_for_channel = channel.permissions_for(bot_guild_me)

    check = [has_perm for has_perm, value in perms.items() if not getattr(bot_perm_for_channel, has_perm) != value]

    if not check:
        return False
    else:
        return True
