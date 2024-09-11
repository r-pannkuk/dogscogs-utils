import re
import discord


def convert_color_name(input: str) -> discord.Color:
    return discord.Colour.__dict__[input.lower().replace(' ', '_')].__func__(discord.Colour)

def convert_hex_code(input: str) -> discord.Color:
    return discord.Color.from_str(input)

def convert_color_tuple(input: str) -> discord.Color:
    return discord.Color.from_rgb(*map(int, re.sub(r"[^0-9,]", "", input).split(',')))

def convert_to_color(input: str):
    try:
        return convert_hex_code(input)
    except:
        try:
            return convert_color_tuple(input)
        except:
            return convert_color_name(input)
            
async def validate_color(input: str, interaction: discord.Interaction):
    try:
        convert_to_color(input)
        return True
    except: 
        return False