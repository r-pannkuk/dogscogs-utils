import discord
from datetime import datetime as datetime, timedelta as timedelta
from enum import StrEnum

class Token(StrEnum):
    MemberName = '$MEMBER_NAME$'
    ServerName = '$SERVER_NAME$'
    MemberCount = '$MEMBER_COUNT$'
    Action = '$ACTION$'

def replace_tokens(text: str, member: discord.Member, use_mentions: bool | None = False, token: str | None = None): ...
