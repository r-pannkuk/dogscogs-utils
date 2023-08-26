from redbot.core import commands

class Percent(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        try:
            if argument[-1] == "%":
                return float(argument[:-1]) / 100
            return float(argument)
        except:
            raise commands.BadArgument("Chance must be between (0, 1]")