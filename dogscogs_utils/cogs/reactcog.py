from enum import Flag, auto
import random
from types import SimpleNamespace
import typing
import discord
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from .dogcog import (
    DogCog,
    DEFAULT_GUILD as _DEFAULT_GUILD,
    Value,
    GuildConfig as _GuildConfig,
)
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config


MEMBER_NAME_TOKEN = "$MEMBER_NAME$"
SERVER_NAME_TOKEN = "$SERVER_NAME$"
MEMBER_COUNT_TOKEN = "$MEMBER_COUNT$"
ACTION_TOKEN = "$ACTION$"


def replace_tokens(
    text: str,
    member: discord.Member,
    use_mentions: typing.Optional[bool] = False,
    token: typing.Optional[str] = None,
):
    if token is not None:
        return text.replace(
            token,
        )
    return (
        text.replace(
            MEMBER_NAME_TOKEN,
            member.display_name if not use_mentions else member.mention,
        )
        .replace(SERVER_NAME_TOKEN, member.guild.name)
        .replace(MEMBER_COUNT_TOKEN, str(member.guild.member_count))
    )


class ReactType(Flag):
    MESSAGE = auto()
    JOIN = auto()
    KICK = auto()
    BAN = auto()
    LEAVE = auto()


class CooldownConfig(typing.TypedDict):
    mins: typing.Union[str, float]
    next: float


class EmbedConfig(typing.TypedDict):
    use_embed: bool
    title: typing.Optional[str]
    footer: typing.Optional[str]
    image_url: typing.Optional[str]


class TriggerConfig(typing.TypedDict):
    type: ReactType
    chance: typing.Union[str, float]
    list: typing.Optional[typing.List[str]]


class GuildConfig(_GuildConfig, typing.TypedDict):
    always_list: typing.Optional[typing.List[typing.Union[str, int]]]
    channel_ids: typing.Optional[typing.List[typing.Union[str, int]]]
    color: typing.Optional[
        typing.Tuple[
            typing.Annotated[int, "[0,255]"],
            typing.Annotated[int, "[0,255]"],
            typing.Annotated[int, "[0,255]"],
        ]
    ]
    cooldown: CooldownConfig
    embed: typing.Optional[EmbedConfig]
    messages: typing.List[str]
    name: str
    trigger: TriggerConfig


DEFAULT_GUILD: GuildConfig = {
    **_DEFAULT_GUILD,
    "always_list": [],
    "channel_ids": [],
    "color": discord.Color.lighter_grey().to_rgb(),
    "cooldown": {
        "mins": "1d30",
        "next": 0,
    },
    "embed": {
        "use_embed": True,
        "title": "",
        "footer": "",
        "image_url": ""
    },
    "messages": [],
    "name": "Greeting messages",
    "trigger": {"type": ReactType.MESSAGE, "chance": 1.0, "list": []},
}


class ReactCog(DogCog):
    def __int__(self, bot: Red) -> None:
        DogCog.__init__(self, bot)
        self.config.register_guild(**DEFAULT_GUILD)
        pass

    def _name(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[str]:
        """Returns the config name for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            str: The name config value.
        """
        return self._group_guild(guild=guild, ctx=ctx).name

    def _messages(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[typing.List[str]]:
        """Returns the config message list for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            list[str]: The messages config value.
        """
        return self._group_guild(guild=guild, ctx=ctx).messages

    def _always_list(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[typing.List[typing.Union[str, int]]]:
        """Returns the config always list for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            list[id]: The list of user ids in the always list.
        """
        return self._group_guild(guild=guild, ctx=ctx).always_list

    def _channel_ids(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[typing.List[typing.Union[str, int]]]:
        """Returns the list of channel ids to respond to for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            list[id]: The list of channel ids this cog should echo into.
        """
        return self._group_guild(guild=guild, ctx=ctx).channel_ids

    def _color(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[typing.Tuple[int, int, int]]:
        """Returns the color for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            Color: The color of embeds this cog uses.
        """
        return self._group_guild(guild=guild, ctx=ctx).color

    def _cooldown(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[CooldownConfig]:
        """Returns the cooldown object of this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            CooldownConfig: The cooldown parameters of this cog.
        """
        return self._group_guild(guild=guild, ctx=ctx).cooldown

    def _embed(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[EmbedConfig]:
        """Returns the embed object of this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            EmbedConfig: The embed parameters of this cog.
        """
        return self._group_guild(guild=guild, ctx=ctx).embed

    def _triggers(
        self,
        *,
        guild: typing.Optional[discord.Guild],
        ctx: typing.Optional[commands.Context],
    ) -> Value[TriggerConfig]:
        """Returns the trigger config for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            TriggerConfig: The list of user ids in the always list.
        """
        return self._group_guild(guild=guild, ctx=ctx).always_list

    async def toggle(self, ctx: commands.Context):
        return await DogCog.enable(ctx, not await self._enabled(ctx)())

    async def message_list(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.title = await self._title(ctx)()

        message_list = []
        messages: list[str] = await self._messages(ctx)()

        for i in range(len(messages)):
            message_list.append(f"[{i}] {messages[i]}")

        embed.description = "\n".join(message_list)

        return await ctx.send(embed=embed)

    async def message_add(self, ctx: commands.Context, str):
        messages: list[str] = await self._messages(ctx)()
        messages.append(str)
        await self._messages(ctx).set(messages)
        return await ctx.send(
            f"Added the following string to {await self._name(ctx)()}:\n{str}"
        )

    async def message_remove(self, ctx: commands.Context, int):
        messages: list[str] = await self._messages(ctx)()
        if int >= len(messages):
            raise commands.BadArgument("Couldn't find the message at the given index.")

        str = messages.pop(int)
        name = await self._name(ctx)()
        if len(messages) == 0:
            str += f"\n\nYou must have at least one message before {name} will fire."

        return await ctx.send(f"Removed the following string to {name}:\n{str}")

    async def list_channel(self, ctx: commands.Context):
        embed = discord.Embed()
        name = await self._name(ctx)()
        embed.title = f"Channels for {name.lower()}:"

        channels = []
        channel_ids = await self._channel_ids(ctx)()

        for i in range(len(channel_ids)):
            try:
                channel: discord.TextChannel = await self.bot.fetch_channel(
                    channel_ids[i]
                )
                channels.append(f"[{i}] {channel.mention}")
            except:
                channel_ids.remove(channel_ids[i])
                continue

        embed.description = "\n".join(channels)
        await self._channel_ids(ctx).set(channel_ids)
        return await ctx.send(embed=embed)

    async def add_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        channel_ids: list[str] = await self._channel_ids(ctx)()
        await self._channel_ids(ctx).set(list(set(channel_ids.append(channel.id))))
        await ctx.send(
            f"Added {channel.mention} to the {await self._name(ctx)()} channel list."
        )
        await self.list_channel(ctx)

    async def remove_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        channel_ids: list[str] = await self._channel_ids(ctx)()
        channel_ids.discard(channel.id)
        await ctx.send(
            f"Removed {channel.mention} from the {await self._name(ctx)()} channel list."
        )
        await self.list_channel(ctx)

    async def use_embed(
        self, ctx: commands.Context, bool: typing.Optional[bool] = None
    ):
        embed: EmbedConfig = await self._embed(ctx)()
        if bool is not None:
            embed["use_embed"] = bool
            await self._embed(ctx).set(embed)

        status_msg = ""

        if embed["use_embed"]:
            status_msg = "**RICH EMBED**"
        else:
            status_msg = "**SIMPLE**"

        return await ctx.send(
            f"Currently configured to use {status_msg} {await self._name(ctx)()}."
        )

    async def chance(
        self,
        ctx: commands.Context,
        chance: typing.Optional[typing.Union[float, str]] = None,
    ):
        triggers: TriggerConfig = await self._triggers(ctx)()

        if chance is not None:
            if chance <= 0 or chance > 1.0:
                raise commands.BadArgument("Chance must be between (0, 1]")

            triggers["chance"] = chance

            await self._triggers(ctx).set(triggers)

        if isinstance(triggers["chance"], float):
            chance_str = f"{triggers['chance'] * 100}%"
        else:
            chance_str = triggers["chance"]

        return await ctx.send(f"The chance to greet users set to {chance_str}.")

    async def image(self, ctx: commands.Context, url: typing.Optional[str] = None):
        embed: EmbedConfig = await self._embed(ctx)()
        prefix = "Currently"

        if url is not None:
            prefix = "Now"
            image_formats = ("image/png", "image/jpeg", "image/gif")
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
                }
                request = Request(url, headers=headers)
                site = urlopen(request)

                meta = site.info()  # get header of the http request

                if meta["content-type"] not in image_formats:
                    return await ctx.send("``ERROR: Given URL is not a valid image.``")
            except (HTTPError, ValueError) as e:
                return await ctx.send("``ERROR: Given parameter is not a valid url.``")

            embed["image_url"] = url
            await self._embed(ctx).set(embed)

        name = await self._name(ctx)()

        if embed["image_url"] is None or embed["image_url"] == "":
            return await ctx.send(
                f"{prefix} no image thumbnail is set for use with rich embed {name}."
            )
        else:
            return await ctx.send(
                f"{prefix} using the following image with rich embed {name}:\n{embed['image_url']}"
            )

    async def title(self, ctx: commands.Context, title: typing.Optional[str] = None):
        embed: EmbedConfig = await self._embed(ctx)()
        prefix = "Currently"

        if title is not None:
            prefix = "Now"
            embed["title"] = title
            await self._embed(ctx).set(embed)

        name = await self._name(ctx)()

        if embed["title"] is None or embed["title"] == "":
            return await ctx.send(
                f"{prefix} no title is set for use with rich embed {name}."
            )
        else:
            return await ctx.send(
                f"{prefix} using the following title with rich embed {name}:\n{embed['title']}"
            )

    async def footer(self, ctx: commands.Context, footer: typing.Optional[str] = None):
        embed: EmbedConfig = await self._embed(ctx)()
        prefix = "Currently"

        if footer is not None:
            prefix = "Now"
            embed["footer"] = footer
            await self._embed(ctx).set(embed)

        name = await self._name(ctx)()

        if embed["footer"] is None or embed["footer"] == "":
            return await ctx.send(
                f"{prefix} no footer is set for use with rich embed {name}."
            )
        else:
            return await ctx.send(
                f"{prefix} using the following footer with rich embed {name}:\n{embed['footer']}"
            )

    async def create_embed(
        self,
        ctx,
        *,
        channel: discord.TextChannel,
        member: discord.Member,
        action: typing.Optional[str],
        perp: typing.Optional[discord.Member],
        reason: typing.Optional[str],
    ):
        embed_config: EmbedConfig = self._embed(ctx)()
        embed = discord.Embed()

        embed.title = replace_tokens(embed_config["title"], member)
        embed.description = replace_tokens(
            random.choice(await self._messages(ctx)()), member
        )
        embed.colour = discord.Color.from_rgb(*embed["color"])

        if "footer" in embed_config and embed_config["footer"] != "":
            embed.set_footer(
                text=replace_tokens(embed_config["footer"], member),
                icon_url=member.avatar.url,
            )

        if "image_url" in embed_config and embed_config["image_url"] != "":
            embed.set_thumbnail(url=embed_config["image_url"])

        if action:
            embed.description = embed.description.replace(ACTION_TOKEN, action)
            embed.title = embed.title.replace(ACTION_TOKEN, action)

        if perp:
            embed.add_field(
                name=f"{action.capitalize()}ed by:",
                value=perp.mention,
                inline=True,
            )

            if reason:
                embed.add_field(name="Reason:", value=reason, inline=True)

        return await channel.send(embed=embed)

    async def create_simple(
        self, ctx, channel: discord.TextChannel, member: discord.Member
    ):
        embed_config: EmbedConfig = await self._embed(ctx)()
        title = replace_tokens(embed_config["title"], member, use_mentions=True)
        choice = replace_tokens(
            random.choice(await self._messages(ctx)()), member, use_mentions=True
        )
        return await channel.send(f"{title} {choice}")

    async def create(
        self,
        ctx,
        *,
        channel: discord.TextChannel,
        member: discord.Member,
        action: typing.Optional[str],
        perp: typing.Optional[discord.Member],
        reason: typing.Optional[str],
    ):
        messages: list[str] = await self._messages(ctx)()
        if len(messages) < 1:
            return

        embed_config: EmbedConfig = await self._embed(ctx)()

        if embed_config["use_embed"]:
            return await self.create_embed(ctx, channel, member, action, perp, reason)
        else:
            return await self.create_simple(ctx, channel, member)

    async def template(self, ctx: commands.Context, channel: discord.TextChannel):
        member = SimpleNamespace(
            **{
                "display_name": MEMBER_NAME_TOKEN,
                "guild": SimpleNamespace(
                    **{"name": SERVER_NAME_TOKEN, "member_count": MEMBER_COUNT_TOKEN}
                ),
                "avatar_url": self.bot.user.avatar.url,
                "mention": "$MEMBER_MENTION$",
            }
        )
        return await self.create(ctx, channel, member)
