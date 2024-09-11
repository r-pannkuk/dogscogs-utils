import typing
import discord
from redbot.core import commands
from ..core.converter import DogCogConverter

class Mention(DogCogConverter):
    @staticmethod
    async def parse(ctx: commands.Context, input: str) -> typing.Union[discord.TextChannel, discord.Member, discord.Role]:
        converter: typing.Union[
            commands.TextChannelConverter,
            commands.MemberConverter,
            commands.RoleConverter,
        ]

        try:
            converter = commands.TextChannelConverter()
            return await converter.convert(ctx, input)
        except:
            pass

        try:
            converter = commands.MemberConverter()
            return await converter.convert(ctx, input)
        except:
            pass

        try:
            converter = commands.RoleConverter()
            return await converter.convert(ctx, input)
        except:
            raise commands.BadArgument("Not a valid mention.")
