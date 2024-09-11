from abc import abstractmethod, ABC
from redbot.core import commands
import typing


class DogCogConverter(ABC, commands.Converter):
    @staticmethod
    @abstractmethod
    async def parse(ctx: commands.Context, input: str) -> typing.Any:
        pass

    async def convert(self, ctx: commands.Context, argument: str):  # type: ignore[override]
        try: 
            return await self.__class__.parse(ctx, argument)
        except commands.BadArgument as ba:
            await ctx.send(str(ba))
            raise ba