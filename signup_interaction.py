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
        user = interaction.user
        i = self.week.button(user, day)
        if i != -1:
            if i == 1:
                await interaction.channel.send("A session is confirmed on **" + day.title() + "** at **7:00 pm EST** with the people listed above. This session can still accept more players.")
            await self.embed_msg.edit(embed=self.week.generate_embed())
            await interaction.response.defer()
        else:
            await interaction.user.send("I could not add or remove you from that day, it's already confirmed or it's already full")
            await interaction.response.defer()
    
    @discord.ui.button(label = "Sunday", style = discord.ButtonStyle.primary)
    async def first_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "sunday")

    @discord.ui.button(label = "Monday", style = discord.ButtonStyle.primary)
    async def second_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "monday")

    @discord.ui.button(label = "Tuesday", style = discord.ButtonStyle.primary)
    async def third_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "tuesday")

    @discord.ui.button(label = "Wednesday", style = discord.ButtonStyle.primary)
    async def fourth_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "wednesday")

    @discord.ui.button(label = "Thursday", style = discord.ButtonStyle.primary)
    async def fifth_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "thursday")

    @discord.ui.button(label = "Friday", style = discord.ButtonStyle.primary)
    async def sixth_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "friday")

    @discord.ui.button(label = "Saturday", style = discord.ButtonStyle.primary)
    async def seventh_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "saturday")
