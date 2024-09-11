import typing
import discord
from redbot.core.commands import commands, GuildContext

from ..core.converter import DogCogConverter

class UserList(DogCogConverter):
    @staticmethod
    async def parse(ctx: GuildContext, argument: str) -> typing.List[discord.User]: # type:ignore[override]
        members = ctx.guild.members
        args = argument.split()

        user_list : typing.List[discord.User] = [member._user for member in members if member.mention in args or member.id in args]
        args = [arg for arg in args if not arg in [user.mention for user in user_list]]

        if len(args) > 0:
            pruned_args = [
                id.replace("<", "").replace(">", "").replace("@", "") for id in args
            ]

            extra_users : typing.List[discord.User] = []

            for arg in pruned_args:
                try:
                    extra_users.append(await ctx.bot.fetch_user(int(arg)))
                except:
                    raise commands.BadArgument(f"No user was found for: {arg}")

            user_list.extend(extra_users)

        return user_list