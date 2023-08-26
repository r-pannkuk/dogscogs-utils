from enum import UNIQUE, Enum, verify
import typing
import discord

@verify(UNIQUE)
class Token(Enum):
    MemberName = "$MEMBER_NAME$"
    ServerName = "$SERVER_NAME$"
    MemberCount = "$MEMBER_COUNT$"
    Action = "$ACTION$"

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
            Token.MemberName,
            member.display_name if not use_mentions else member.mention,
        )
        .replace(Token.ServerName, member.guild.name)
        .replace(Token.MemberCount, str(member.guild.member_count))
    )