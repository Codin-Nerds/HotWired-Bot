from dateutil.relativedelta import relativedelta
from datetime import datetime
import typing as t


def stringify_timedelta(time_delta: relativedelta, min_unit: str = "seconds") -> str:
    """
    Convert `dateutil.relativedelta.relativedelta` into a readable string

    `min_unit` is used to specify the printed precision
    """
    time_dict = {
        "years": time_delta.years,
        "months": time_delta.months,
        "weeks": time_delta.weeks,
        "days": time_delta.days,
        "hours": time_delta.hours,
        "minutes": time_delta.minutes,
        "seconds": time_delta.seconds,
        "microseconds": time_delta.microseconds,
    }

    stringified_time = ""
    time_list = []

    for unit, value in time_dict.items():
        if value:
            time_list.append(f"{value} {unit if value != 1 else unit[:-1]}")

        if unit == min_unit:
            break

    if len(time_list) > 1:
        stringified_time = " ".join(time_list[:-1])
        stringified_time += f" and {time_list[-1]}"
    elif len(time_list) == 0:
        stringified_time = "now"
    else:
        stringified_time = time_list[0]

    return stringified_time


def time_elapsed(_from: datetime, to: t.Optional[datetime] = None) -> str:
    """
    Returns how much time has elapsed in a readable string

    when no `to` value is specified, current time is assumed
    """
    if not to:
        to = datetime.datetime.utcnow()

    delta = abs(to - _from)
    rel_delta = relativedelta.seconds = delta.total_seconds
    stringified_time = stringify_timedelta(rel_delta)
    return f"{stringified_time} ago."
