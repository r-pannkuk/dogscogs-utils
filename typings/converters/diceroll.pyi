from ..core.converter import DogCogConverter as DogCogConverter
from redbot.core import commands

class DiceRoll(DogCogConverter):
    @staticmethod
    async def parse(_ctx: commands.Context, input: str) -> str: ...
