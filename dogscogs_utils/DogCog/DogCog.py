import typing
from typing import Union
import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config, Group as _Group, Value as _Value


class GuildConfig(typing.TypedDict):
    is_enabled: bool


DEFAULT_GUILD: GuildConfig = {"is_enabled": True}

ValueType = typing.TypeVar("ValueType")
GroupType = typing.TypeVar("GroupType", discord.Guild, discord.TextChannel, discord.User, discord.Member, discord.Role)
ConfigType = typing.TypeVar("ConfigType", bound="GuildConfig")


class Value(typing.Generic[ValueType], _Value):
    """Type wrapper for generic config Value types."""

    def __call__(self, default=..., *, acquire_lock: bool = True) -> ValueType:
        return _Value.__call__(self, default, acquire_lock)

    async def set(self, value: ValueType) -> None:
        return _Value.set(self, value)


class Group(typing.Generic[GroupType, ConfigType], _Group):
    def __init__(self, **args):
        super().__init__(self, **args)

    def __getattr__(self, item: str) -> Value:
        return super().__getattr__(item)


class DogCog(commands.Cog):
    """Generic cog for Dog Cog development."""

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=260288776360820736,
            force_registration=True,
        )

    def _group_guild(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Group[discord.Guild, GuildConfig]:
        """Returns the guild config for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            Group: Group config for the guild.
        """
        return self.config.guild(guild | ctx.guild)

    def _enabled(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[bool]:
        """Returns whether or not this cog is enabled in the config.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            Value[bool]: The enabled value of the config.
        """
        return self._group_guild(guild=guild, ctx=ctx).is_enabled

    async def enabled(self, ctx: commands.Context, is_enabled: typing.Optional[bool]):
        """Enables or disables the cog.

        Args:
            is_enabled (typing.Optional[bool]): (Optional) Whether or not to enable this.
        """
        if is_enabled is None:
            is_enabled = await self._enabled(ctx)

        status_msg = ""

        if is_enabled:
            status_msg = "**ENABLED**"
        else:
            status_msg = "**DISABLED**"

        await self._enabled(ctx).set(is_enabled)

        await ctx.send(f"{self.__class__.__name__} is currently {status_msg}.")

        pass

    async def enable(self, ctx: commands.Context):
        """Enables this cog."""
        await self.enabled(ctx, True)
        pass

    async def disable(self, ctx: commands.Context):
        """Disables this cog."""
        await self.enabled(ctx, False)
        pass

    async def test(self) -> int:
        return
