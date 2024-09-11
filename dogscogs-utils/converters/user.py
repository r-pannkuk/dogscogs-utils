import typing
import discord
from redbot.core.commands import commands, GuildContext

from core.converter import DogCogConverter

class UserList(DogCogConverter):
    @staticmethod
    async def parse(ctx: GuildContext, argument: str) -> typing.List[discord.User]:
        users = ctx.guild.members
        args = argument.split()

        user_list = [user for user in users if user.mention in args or user.id in args]
        args = [arg for arg in args if not arg in [user.mention for user in user_list]]

        if len(args) > 0:
            pruned_args = [
                id.replace("<", "").replace(">", "").replace("@", "") for id in args
            ]
            extra_users = [await ctx.bot.fetch_user(arg) for arg in pruned_args]

            badUsers = []

            for i in range(len(extra_users)):
                user = extra_users[i]
                if user is None:
                    badUsers.append(args[i])
                else:
                    user_list.append(user)

            if len(badUsers) > 0:
                raise commands.BadArgument(
                    f"No user was found for: {','.join(badUsers)}"
                )

        return user_list