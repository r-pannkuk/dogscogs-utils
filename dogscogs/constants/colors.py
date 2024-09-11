import colorsys
from fractions import Fraction
import itertools
import random
from typing import Iterable, Tuple
import typing

import discord


HSVTuple = Tuple[Fraction, Fraction, Fraction]
RGBTuple = Tuple[float, float, float]

DEFAULT_COLORS = [
    (240, 248, 255),
    (250, 235, 215),
    (0, 255, 255),
    (127, 255, 212),
    (240, 255, 255),
    (245, 245, 220),
    (255, 228, 196),
    (0, 0, 0),
    (255, 235, 205),
    (0, 0, 255),
    (138, 43, 226),
    (165, 42, 42),
    (222, 184, 135),
    (95, 158, 160),
    (127, 255, 0),
    (210, 105, 30),
    (255, 127, 80),
    (100, 149, 237),
    (255, 248, 220),
    (220, 20, 60),
    (0, 255, 255),
    (0, 0, 139),
    (0, 139, 139),
    (184, 134, 11),
    (169, 169, 169),
    (0, 100, 0),
    (189, 183, 107),
    (139, 0, 139),
    (85, 107, 47),
    (255, 140, 0),
    (153, 50, 204),
    (139, 0, 0),
    (233, 150, 122),
    (143, 188, 143),
    (72, 61, 139),
    (47, 79, 79),
    (0, 206, 209),
    (148, 0, 211),
    (255, 20, 147),
    (0, 191, 255),
    (105, 105, 105),
    (30, 144, 255),
    (178, 34, 34),
    (255, 250, 240),
    (34, 139, 34),
    (255, 0, 255),
    (220, 220, 220),
    (248, 248, 255),
    (255, 215, 0),
    (218, 165, 32),
    (128, 128, 128),
    (0, 128, 0),
    (173, 255, 47),
    (240, 255, 240),
    (255, 105, 180),
    (205, 92, 92),
    (75, 0, 130),
    (255, 255, 240),
    (240, 230, 140),
    (230, 230, 250),
    (255, 240, 245),
    (124, 252, 0),
    (255, 250, 205),
    (173, 216, 230),
    (240, 128, 128),
    (224, 255, 255),
    (250, 250, 210),
    (144, 238, 144),
    (211, 211, 211),
    (255, 182, 193),
    (255, 160, 122),
    (32, 178, 170),
    (135, 206, 250),
    (119, 136, 153),
    (176, 196, 222),
    (255, 255, 224),
    (0, 255, 0),
    (50, 205, 50),
    (250, 240, 230),
    (255, 0, 255),
    (128, 0, 0),
    (102, 205, 170),
    (0, 0, 205),
    (186, 85, 211),
    (147, 112, 219),
    (60, 179, 113),
    (123, 104, 238),
    (0, 250, 154),
    (72, 209, 204),
    (199, 21, 133),
    (25, 25, 112),
    (245, 255, 250),
    (255, 228, 225),
    (255, 228, 181),
    (255, 222, 173),
    (0, 0, 128),
    (253, 245, 230),
    (128, 128, 0),
    (107, 142, 35),
    (255, 165, 0),
    (255, 69, 0),
    (218, 112, 214),
    (238, 232, 170),
    (152, 251, 152),
    (175, 238, 238),
    (219, 112, 147),
    (255, 239, 213),
    (255, 218, 185),
    (205, 133, 63),
    (255, 192, 203),
    (221, 160, 221),
    (176, 224, 230),
    (128, 0, 128),
    (255, 0, 0),
    (188, 143, 143),
    (65, 105, 225),
    (139, 69, 19),
    (250, 128, 114),
    (244, 164, 96),
    (46, 139, 87),
    (255, 245, 238),
    (160, 82, 45),
    (192, 192, 192),
    (135, 206, 235),
    (106, 90, 205),
    (112, 128, 144),
    (255, 250, 250),
    (0, 255, 127),
    (70, 130, 180),
    (210, 180, 140),
    (0, 128, 128),
    (216, 191, 216),
    (255, 99, 71),
    (64, 224, 208),
    (238, 130, 238),
    (245, 222, 179),
    (255, 255, 255),
    (245, 245, 245),
    (255, 255, 0),
    (154, 205, 50),
]


def color_diff(rgb1, rgb2):
    """
    Determines the relative distance between two colors.
    """
    if isinstance(rgb1, discord.Colour):
        rgb1 = (rgb1.r, rgb1.g, rgb1.b)
    if isinstance(rgb2, discord.Colour):
        rgb2 = (rgb2.r, rgb2.g, rgb2.b)

    return (
        abs(rgb1[0] - rgb2[0]) ** 2
        + abs(rgb1[1] - rgb2[1]) ** 2
        + abs(rgb1[2] - rgb2[2]) ** 2
    )


def sort_palette(color):
    """
    Sorts a palette based on hue, then by lightness, then by saturation.
    """
    hls = colorsys.rgb_to_hls(color[0] / 255, color[1] / 255, color[2] / 255)
    return hls[0] * 100 + hls[1] * 5 + hls[2] * 5


def aggregate_palette(p):
    """
    Combines a palette together to get a superset.
    """
    result = 0
    for a, b in itertools.combinations(p, 2):
        result += color_diff(a, b)

    return result / len(p)


def min_palette_diff(p):
    """
    Finds the smallest distance between two elements of a palette.
    """
    min = None
    for a, b in itertools.combinations(p, 2):
        diff = color_diff(a, b)
        if min == None or diff < min:
            min = diff
    return diff


def get_palette(
    n: int = 100, Lmin: int = 5, Lmax: int = 90, maxLoops: int = 100000
) -> Iterable[RGBTuple]:
    """
    Obtains a palette based on the number of colors desired.
    """
    data = []

    for color in DEFAULT_COLORS:
        hls = colorsys.rgb_to_hls(color[0] / 255, color[1] / 255, color[2] / 255)
        L = 100 * hls[1]
        if (L >= Lmin) and (L <= Lmax):
            data.append(color)

    palettes = []

    for i in range(0, maxLoops):
        palettes.append(random.sample(data, k=n))

    palettes.sort(key=min_palette_diff, reverse=True)

    bestPalette = palettes[0]

    bestPalette.sort(key=sort_palette)

    return bestPalette


# def rgbs(num_colors) -> Iterable[RGBTuple]:
#     """
#     Obtains a palette based on the number of colors desired.
#     """
#     colors = [(0.08, 0.08, 0.08), (1, 1, 1), (0.5, 0.5, 0.5)]
#     if num_colors > 3:
#         for i in np.arange(0., 360., 360. / (num_colors - 3)):
#             hue = i/360.
#             lightness = (50 + np.random.rand() * 10)/100.
#             saturation = (90 + np.random.rand() * 10)/100.
#             colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
#     return colors


# https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    """
    Converts a hex value to 3 rgb values.
    """
    h = h.replace("#", "").replace("0x", "").replace("0X", "")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) # type: ignore[return-value]

