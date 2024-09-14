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
            raise ValueError("Please enter a valid number.")

        if self.min is not None and value < self.min:
            raise ValueError(f"Please enter a number greater than {self.min}.")

        if self.max is not None and value > self.max:
            raise ValueError(f"Please enter a number less than {self.max}.")

        return True
        

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

        # try:
        #     value = await Percent.parse(None, self.item.value) # type: ignore[arg-type]
        # except:
        #     raise ValueError("Please enter a valid number.")

        # if value < self.min or value > self.max:
        #     raise ValueError(
        #         f"Please enter a number between {self.min} and {self.max}."
        #     )

        return True

    async def on_error(self, interaction: discord.Interaction, exception: Exception) -> None:  # type: ignore
        await interaction.response.send_message(
            str(exception), ephemeral=True, delete_after=20
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()