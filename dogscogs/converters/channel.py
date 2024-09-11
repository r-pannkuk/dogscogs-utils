import typing
from redbot.core import commands

from ..constants.discord.channel import TEXT_TYPES

from ..core.converter import DogCogConverter

class ListChannelsText(DogCogConverter):
    @staticmethod
    async def parse(ctx: commands.GuildContext, argument: str) -> typing.List[TEXT_TYPES]: # type:ignore[override]
        channels = ctx.guild.channels
        args = argument.split()

        channel_list = [
            channel
            for channel in channels
            if channel.mention in args or channel.id in args
        ]
        args = [
            arg
            for arg in args
            if not arg in [channel.mention for channel in channel_list]
        ]

        if len(args) > 0:
            raise commands.BadArgument(f"No channels were found for: {','.join(args)}")

        bad_channels = [
            channel.mention
            for channel in channel_list
            if not isinstance(channel, TEXT_TYPES) 
        ]

        if len(bad_channels) > 0:
            raise commands.BadArgument(
                f"Can't read messages for {','.join(bad_channels)}"
            )

        return channel_list # type: ignore[return-value]