import discord
import typing
from _typeshed import Incomplete
from datetime import datetime as datetime, timedelta as timedelta
from enum import StrEnum

class Token(StrEnum):
    MemberName = '$MEMBER_NAME$'
    ServerName = '$SERVER_NAME$'
    MemberCount = '$MEMBER_COUNT$'
    Action = '$ACTION$'
    InstigatorName = '$INSTIGATOR_NAME$'
    Context = '$CONTEXT$'
    Param = '$PARAM$'
    ReactToken = ...
    WeightToken = ...

ActionType: Incomplete

class MessageOptions(typing.TypedDict, total=False):
    content: str | None
    embed: discord.Embed | None
    reactions: list[discord.Emoji | str] | None

def replace_tokens(text: str, *, member: discord.Member | None = None, guild: discord.Guild | None = None, action: ActionType | None = None, instigator: discord.Member | None = None, context: str | None = None, use_mentions: bool | None = False): ...
