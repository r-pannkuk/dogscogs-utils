from ..core.converter import DogCogConverter as DogCogConverter
from redbot.core import commands

class Percent(DogCogConverter):
    @staticmethod
    async def parse(ctx: commands.Context, input: str) -> float: ...
