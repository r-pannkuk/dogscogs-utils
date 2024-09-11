import abc
import datetime
from ..constants import TIMEZONE as TIMEZONE
from ..core.converter import DogCogConverter as DogCogConverter
from _typeshed import Incomplete
from collections.abc import Generator
from redbot.core import commands as commands

def date_formats() -> Generator[Incomplete, None, None]: ...

class BirthdayConverter(DogCogConverter, metaclass=abc.ABCMeta):
    """Returns a datetime object ignoring the birthday for a birthday string.
    """
    @staticmethod
    async def convert(_ctx: commands.Context, argument: str) -> datetime.datetime: ...
