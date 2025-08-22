import discord
import discord.ext
import asyncio
from discord.ext import commands
from week import Week
import json
from signup import Signup

class SignupButtons(discord.ui.View):

    def __init__(self, cog: Signup, bot, week: Week, channel_id: int, embed_id: int, view_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.cog = cog
        self.week = week
        self.channel_id = channel_id
        self.embed_id = embed_id
        self.view_id = view_id
    
    async def button_handle(self, interaction: discord.Interaction, day: str):
        user = interaction.user
        channel = self.bot.get_channel(self.channel_id)
        embed_msg = await channel.fetch_message(self.embed_id)

        i = self.week.button(user, day)
        if i != -1:
            if i == 1:
                await channel.send("A session is confirmed on **" + day.title() + "** at **7:00 pm EST** with the people listed above. This session can still accept more players.")

            await embed_msg.edit(embed=self.cog.generate_embed())
            state = {
                "channel_id": channel.id,
                "embed_id": self.embed_id,
                "view_id": self.view_id,
                "week": self.week.to_dict()
            }
            with open("signup_state.json", "w") as f:
                json.dump(state, f)

            await interaction.response.defer()
        else:
            await interaction.user.send("I could not add or remove you from that day, it's already confirmed or it's already full")
            await interaction.response.defer()
    
    @discord.ui.button(label = "Sunday", style = discord.ButtonStyle.primary, custom_id="signup_sunday")
    async def first_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "sunday")

    @discord.ui.button(label = "Monday", style = discord.ButtonStyle.primary, custom_id="signup_monday")
    async def second_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "monday")

    @discord.ui.button(label = "Tuesday", style = discord.ButtonStyle.primary, custom_id="signup_tuesday")
    async def third_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "tuesday")

    @discord.ui.button(label = "Wednesday", style = discord.ButtonStyle.primary, custom_id="signup_wednesday")
    async def fourth_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "wednesday")

    @discord.ui.button(label = "Thursday", style = discord.ButtonStyle.primary, custom_id="signup_thursday")
    async def fifth_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "thursday")

    @discord.ui.button(label = "Friday", style = discord.ButtonStyle.primary, custom_id="signup_friday")
    async def sixth_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "friday")

    @discord.ui.button(label = "Saturday", style = discord.ButtonStyle.primary, custom_id="signup_saturday")
    async def seventh_button_callback(self, interaction: discord.Interaction, button):
        await self.button_handle(interaction, "saturday")
