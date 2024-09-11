from enum import Enum
import typing
import discord


class Embed(typing.TypedDict):
    MAX_DESCRIPTION_LENGTH = 2048


class Message(typing.TypedDict):
    MAX_CONTENT_LENGTH = 2000


class User(typing.TypedDict):
    MAX_NAME_LENGTH = 32


class Emoji(typing.TypedDict):
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 32


class Channel(typing.TypedDict):
    TEXT_TYPES = typing.Union[discord.TextChannel, discord.Thread]
