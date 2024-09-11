import typing
import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config, Group as _Group, Value as _Value
from abc import ABCMeta, ABC

COG_IDENTIFIER = 260288776360820736

class GuildConfig(typing.TypedDict):
    is_enabled: bool

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

    DefaultConfig : GuildConfig = {
        "is_enabled": True
    }

    def __init__(self, bot: Red) -> None:
        self.bot = bot

    def _group_guild(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Group[discord.Guild, GuildConfig]:
        """Returns the guild config for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            Group: Group config for the guild.
        """
        if guild is None and (ctx is None or ctx.guild is None):
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")
        
        return self.config.guild(guild or ctx.guild)

    def _enabled(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[bool]:
        """Returns whether or not this cog is enabled in the config.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            Value[bool]: The enabled value of the config.
        """
        if guild is None and (ctx is None or ctx.guild is None):
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")
        
        return self._group_guild(guild=guild, ctx=ctx).is_enabled
    
    async def clear_all(
        self, ctx: commands.Context, verbose: typing.Optional[bool] = True
    ):
        """Clears all data. WARNING: Irreversible.

        Args:
            verbose (typing.Optional[bool], optional): Verbose output. Defaults to True.
        """
        guild: discord.Guild = ctx.guild
        await self.config.guild(guild).clear()
        if verbose:
            await ctx.send(f"Data cleared for {guild.name}.")

    async def clear_specific(
        self,
        ctx: commands.Context,
        config_type: str,
        verbose: typing.Optional[bool] = True,
    ):
        """Clears specific data for a config. WARNING: Irreversible.

        Args:
            config (str): The type of config to clear.
        """
        config_type = config_type.lower()

        if config_type not in DogCog.DefaultConfig.keys():
            await ctx.send(
                f"Invalid config type provided, please choose from: `{DogCog.DefaultConfig.keys()}`"
            )
            return

        guild: discord.Guild = ctx.guild
        config = DogCog.DefaultConfig[config_type]
        await self.config.guild(guild).get_attr(config_type).set(config)
        if verbose:
            await ctx.send(f"Data reset for {config_type} in {guild.name}.")

    async def enabled(self, ctx: commands.Context, is_enabled: typing.Optional[bool]):
        """Enables or disables the cog.

        Args:
            is_enabled (typing.Optional[bool]): (Optional) Whether or not to enable this.
        """
        if is_enabled is None:
            is_enabled = await self._enabled(ctx=ctx)()

        status_msg = ""

        if is_enabled:
            status_msg = "**ENABLED**"
        else:
            status_msg = "**DISABLED**"

        await self._enabled(ctx=ctx).set(is_enabled)

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