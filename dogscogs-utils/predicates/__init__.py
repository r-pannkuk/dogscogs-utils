import re
import typing
import discord
from redbot.core import Config

from converters.diceroll import DiceRoll
from converters.percent import Percent
from constants import regex

async def validate_true(str: str, interaction: discord.Interaction):
    return True

async def validate_number_or_diceroll(input: str, interaction: discord.Interaction):
    try:
        float(input)
        return True
    except:
        try:
            await DiceRoll.parse(input)
            return True
        except:
            return False

async def validate_percent_or_diceroll(input: str, interaction: discord.Interaction):
    try:
        await Percent.parse(input)
        return True
    except:
        try:
            DiceRoll.parse(input)
            return True
        except:
            return False

async def validate_not_in_list(list: typing.List[str], input: str, interaction: discord.Interaction):
    return input.lower() not in list

async def validate_image(input: str, _interaction: discord.Interaction):
    return input == "" or re.match(regex.IMAGE, input) is not None

async def validate_length(length: int, input: str, interaction: discord.Interaction):
    return len(input) <= length