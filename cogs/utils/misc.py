import random

import discord
# TODO : This package is installed here. The Pipfile and Pipfile.lock is updated, couldn't install!
from argon2 import PasswordHasher, exceptions as argerr

from cogs.utils import async_helper


def random_color():
    return random.randint(0, 255**3-1)


async def distribute_pages(pager_list, per_page):
    final_paged_product = []

    if len(pager_list) > per_page + 1:
        # If you can perfectly split the content into pages with
        # per_page amount of items each then there will be no remainders.
        if len(pager_list) % per_page == 0:
            remain = None
        # There is a remainder
        else:
            remain = len(pager_list) % per_page

        # Iterates through the content list with each iteration accessing per_page amount of items
        for items in zip(*[iter(pager_list)] * per_page):
            final_paged_product.append("".join(items))

        # Adds in the amount of remaining (which would be the items at the end of the list) items to the final product
        if remain:
            final_paged_product.append("".join(pager_list[-remain:]))
    else:
        final_paged_product = ["".join(pager_list)]

    return final_paged_product


async def dm_user(user, **content):
    try:
        await user.send(**content)
    except discord.Forbidden:
        return False


async def hash_pass(password):
    ph = PasswordHasher()
    try:
        return await async_helper.run_async_with_adjustable_timeout(ph.hash, password=password, timelimit=0.09)
    except argerr.HashingError:
        raise argerr.HashingError


async def verify_pass(p_hash, password):
    ph = PasswordHasher()
    try:
        return await async_helper.run_async_with_adjustable_timeout(ph.verify, hash=p_hash,
                                                          password=password, timelimit=0.09)
    except argerr.VerificationError:
        return False
    except Exception as e:
        raise e
