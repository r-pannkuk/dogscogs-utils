import typing
import discord

from ...converters.percent import Percent

class PercentagePrompt(discord.ui.Modal):
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

        self.item: discord.ui.TextInput = discord.ui.TextInput(
            label=label,
            placeholder=placeholder,
            required=True,
            style=discord.TextStyle.short,
            custom_id=custom_id,
            row=row,
        )

        self.add_item(self.item)

        self.min = min
        self.max = max
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            return False

        try:
            value = await Percent.parse(None, self.item.value) # type: ignore[arg-type]
        except:
            raise ValueError("Please enter a valid number.")

        if value < self.min or value > self.max:
            raise ValueError(
                f"Please enter a number between {self.min} and {self.max}."
            )

        return True

    async def on_error(self, interaction: discord.Interaction, exception: Exception) -> None:  # type: ignore
        await interaction.response.send_message(
            str(exception), ephemeral=True, delete_after=20
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()