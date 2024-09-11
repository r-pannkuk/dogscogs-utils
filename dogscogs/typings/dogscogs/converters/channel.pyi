from ..constants.discord.channel import TEXT_TYPES as TEXT_TYPES
from ..core.converter import DogCogConverter as DogCogConverter
from redbot.core import commands

class TextChannelList(DogCogConverter):
    @staticmethod
    async def parse(ctx: commands.GuildContext, argument: str) -> list[TEXT_TYPES]: ...
