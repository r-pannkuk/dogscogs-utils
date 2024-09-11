from ..constants import TIMEZONE as TIMEZONE
from _typeshed import Incomplete
from collections.abc import Generator
from datetime import datetime as datetime

def date_formats() -> Generator[Incomplete, None, None]: ...
def to_birthdate(*args, **kwargs): ...
def duration_string(hours: int, minutes: int, seconds: int) -> str:
    """Converts hours, minutes, and seconds into a string duration.

    Args:
        hours (int): Integer number of hours.
        minutes (int): Integer number of minutes.
        seconds (int): Integer number of seconds.

    Returns:
        str: The completed string composing of the duration.
    """
def parse_duration_string(input: str) -> int:
    """Parses a duration string into the number of seconds it composes.

    Args:
        input (str): The input string to parse.

    Returns:
        int: The number of seconds in duration that string is.
    """
