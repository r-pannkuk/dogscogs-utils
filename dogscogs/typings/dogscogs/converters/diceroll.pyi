from ..core.converter import DogCogConverter as DogCogConverter
from redbot.core import commands

class DiceRoll(DogCogConverter):
    @staticmethod
    async def parse(_ctx: commands.Context, input: str) -> str:
        """Converts a string to a float or a d20 roll.

        Args:
            input (str): The string argument input.

        Returns:
            typing.Union[float, str]: A float if it's a percentage, or a string if it's a d20 roll.
        """