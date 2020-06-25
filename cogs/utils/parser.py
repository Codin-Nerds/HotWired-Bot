import re
import string
from datetime import datetime
from typing import Union, Optional

import discord
from dateutil.relativedelta import relativedelta

from cogs.utils import nlp_dates


async def user_parser(bot, username: Union[discord.User, discord.ClientUser, discord.Member, str] = None, ctx=None):
    if isinstance(username, (discord.User, discord.ClientUser, discord.Member)):
        return username

    if not username and ctx:
        user = ctx.author
        return user
    elif username:
        parsed = "".join(re.findall(r"\d+", username))

        if len(parsed) == 0:
            return False
        try:
            user = bot.get_user(int(parsed))
            if user is None:
                user = await bot.fetch_user(int(parsed))
        except discord.NotFound:
            user = None

        return user if user else False
    else:
        return False


async def channel_parser(channel: Union[discord.TextChannel, discord.VoiceChannel] = None,
                         ctx=None):
    """Parses message into a channel"""
    if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
        return channel
    elif not channel and ctx:
        parsed_channel = ctx.message.author
        return parsed_channel
    else:
        return False


async def role_parser(role: Optional[discord.Role]):
    if isinstance(role, discord.Role):
        return role
    else:
        return False


async def human_readable_number(number):
    number = float(number)
    pow_ten = 0

    while abs(number) >= 1000:
        pow_ten += 1
        number /= 1000

    suffix = ['', 'k', 'm', 'b', 't', "q"][pow_ten]

    if pow_ten:
        return f"{round(number,2)}{suffix}"
    else:
        return f"{round(number)}{suffix}"


async def timestamp_parser(ctx, message, check=0):
    converter = nlp_dates.HumanTimeParser(check)
    return await converter.convert(ctx, message)


async def no_ctx_tm_parser(message, check=0):
    converter = nlp_dates.NoCtxHumanTimeParser(check)
    return await converter.convert(message)


async def remove_special(message, regex=None):
    if regex:
        message = re.sub(regex, "", message)
    return "".join(filter(lambda x: x in string.printable, message))


async def back_front_parser(message, length_of_search: int = None, is_list=False):
    if is_list is False:
        return [message[:length_of_search], message[-length_of_search:]]
    elif is_list is True:
        return [message[0], message[-1]]

        #
        # when_value = int("".join(re.findall(r"\d+", "".join(timestamp))))
        # times = "".join(re.findall("[A-Za-z]", "".join(timestamp)))
        # when_term = conversion_table[times]
        #
        # if when_term == "years":
        #     when_term = "days"
        #     when_value *= 365
        #
        # if ret:
        #     return (
        #         datetime.datetime.utcnow() + datetime.timedelta(**{when_term: when_value}),
        #         " ".join(message).replace(" ".join(timestamp), "")
        #     )
        # else:
        #     return datetime.datetime.utcnow() + datetime.timedelta(**{when_term: when_value})


async def human_readable_datetime_parser(ctx, time, dt=True, show_all=False, varient=0):
    """Converts a datetime object to a human readable version
    Varient 0 example: 3 hours 50 min
    Varient 1 example: 3:50:02
    """
    now = datetime.utcnow()

    if dt is False:
        time = relativedelta(seconds=time.total_seconds())
    else:
        if time > now:
            time = relativedelta(time, now)
        else:
            time = relativedelta(now, time)
    if time.microseconds >= 900000:
        time.microseconds, time.seconds = 0, time.minutes+1
        time = time.normalized()

    unit_list = ["y", "mo", "d", "h", "m", "s"] if varient is 0 else [":"] * 6
    reldelta_unit_list = ["years", "months", "days", "hours", "minutes", "seconds"]
    unit_list = {delta_name: dis_name for delta_name, dis_name in zip(reldelta_unit_list, unit_list)}

    processed = []
    for id_index, (delta_name, dis_name) in enumerate(unit_list.items()):
        time_quanity = int(getattr(time, delta_name))

        if varient is 1:
            if len([quan for quan in processed if quan != 0]) > 2:
                continue
            elif time_quanity is 0 and (show_all == 2 and id_index in [0, 1, 2, 3]):
                continue
            elif len(str(time_quanity)) == 1 and time_quanity != 0:
                time_quanity = str(time_quanity).zfill(2)

        if not show_all and time_quanity is 0:
            continue

        processed.append(f"{time_quanity}{dis_name}")
    if varient is 0:
        return " ".join(processed)
    elif varient is 1:
        return "".join(processed).strip(":")
