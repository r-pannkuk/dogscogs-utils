import typing
import discord
import requests

from discord.ext import commands

from ..converters.percent import Percent

class ValidRoleTextInput(discord.ui.TextInput):
    role: typing.Union[None, discord.Role] = None
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        try:
            class FakeContext():
                guild: discord.Guild

            ctx = FakeContext()
            ctx.guild = interaction.guild # type: ignore[assignment]

            value = self.value

            if value.startswith('@'):
                value = value[1:]

            self.role = await commands.RoleConverter().convert(ctx, value) # type: ignore[arg-type]
        except:
            await interaction.response.send_message("❌ ERROR: Please enter a valid role.", ephemeral=True, delete_after=15)
            return False

        return True

class ValidImageURLTextInput(discord.ui.TextInput):
    def __init__(
        self,
        *args,
        valid_extensions: typing.List[str] = ["png", "jpg", "jpeg", "gif"],
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.valid_extensions = valid_extensions

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        extension = self.value.lower().split(".")[-1]

        if extension not in self.valid_extensions:
            await interaction.response.send_message(f"❌ ERROR: Only the following image extensions are supported: {', '.join(self.valid_extensions)}.", ephemeral=True, delete_after=15)
            return False

        try: 
            image_formats = (
                f"image/{ext}" for ext in self.valid_extensions
            )
            r = requests.head(self.value)
            if r.headers["content-type"] not in image_formats:
                await interaction.response.send_message("❌ ERROR: Please enter a valid image URL.", ephemeral=True, delete_after=15)
                return False
            return True
        except:
            await interaction.response.send_message("❌ ERROR: Please enter a valid image URL.", ephemeral=True, delete_after=15)
            return False


class NumberPromptTextInput(discord.ui.TextInput):
    def __init__(
        self,
        *args,
        min : typing.Optional[typing.Union[int, float]] = None,
        max : typing.Optional[typing.Union[int, float]] = None,
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

    
        

class NumberPromptModal(discord.ui.Modal):
    def __init__(
        self,
        *,
        author: typing.Union[discord.Member, discord.User],
        title: str,
        label: str,
        placeholder: str,
        custom_id: str,
        min: float,
        max: float,
        default: typing.Optional[float] = None,
        use_float: bool = False,
        row: int = 0,
    ):
        super().__init__(
            timeout=10 * 60,
            title=title,
        )

        if not use_float:
            min = int(min)
            max = int(max)
            default = int(default) if default is not None else None

        self.item: NumberPromptTextInput = NumberPromptTextInput(
            label=label,
            placeholder=placeholder,
            required=True,
            style=discord.TextStyle.short,
            custom_id=custom_id,
            row=row,
            default=str(default) if default is not None else None,
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