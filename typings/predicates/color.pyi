import discord

def convert_color_name(input: str) -> discord.Color: ...
def convert_hex_code(input: str) -> discord.Color: ...
def convert_color_tuple(input: str) -> discord.Color: ...
def convert_to_color(input: str): ...
async def validate_color(input: str, interaction: discord.Interaction): ...