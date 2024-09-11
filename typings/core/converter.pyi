import abc
import typing
from abc import ABC, abstractmethod
from redbot.core import commands

class DogCogConverter(ABC, commands.Converter, metaclass=abc.ABCMeta):
    @staticmethod
    @abstractmethod
    async def parse(ctx: commands.Context, input: str) -> typing.Any: ...
    async def convert(self, ctx: commands.Context, argument: str): ...
