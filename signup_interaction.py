import discord
import discord.ext
import asyncio
from discord.ext import commands
from week import Week

class GetSignupResponse(discord.ui.Modal):

    def __init__(self, ctx: commands.context, week: Week, embed_msg: discord.Message, day: str, username: str):
        super().__init__()
        self.ctx = ctx
        self.week = week
        self.day = day
        self.embed_msg = embed_msg
        self.username = username

    async def on_submit(self, interaction: discord.Interaction):
        self.week.button(self.username, self.day)
        await interaction.response.edit_message(embed=self.week.generate_embed())

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
    
    @discord.ui.button(label = "Sunday", style = discord.ButtonStyle.primary)
    async def first_button_callback(self, interaction: discord.Interaction, button):
        response = GetSignupResponse(self.ctx, self.week, self.embed_msg, "sunday", interaction.user.name)
        await interaction.response.send_message(response)

    @discord.ui.button(label = "Monday", style = discord.ButtonStyle.primary)
    async def second_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.name
        self.week.button(username, "monday")
        await self.embed_msg.edit(embed=self.week.generate_embed())

    @discord.ui.button(label = "Tuesday", style = discord.ButtonStyle.primary)
    async def third_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.name
        self.week.button(username, "tuesday")
        await self.embed_msg.edit(embed=self.week.generate_embed())

    @discord.ui.button(label = "Wednesday", style = discord.ButtonStyle.primary)
    async def fourth_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.name
        self.week.button(username, "wednesday")
        await self.embed_msg.edit(embed=self.week.generate_embed())

    @discord.ui.button(label = "Thursday", style = discord.ButtonStyle.primary)
    async def fifth_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.name
        self.week.button(username, "thursday")
        await self.embed_msg.edit(embed=self.week.generate_embed())

    @discord.ui.button(label = "Friday", style = discord.ButtonStyle.primary)
    async def sixth_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.name
        self.week.button(username, "friday")
        await self.embed_msg.edit(embed=self.week.generate_embed())

    @discord.ui.button(label = "Saturday", style = discord.ButtonStyle.primary)
    async def seventh_button_callback(self, interaction: discord.Interaction, button):
        username = interaction.user.name
        self.week.button(username, "saturday")
        await self.embed_msg.edit(embed=self.week.generate_embed())           
