from contextlib import suppress
from datetime import datetime, timedelta
from enum import UNIQUE, StrEnum, verify
import re
import typing
import discord
import pytz


@verify(UNIQUE)
class Token(StrEnum):
    MemberName = "$MEMBER_NAME$"
    ServerName = "$SERVER_NAME$"
    MemberCount = "$MEMBER_COUNT$"
    Action = "$ACTION$"
    InstigatorName = "$INSTIGATOR_NAME$"
    Context = "$CONTEXT$"
    Param = "$PARAM$"
    ReactToken = f"react({Param})"
    WeightToken = f"weight({Param})"

ActionType = typing.Literal["joined", "was banned", "was kicked", "left"]

class MessageOptions(typing.TypedDict, total=False):
    content: typing.Optional[str]
    embed: typing.Optional[discord.Embed]
    reactions: typing.Optional[typing.List[typing.Union[discord.Emoji, str]]]

def replace_tokens(
    text: str,
    *,
    member: typing.Optional[discord.Member] = None,
    guild: typing.Optional[discord.Guild] = None,
    action: typing.Optional[ActionType] = None,
    instigator: typing.Optional[discord.Member] = None,
    context: typing.Optional[str] = None,
    use_mentions: typing.Optional[bool] = False,
):
    if member is not None:
        text = text.replace(
                Token.MemberName.value,
                member.display_name if not use_mentions else member.mention,
            )
    if guild is not None:
        text = text.replace(Token.ServerName.value, guild.name)
        text = text.replace(Token.MemberCount.value, str(guild.member_count))
        emoji_matches = re.findall(r"[:][a-zA-Z0-9_]+[:]", text)

        for match in emoji_matches:
            emoji_name = match[1:-1]
            with suppress(discord.errors.HTTPException):
                emoji = discord.utils.get(guild.emojis, name=emoji_name)
                if emoji is not None:
                    text = text.replace(match, str(emoji))
        
    if action is not None:
        text = text.replace(Token.Action.value, action)
    if instigator is not None:
        text = text.replace(
            Token.InstigatorName.value,
            instigator.display_name if not use_mentions else instigator.mention,
        )
    if context is not None:
        text = text.replace(Token.Context.value, context)

    return text