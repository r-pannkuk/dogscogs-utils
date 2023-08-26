from datetime import datetime, timedelta
from enum import Flag, auto
import random
from types import SimpleNamespace
import typing
import discord
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import d20

from redbot.core import commands
from redbot.core.bot import Red

from dogscogs_utils.adapters.converters import Percent

from .dogcog import (
    DogCog,
    Value,
    GuildConfig as _GuildConfig,
)
from ..adapters.parsers import Token, get_audit_log_reason, replace_tokens


class ReactType(Flag):
    MESSAGE = auto()
    JOIN = auto()
    KICK = auto()
    BAN = auto()
    LEAVE = auto()


class CooldownConfig(typing.TypedDict):
    mins: typing.Union[str, float]
    next: float
    last_timestamp: float


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


class ReactCog(DogCog):
    DefaultConfig: GuildConfig = {
        **DogCog.DefaultConfig,
        "always_list": [],
        "channel_ids": [],
        "color": discord.Color.lighter_grey().to_rgb(),
        "cooldown": {
            "mins": "1d30",
            "next": 0,
        },
        "embed": {"use_embed": True, "title": "", "footer": "", "image_url": ""},
        "messages": [],
        "name": "Greeting messages",
        "trigger": {"type": ReactType.MESSAGE, "chance": 1.0, "list": []},
    }

    TRIGGER_LENGTH_LIMIT = 6

    def __int__(self, bot: Red) -> None:
        super().__init__(bot)
        self.config.register_guild(**ReactCog.DefaultConfig)
        self._ban_cache = {}

        bot.add_listener(func=self.on_message, name="on_message")
        bot.add_listener(func=self.on_member_ban, name="on_member_ban")
        bot.add_listener(func=self.on_member_unban, name="on_member_unban")
        bot.add_listener(func=self.on_member_join, name="on_member_join")
        bot.add_listener(func=self.on_member_remove, name="on_member_remove")

        pass

    def _name(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[str]:
        """Returns the config name for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            str: The name config value.
        """
        if guild is None and ctx is None:
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")
            
        return self._group_guild(guild=guild, ctx=ctx).name

    def _messages(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[typing.List[str]]:
        """Returns the config message list for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            list[str]: The messages config value.
        """
        if guild is None and ctx is None:
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")

        return self._group_guild(guild=guild, ctx=ctx).messages

    def _always_list(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[typing.List[typing.Union[str, int]]]:
        """Returns the config always list for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            list[id]: The list of user ids in the always list.
        """
        if guild is None and ctx is None:
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")

        return self._group_guild(guild=guild, ctx=ctx).always_list

    def _channel_ids(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[typing.List[typing.Union[str, int]]]:
        """Returns the list of channel ids to respond to for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            list[id]: The list of channel ids this cog should echo into.
        """
        if guild is None and ctx is None:
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")
        
        return self._group_guild(guild=guild, ctx=ctx).channel_ids

    def _color(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[typing.Tuple[int, int, int]]:
        """Returns the color for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            Color: The color of embeds this cog uses.
        """
        if guild is None and ctx is None:
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")

        return self._group_guild(guild=guild, ctx=ctx).color

    def _cooldown(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[CooldownConfig]:
        """Returns the cooldown object of this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            CooldownConfig: The cooldown parameters of this cog.
        """
        if guild is None and ctx is None:
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")

        return self._group_guild(guild=guild, ctx=ctx).cooldown

    def _embed(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[EmbedConfig]:
        """Returns the embed object of this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            EmbedConfig: The embed parameters of this cog.
        """
        if guild is None and ctx is None:
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")

        return self._group_guild(guild=guild, ctx=ctx).embed

    def _triggers(
        self,
        *,
        guild: typing.Optional[discord.Guild] = None,
        ctx: typing.Optional[commands.Context] = None,
    ) -> Value[TriggerConfig]:
        """Returns the trigger config for this cog.

        Args:
            guild (typing.Optional[discord.Guild]): (Optional) The guild.
            ctx (typing.Optional[commands.Context]): (Optional) The command context.

        Returns:
            TriggerConfig: The list of user ids in the always list.
        """
        if guild is None and ctx is None:
            raise commands.BadArgument("Must provide either `guild` or `ctx` to call.")

        return self._group_guild(guild=guild, ctx=ctx).always_list

    async def toggle(self, ctx: commands.Context):
        """Toggles the functionality of this trigger on or off."""
        return await DogCog.enable(ctx, not await self._enabled(ctx=ctx)())

    async def message_list(self, ctx: commands.Context):
        """Lists all of the messages that have a chance to be said in response to triggers."""
        embed = discord.Embed()
        embed.title = self._name(ctx=ctx)()

        message_list = []
        messages: list[str] = await self._messages(ctx=ctx)()

        for i in range(len(messages)):
            message_list.append(f"[{i}] {messages[i]}")

        embed.description = "\n".join(message_list)

        return await ctx.send(embed=embed)

    async def message_add(self, ctx: commands.Context, msg: str):
        """Adds a new hello message for use in the server.  Use the following escaped strings for values:
        -- ``{Token.MemberName}`` - The target member's name
        -- ``{Token.MemberName}`` - The server name
        -- ``{Token.MemberName}`` - The server member count

        Args:
        \t\tentry (str): The new hello message to be used at random.
        """
        messages: list[str] = await self._messages(ctx=ctx)()
        messages.append(msg)
        await self._messages(ctx=ctx).set(messages)
        return await ctx.send(
            f"Added the following string to {await self._name(ctx=ctx)()}:\n{msg}"
        )

    async def message_remove(self, ctx: commands.Context, index: int):
        """Removes a trigger response message.

        Args:
            index (int): The index of the message to remove.

        Raises:
            commands.BadArgument: If the index is out of range.
        """
        messages: list[str] = await self._messages(ctx=ctx)()
        if index >= len(messages):
            raise commands.BadArgument("Couldn't find the message at the given index.")

        str = messages.pop(index)
        name = await self._name(ctx=ctx)()
        if len(messages) == 0:
            str += f"\n\nYou must have at least one message before {name} will fire."

        return await ctx.send(f"Removed the following string to {name}:\n{str}")

    async def list_channel(self, ctx: commands.Context):
        """Lists all channels that triggers will respond to."""
        embed = discord.Embed()
        name = await self._name(ctx=ctx)()
        embed.title = f"Channels for {name.lower()}:"

        channels = []
        channel_ids = await self._channel_ids(ctx=ctx)()

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
        await self._channel_ids(ctx=ctx).set(channel_ids)
        return await ctx.send(embed=embed)

    async def add_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Adds a channel to the list of trigger channels.

        Args:
            channel (discord.TextChannel): The channel to add for triggering in.
        """
        channel_ids: list[str] = await self._channel_ids(ctx=ctx)()
        await self._channel_ids(ctx=ctx).set(list(set(channel_ids.append(channel.id))))
        await ctx.send(
            f"Added {channel.mention} to the {await self._name(ctx=ctx)()} channel list."
        )
        await self.list_channel(ctx)

    async def remove_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Removes a channel from the list of trigger channels.

        Args:
            channel (discord.TextChannel): The channel to respond with triggers in.
        """
        channel_ids: list[str] = await self._channel_ids(ctx=ctx)()
        channel_ids.discard(channel.id)
        await ctx.send(
            f"Removed {channel.mention} from the {await self._name(ctx=ctx)()} channel list."
        )
        await self.list_channel(ctx)

    async def use_embed(
        self, ctx: commands.Context, bool: typing.Optional[bool] = None
    ):
        """Sets whether or not to use Rich Embeds for trigger messages.

        Args:
            bool (bool, optional): Whether or not to use Rich Embeds.
        """
        embed: EmbedConfig = await self._embed(ctx=ctx)()
        if bool is not None:
            embed["use_embed"] = bool
            await self._embed(ctx=ctx).set(embed)

        status_msg = ""

        if embed["use_embed"]:
            status_msg = "**RICH EMBED**"
        else:
            status_msg = "**SIMPLE**"

        return await ctx.send(
            f"Currently configured to use {status_msg} {await self._name(ctx=ctx)()}."
        )

    async def image(self, ctx: commands.Context, url: typing.Optional[str] = None):
        """Sets the image used with the trigger response.

        Args:
            url (str, optional): The image to use in response messages. Defaults to None.
        """
        embed: EmbedConfig = await self._embed(ctx=ctx)()
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
            await self._embed(ctx=ctx).set(embed)

        name = await self._name(ctx=ctx)()

        if embed["image_url"] is None or embed["image_url"] == "":
            return await ctx.send(
                f"{prefix} no image thumbnail is set for use with rich embed {name}."
            )
        else:
            return await ctx.send(
                f"{prefix} using the following image with rich embed {name}:\n{embed['image_url']}"
            )

    async def title(self, ctx: commands.Context, title: typing.Optional[str] = None):
        """Sets the response message title for the trigger action.

        Args:
            title (str): (Optional) The string for the title to be set to.
        """
        embed: EmbedConfig = await self._embed(ctx=ctx)()
        prefix = "Currently"

        if title is not None:
            prefix = "Now"
            embed["title"] = title
            await self._embed(ctx=ctx).set(embed)

        name = await self._name(ctx=ctx)()

        if embed["title"] is None or embed["title"] == "":
            return await ctx.send(
                f"{prefix} no title is set for use with rich embed {name}."
            )
        else:
            return await ctx.send(
                f"{prefix} using the following title with rich embed {name}:\n{embed['title']}"
            )

    async def footer(self, ctx: commands.Context, footer: typing.Optional[str] = None):
        """Sets the footer string for the trigger response.

        Args:
            footer (str): (Optional) The footer to provide.
        """
        embed: EmbedConfig = await self._embed(ctx=ctx)()
        prefix = "Currently"

        if footer is not None:
            prefix = "Now"
            embed["footer"] = footer
            await self._embed(ctx=ctx).set(embed)

        name = await self._name(ctx=ctx)()

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
        *,
        channel: discord.TextChannel,
        member: discord.Member,
        action: typing.Optional[str] = None,
        perp: typing.Optional[discord.Member] = None,
        reason: typing.Optional[str] = None,
    ):
        """Creates a rich embed to send for the trigger action.

        Args:
            channel (discord.TextChannel): The channel to send to
            member (discord.Member): The triggering user
            action (str): (Optional) The trigger action.
            perp (discord.Member): (Optional) The perpetrator user.
            reason (str): (Optional) The reason for the trigger.
        """
        guild = channel.guild
        embed_config: EmbedConfig = self._embed(guild=guild)()
        embed = discord.Embed()

        embed.title = replace_tokens(embed_config["title"], member)
        embed.description = replace_tokens(
            random.choice(await self._messages(guild=guild)()), member
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
            embed.description = embed.description.replace(Token.Action, action)
            embed.title = embed.title.replace(Token.Action, action)

        if perp:
            embed.add_field(
                name=f"{action.capitalize()} by:",
                value=perp.mention,
                inline=True,
            )

            if reason:
                embed.add_field(name="Reason:", value=reason, inline=True)

        return await channel.send(embed=embed)

    async def create_simple(
        self, *, channel: discord.TextChannel, member: discord.Member
    ):
        """Creates a simple text message for the trigger action.

        Args:
            channel (discord.TextChannel): The channel to send to.
            member (discord.Member): The triggering user.
        """
        guild = channel.guild
        embed_config: EmbedConfig = await self._embed(guild=guild)()
        title = replace_tokens(embed_config["title"], member, use_mentions=True)
        choice = replace_tokens(
            random.choice(await self._messages(guild=guild)()), member, use_mentions=True
        )
        return await channel.send(f"{title} {choice}")

    async def create(
        self,
        *,
        channel: discord.TextChannel,
        member: discord.Member,
        action: typing.Optional[str] = None,
        perp: typing.Optional[discord.Member] = None,
        reason: typing.Optional[str] = None,
    ):
        """Creates a trigger message.

        Args:
            channel (discord.TextChannel): The channel to post it in.
            member (discord.Member): The member who triggered.
            action (str): (Optional) The action of the trigger.
            perp (discord.Member): (Optional) The perpetrator of the trigger.
            reason (str): (Optional) The reason for the trigger.
        """
        guild = channel.guild
        messages: list[str] = await self._messages(guild=guild)()
        if len(messages) < 1:
            return

        embed_config: EmbedConfig = await self._embed(guild=guild)()

        if embed_config["use_embed"]:
            return await self.create_embed(channel=channel, member=member, action=action, perp=perp, reason=reason)
        else:
            return await self.create_simple(channel=channel, member=member)

    async def template(self, ctx: commands.Context, channel: discord.TextChannel):
        """Creates a template based off the given configuration.

        Args:
            channel (discord.TextChannel): The text channel to send it to.
        """
        member = SimpleNamespace(
            **{
                "display_name": Token.MemberName,
                "guild": SimpleNamespace(
                    **{"name": Token.ServerName, "member_count": Token.MemberCount}
                ),
                "avatar_url": self.bot.user.display_avatar.url,
                "mention": "$MEMBER_MENTION$",
            }
        )
        return await self.create(channel=channel, member=member)

    async def chance(
        self,
        ctx: commands.Context,
        chance: typing.Optional[Percent] = None,
    ):
        """Sets the random chance that the greeter will go off.

        Args:
            chance (float | Percentage): A percent between 0.00 and 1.00 or 0% and 100%
        """
        triggers: TriggerConfig = await self._triggers(ctx=ctx)()

        if chance is not None:
            triggers["chance"] = chance

            await self._triggers(ctx=ctx).set(triggers)

        if isinstance(triggers["chance"], float):
            chance_str = f"{triggers['chance'] * 100}%"
        else:
            chance_str = triggers["chance"]

        return await ctx.send(f"The chance to greet users set to {chance_str}.")

    async def cooldown(self, ctx: commands.Context, *, cooldown: typing.Optional[str] = None):
        """Sets the cooldown used by the greeter.

        Args:
            cooldown (str): The cooldown amount; either a number or an RNG dice amount (1d30 for random within 30 minutes).
        """
        cooldown_config: CooldownConfig = await self._cooldown(ctx=ctx)()

        if cooldown is not None:
            try:
                parsed = d20.parse(cooldown)
            except d20.RollSyntaxError as e:
                await ctx.send(
                    "ERROR: Please enter a valid cooldown using dice notation or a number."
                )
                return

            cooldown_config["mins"] = cooldown

            # Moving the cooldown to whatever the new amount is.
            if cooldown_config["next"] > datetime.now().timestamp():
                cooldown_config["next"] = (
                    datetime.fromtimestamp(cooldown_config["last_timestamp"])
                    + timedelta(minutes=d20.roll(cooldown).total)
                ).timestamp()

            await self._cooldown(ctx=ctx).set(cooldown_config)

            await ctx.send(f"Set the cooldown to greet users to {cooldown} minutes.")
        else:
            await ctx.send(
                f"The chance to greet users is currently {cooldown_config['mins']} minutes."
            )
        pass

    async def always_list(self, ctx: commands.Context):
        """Gets the list of random hello messages for the server."""
        always_list: typing.List[typing.Union[str, int]] = self._always_list(ctx=ctx)()
        guild: discord.Guild = ctx.guild
        embed = discord.Embed()
        embed.title = f"Always triggered on the following users:"

        users = []

        for i in range(len(always_list)):
            member: discord.Member = guild.get_member(always_list[i])

            if member is None:
                continue

            users.append(f"[{i}] {member.mention}")

        embed.description = "\n".join(users)

        await ctx.send(embed=embed)
        pass

    async def always_add(self, ctx: commands.Context, *, member: discord.Member):
        """Adds a user to always have hello messages sent to them.

        Args:
            member (discord.Member): The member to always greet.
        """
        always_list: typing.List[typing.Union[str, int]] = self._always_list(ctx=ctx)()

        if member.id in always_list:
            await ctx.send(
                f"{member.display_name} is already always triggering on **{await self._name(ctx=ctx)().upper()}**."
            )
            return

        always_list.append(member.id)
        await self._always_list(ctx=ctx).set(always_list)
        await ctx.send(
            f"Added user {member.display_name} to the **{await self._name(ctx=ctx)().upper()}** always triggers list."
        )
        pass

    async def always_remove(self, ctx: commands.Context, *, member: discord.Member):
        """Removes a user from always being greeted.

        Args:
            member (discord.Member): The member to remove.
        """
        always_list: typing.List[typing.Union[str, int]] = self._always_list(ctx=ctx)()

        if member.id not in always_list:
            await ctx.send(
                f"{member.display_name} is not triggering on **{await self._name(ctx=ctx)().upper()}**."
            )
            return

        always_list.remove(member.id)
        await self._always_list(ctx=ctx).set(always_list)
        await ctx.send(
            f"Removed {member.display_name} from the **{await self._name(ctx=ctx)().upper()}** always trigger list."
        )
        pass

    async def triggers_list(self, ctx: commands.Context):
        """Gets the list of random hello messages for the server."""
        trigger_config: TriggerConfig = self._triggers(ctx=ctx)()
        embed = discord.Embed()
        embed.title = f"**{await self._name(ctx=ctx)().upper}** Trigger Phrases:"

        phrases = []

        trigger_list = trigger_config["list"]

        for i in range(len(trigger_list)):
            phrase = trigger_list[i]

            phrases.append(f"[{i}] {phrase}")

        embed.description = "\n".join(phrases)

        await ctx.send(embed=embed)
        pass

    async def triggers_add(self, ctx: commands.Context, *, phrase: str):
        """Adds a phrase which will trigger Hello messages.

        Args:
            phrase (str): The phrase to add for triggering.
        """
        trigger_config: TriggerConfig = self._triggers(ctx=ctx)()
        trigger_list = trigger_config["list"]

        if phrase.lower() in trigger_list:
            await ctx.send(
                f"``{phrase}`` is already triggering for **{await self._name(ctx=ctx)().upper}**."
            )
            return

        trigger_list.append(phrase.lower())
        trigger_config["list"] = trigger_list
        await self._triggers(ctx=ctx).set(trigger_config)
        await ctx.send(
            f"Added ``{phrase}`` to the list of **{await self._name(ctx=ctx)().upper}** triggers."
        )
        pass

    async def triggers_remove(
        self, ctx: commands.Context, *, phrase: typing.Union[str, int]
    ):
        """Removes a phrase from triggering hello messages.

        Args:
            phrase (str | int): The triggering phrase.
        """
        trigger_config: TriggerConfig = self._triggers(ctx=ctx)()
        trigger_list = trigger_config["list"]

        if isinstance(phrase, int):
            if phrase >= len(trigger_list):
                await ctx.send(f"``{phrase}`` is out of range.")
                return

            removed_phrase = trigger_list.pop(phrase)
        else:
            if phrase.lower() not in trigger_list:
                await ctx.send(
                    f"``{phrase}`` is not on the **{await self._name(ctx=ctx)().upper}** triggers list."
                )
                return

            removed_phrase = trigger_list.remove(phrase.lower())

        trigger_list.append(phrase.lower())
        trigger_config["list"] = trigger_list
        await self._triggers(ctx=ctx).set(trigger_config)

        await ctx.send(
            f"Removed ``{removed_phrase}`` from the list of triggers for **{await self._name(ctx=ctx)().upper}**."
        )
        pass

    async def create_if_enabled(
        self,
        *,
        member: discord.Member,
        action: typing.Optional[str] = None,
        perp: typing.Optional[discord.Member] = None,
        reason: typing.Optional[str] = None,
    ):
        guild = member.guild
        if not await self._enabled(guild=guild)():
            return

        if action is None:
            action = await self._name(guild=guild)()

        channel_ids = await self._channel_ids(guild=guild)()
        for channel_id in channel_ids:
            channel = guild.get_channel(channel_id)

            if channel is not None:
                await self.create(
                    channel,
                    member,
                    action,
                    perp,
                    reason,
                )

    ###########################################################################################################
    #                                                Listeners                                                #
    ###########################################################################################################

    async def on_member_join(self, member: discord.Member):
        """Fires greeting messages if enabled.

        __Args__:
            member (discord.Member): Affected member.
        """
        if member.bot:
            return

        await self.create_if_enabled(member=member)

        pass

    async def on_member_remove(self, member: discord.Member):
        """Fires departure or kick / ban messages if enabled.

        __Args__:
            member (discord.Member): Affected member.
        """
        guild = member.guild

        if member.bot:
            return

        if guild.id in self._ban_cache and member.id in self._ban_cache[guild.id]:
            perp, reason = await get_audit_log_reason(
                guild, member, discord.AuditLogAction.ban
            )
        else:
            perp, reason = await get_audit_log_reason(
                guild, member, discord.AuditLogAction.kick
            )

        if perp is not None:
            if guild.id in self._ban_cache and member.id in self._ban_cache[guild.id]:
                action = "banned"
                pass
            else:
                action = "kicked"
                pass

            await self.create_if_enabled(member=member, action=action, perp=perp, reason=reason)
        else:
            await self.create_if_enabled(member=member)
        pass

    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        """
        This is only used to track that the user was banned and not kicked/removed
        """
        if guild.id not in self._ban_cache:
            self._ban_cache[guild.id] = [member.id]
        else:
            self._ban_cache[guild.id].append(member.id)

    async def on_member_unban(self, guild: discord.Guild, member: discord.Member):
        """
        This is only used to track that the user was banned and not kicked/removed
        """
        if guild.id in self._ban_cache:
            if member.id in self._ban_cache[guild.id]:
                self._ban_cache[guild.id].remove(member.id)

    async def on_message(self, message: discord.Message):
        """Listens for hello triggers and rolls a chance to trigger a response.

        Args:
            message (discord.Message): The discord message listened to.
        """
        guild = message.guild

        if not await self._enabled(guild=guild)():
            return

        if message.author.bot:
            return

        prefix = await self.bot.get_prefix(message)

        if isinstance(prefix, str):
            if message.content.startswith(prefix):
                return
        else:
            if any(message.content.startswith(p) for p in prefix):
                return

        content = message.content.lower().split()
        trigger_config: TriggerConfig = self._triggers(guild=guild)()
        always_list: typing.List[typing.Union[str, int]] = self._always_list(guild=guild)()
        cooldown_config: CooldownConfig = self._cooldown(guild=guild)()

        if (
            any(
                [t in content and content.index(t) > -1 for t in trigger_config["list"]]
            )
            and len(content.split()) < ReactCog.TRIGGER_LENGTH_LIMIT
        ):
            if (
                message.author.id in always_list
                and (datetime.now() - timedelta(minutes=1)).timestamp()
                > cooldown_config["last_timestamp"]
            ):
                is_firing = True
            else:
                is_firing = (
                    random.random() < trigger_config["chance"]
                    and datetime.now().timestamp() > cooldown_config["next"]
                )

            if is_firing:
                await self.create(channel=message.channel, member=message.author)

                cooldown_config["next"] = (
                    datetime.now()
                    + timedelta(minutes=d20.roll(cooldown_config["mins"]).total)
                ).timestamp()

                cooldown_config["last_timestamp"] = datetime.now().timestamp()

                await self._cooldown(guild=guild).set(cooldown_config)
        pass
