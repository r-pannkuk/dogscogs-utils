import discord

class MessageUpdateEvent(discord.Message):
    channel_id: int
