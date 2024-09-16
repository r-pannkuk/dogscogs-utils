import typing
import discord

from ..converters.percent import Percent

class NumberPromptTextInput(discord.ui.TextInput):
    def __init__(
        self,
        *args,
        min : typing.Optional[int] = None,
        max : typing.Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.min = min
        self.max = max

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        try:
            value = await Percent.parse(None, self.value) # type: ignore[arg-type]
        except:
            await interaction.response.send_message("❌ ERROR: Please enter a valid number.", ephemeral=True, delete_after=15)
            return False

        if self.min is not None and value < self.min:
            await interaction.response.send_message(f"❌ ERROR: Please enter a number greater than {self.min}.", ephemeral=True, delete_after=15)
            return False

        if self.max is not None and value > self.max:
            await interaction.response.send_message(f"❌ ERROR: Please enter a number less than {self.max}.", ephemeral=True, delete_after=15)
            return False

        return True
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

    
        

class NumberPromptModal(discord.ui.Modal):
    def __init__(
        self,
        *,
        author: typing.Union[discord.Member, discord.User],
        title: str,
        label: str,
        placeholder: str,
        custom_id: str,
        min: int,
        max: int,
        row: int = 0,
    ):
        super().__init__(
            timeout=10 * 60,
            title=title,
        )

        self.item: NumberPromptTextInput = NumberPromptTextInput(
            label=label,
            placeholder=placeholder,
            required=True,
            style=discord.TextStyle.short,
            custom_id=custom_id,
            row=row,
            min=min,
            max=max,
        )

        self.add_item(self.item)

        self.author: typing.Union[discord.Member, discord.User] = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            return False
        
        for item in self.children:
            if not await item.interaction_check(interaction):
                return False

        return True
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: # type: ignore[override]
        await interaction.response.send_message(f"❌ An error occured: {error}", ephemeral=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.stop()