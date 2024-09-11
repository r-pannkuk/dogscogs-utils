import datetime
from itertools import permutations
from redbot.core import commands

from ..constants import TIMEZONE
from ..core.converter import DogCogConverter

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


class BirthdayConverter(DogCogConverter):
    """Returns a datetime object ignoring the birthday for a birthday string.
    """
    @staticmethod
    async def convert(_ctx: commands.Context, argument: str) -> datetime.datetime: # type:ignore[override]
        for fmt in date_formats():
            try:
                return datetime.datetime.strptime(argument, fmt).replace(year=1980).astimezone(tz=TIMEZONE)
            except ValueError:
                pass
        raise ValueError(f"{argument} is not a recognized date.")