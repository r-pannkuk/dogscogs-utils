from redbot.core import commands

from ..core.converter import DogCogConverter

class Percent(DogCogConverter):
    @staticmethod
    async def parse(ctx: commands.Context, input: str) -> float:
        try:
            if input[-1] == "%":
                return float(input[:-1]) / 100
            return float(input)
        except:
            raise commands.BadArgument("Invalid percent value.")