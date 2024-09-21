import discord
from ..converters.percent import Percent as Percent
from _typeshed import Incomplete

class ValidRoleTextInput(discord.ui.TextInput):
    role: None | discord.Role
    async def interaction_check(self, interaction: discord.Interaction) -> bool: ...

class ValidImageURLTextInput(discord.ui.TextInput):
    valid_extensions: Incomplete
    def __init__(self, *args, valid_extensions: list[str] = ['.png', '.jpg', '.jpeg', '.gif'], **kwargs) -> None: ...
    async def interaction_check(self, interaction: discord.Interaction) -> bool: ...

class NumberPromptTextInput(discord.ui.TextInput):
    min: Incomplete
    max: Incomplete
    def __init__(self, *args, min: int | float | None = None, max: int | float | None = None, **kwargs) -> None: ...
    async def interaction_check(self, interaction: discord.Interaction) -> bool: ...

class NumberPromptModal(discord.ui.Modal):
    item: Incomplete
    author: Incomplete
    def __init__(self, *, author: discord.Member | discord.User, title: str, label: str, placeholder: str, custom_id: str, min: float, max: float, default: float | None = None, use_float: bool = False, row: int = 0) -> None: ...
    async def interaction_check(self, interaction: discord.Interaction) -> bool: ...
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: ...
    async def on_submit(self, interaction: discord.Interaction) -> None: ...
