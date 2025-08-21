import discord
import discord.ext
import asyncio
from discord.ext import commands
from week import Week

class SignupButtons(discord.ui.View):

    def __init__(self, bot, ctx: commands.Context, embed_msg : discord.Message, week: Week):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.embed_msg = embed_msg
        self.week = week
    
    def check(self, m):
        return m.author == self.ctx.message.author
    
    async def try_function(self):
        try:
            msg = await self.bot.wait_for('message', timeout = 30, check = self.check)
        except asyncio.TimeoutError:
            await self.ctx.send("Timeout error, please try again.")
            return -1
        else:
            return msg

    async def button_handle(self, interaction: discord.Interaction, day: str):
        username = interaction.user.display_name
        self.week.button(username, day)
        await self.embed_msg.edit(embed=self.week.generate_embed())
        await interaction.response.defer()
    
    @discord.ui.button(label = "Sunday", style = discord.ButtonStyle.primary)
    async def first_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "sunday")

    @discord.ui.button(label = "Monday", style = discord.ButtonStyle.primary)
    async def second_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.display_name
        self.week.button(username, "monday")
        await self.embed_msg.edit(embed=self.week.generate_embed())
        await interaction.response.defer()

    @discord.ui.button(label = "Tuesday", style = discord.ButtonStyle.primary)
    async def third_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.display_name
        self.week.button(username, "tuesday")
        await self.embed_msg.edit(embed=self.week.generate_embed())
        await interaction.response.defer()

    @discord.ui.button(label = "Wednesday", style = discord.ButtonStyle.primary)
    async def fourth_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.display_name
        self.week.button(username, "wednesday")
        await self.embed_msg.edit(embed=self.week.generate_embed())
        await interaction.response.defer()

    @discord.ui.button(label = "Thursday", style = discord.ButtonStyle.primary)
    async def fifth_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.display_name
        self.week.button(username, "thursday")
        await self.embed_msg.edit(embed=self.week.generate_embed())
        await interaction.response.defer()

    @discord.ui.button(label = "Friday", style = discord.ButtonStyle.primary)
    async def sixth_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.display_name
        self.week.button(username, "friday")
        await self.embed_msg.edit(embed=self.week.generate_embed())
        await interaction.response.defer()

    @discord.ui.button(label = "Saturday", style = discord.ButtonStyle.primary)
    async def seventh_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.display_name
        self.week.button(username, "saturday")
        await self.embed_msg.edit(embed=self.week.generate_embed())
        await interaction.response.defer()           
