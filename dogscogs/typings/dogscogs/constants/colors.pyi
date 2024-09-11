from _typeshed import Incomplete
from fractions import Fraction
from typing import Iterable

HSVTuple = tuple[Fraction, Fraction, Fraction]
RGBTuple = tuple[float, float, float]
DEFAULT_COLORS: Incomplete

def color_diff(rgb1, rgb2):
    """
    Determines the relative distance between two colors.
    """
def sort_palette(color):
    """
    Sorts a palette based on hue, then by lightness, then by saturation.
    """
def aggregate_palette(p):
    """
    Combines a palette together to get a superset.
    """
def min_palette_diff(p):
    """
    Finds the smallest distance between two elements of a palette.
    """
def get_palette(n: int = 100, Lmin: int = 5, Lmax: int = 90, maxLoops: int = 100000) -> Iterable[RGBTuple]:
    """
    Obtains a palette based on the number of colors desired.
    """
def hex_to_rgb(h: str) -> tuple[int, int, int]:
    """
    Converts a hex value to 3 rgb values.
    """
