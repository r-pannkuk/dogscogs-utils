from datetime import datetime, timedelta
import typing
import discord
import pytz


async def get_audit_log_reason(
    guild: discord.Guild,
    target: typing.Union[discord.abc.GuildChannel, discord.Member, discord.Role],
    action: discord.AuditLogAction,
) -> typing.Tuple[typing.Optional[discord.abc.User], typing.Optional[str]]:
    perp = None
    reason = None
    if guild.me.guild_permissions.view_audit_log:
        async for log in guild.audit_logs(limit=5, action=action):
            if (
                log.target
                and log.target.id == target.id
                and (log.created_at > (datetime.now(tz=pytz.timezone("UTC")) - timedelta(0, 5)))
            ):
                perp = log.user
                if log.reason:
                    reason = log.reason
                break
    return perp, reason
