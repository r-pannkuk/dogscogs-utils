from datetime import datetime
from itertools import permutations
import re
from time import strptime
from redbot.core.commands import commands

from ..constants import TIMEZONE

import pytz


def date_formats():
    years = ("%Y", "%y")
    months = ("%b", "%B", "%m")
    days = ("%d",)

    for month in months:
        for day in days:
            for args in ((month, day), (day, month)):
                yield " ".join(args)
                yield "/".join(args)
                date_spaced = " ".join(args)
                date_slash = "/".join(args)
                for year in years:
                    for combo in permutations([year, date_spaced]):
                        yield " ".join(combo).strip()
                    for combo in permutations([year, date_slash]):
                        yield "/".join(combo).strip()


def to_birthdate(*args, **kwargs):
    for fmt in date_formats():
        try:
            return strptime(args[0], fmt).replace(year=1980).astimezone(tz=TIMEZONE)
        except ValueError:
            pass
    raise ValueError(f"{args[0]} is not a recognized date.")

def duration_string(hours: int, minutes: int, seconds: int) -> str:
    """Converts hours, minutes, and seconds into a string duration.

    Args:
        hours (int): Integer number of hours.
        minutes (int): Integer number of minutes.
        seconds (int): Integer number of seconds.

    Returns:
        str: The completed string composing of the duration.
    """
    hour_string = ""
    minute_string = ""
    second_string = ""

    if hours > 0:
        hour_string = f"{hours}"
        minute_string = f":{minutes:02}"
        second_string = f":{seconds:02}"
    elif minutes > 0:
        minute_string = f"{minutes}"
        second_string = f":{seconds:02}"
    else:
        second_string = f"{seconds} seconds"

    return f"{hour_string}{minute_string}{second_string}"


def parse_duration_string(input: str) -> int:
    """Parses a duration string into the number of seconds it composes.

    Args:
        input (str): The input string to parse.

    Returns:
        int: The number of seconds in duration that string is.
    """
    if(re.match("^[\\d]+:[0-5][0-9]:[0-5][0-9]$", input)):
        hours, rest = input.split(':', 1)
        t = strptime(rest, "%M:%S")
        return int(hours) * 60 * 60 + t.tm_min * 60 + t.tm_sec
    elif(re.match("^[0-9]?[0-9]:[0-5][0-9]$", input)):
        t = strptime(input, "%M:%S")
        return t.tm_min * 60 + t.tm_sec
    else:
        raise commands.BadArgument("Could not parse the duration.")