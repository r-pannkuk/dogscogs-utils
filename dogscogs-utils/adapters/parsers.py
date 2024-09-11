from datetime import datetime, timedelta
from enum import UNIQUE, StrEnum, verify
import typing
import discord
import pytz


@verify(UNIQUE)
class Token(StrEnum):
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
            Token.MemberName.value,
            member.display_name if not use_mentions else member.mention,
        )
        .replace(Token.ServerName.value, member.guild.name)
        .replace(Token.MemberCount.value, str(member.guild.member_count))
    )


async def get_audit_log_reason(
    guild: discord.Guild,
    target: typing.Union[discord.abc.GuildChannel, discord.Member, discord.Role],
    action: discord.AuditLogAction,
) -> typing.Tuple[typing.Optional[discord.abc.User], typing.Optional[str]]:
    perp = None
    reason = None
    if guild.me.guild_permissions.view_audit_log:
        async for log in guild.audit_logs(limit=5, action=action):
            if log.target.id == target.id and (
                log.created_at
                > (datetime.now(tz=pytz.timezone("UTC")) - timedelta(0, 5))
            ):
                perp = log.user
                if log.reason:
                    reason = log.reason
                break
    return perp, reason
