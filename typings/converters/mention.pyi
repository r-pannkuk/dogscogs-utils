import discord
from ..core.converter import DogCogConverter as DogCogConverter
from redbot.core import commands

class Mention(DogCogConverter):
    @staticmethod
    async def parse(ctx: commands.Context, input: str) -> discord.TextChannel | discord.Member | discord.Role: ...
