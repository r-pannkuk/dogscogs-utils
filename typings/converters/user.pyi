import discord
from ..core.converter import DogCogConverter as DogCogConverter
from redbot.core.commands import GuildContext as GuildContext

class UserList(DogCogConverter):
    @staticmethod
    async def parse(ctx: GuildContext, argument: str) -> list[discord.User]: ...
