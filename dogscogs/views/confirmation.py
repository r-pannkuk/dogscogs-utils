import typing
import discord

async def async_true(i: discord.Interaction) -> bool:
    return True

class ConfirmationPrompt(discord.ui.Modal):
    value: bool = False

    def __init__(
        self,
        *args,
        author: discord.Member,
        callback: typing.Callable[[discord.Interaction], typing.Awaitable[bool]] = async_true,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.author = author
        self.callback = callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You are not allowed to interact with this message.", ephemeral=True, delete_after=10)
            return False
        return True
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.value = await self.callback(interaction)
        self.stop()
        

class ConfirmationView(discord.ui.View):
    """Whether the user pressed Yes or No."""
    value : bool = False

    def __init__(
            self, 
            *args, 
            author: discord.Member,
            callback: typing.Callable[[discord.Interaction], typing.Awaitable[bool]] = async_true,
            **kwargs
        ):
        super().__init__(*args, **kwargs)
        self.author = author
        self.callback = callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You are not allowed to interact with this message.", ephemeral=True, delete_after=10)
            return False
        return True

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = await self.callback(interaction)
        if not interaction.response.is_done():
            await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.defer()
        self.stop()