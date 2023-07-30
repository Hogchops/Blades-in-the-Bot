import discord
import discord.ext
import asyncio
from faction_clock_objects import Faction
from faction_clock_objects import Clock

class GetResponse(discord.ui.Modal):

    def __init__(self, title: str, faction: Faction, msg: discord.Message, ctx):
        self.field_name = title.lower()
        self.faction = faction
        super().__init__(title = self.field_name)
        self.answer = ""
        self.clock_fields = ""
        self.add_clock = ""
        self.msg = msg
        self.ctx = ctx

        if self.field_name != "clocks" and self.field_name != "contacts":
            self.answer = discord.ui.TextInput(label = f'Enter a new {self.field_name.title()}.', style = discord.TextStyle.paragraph, placeholder = self.faction.get(self.field_name))
            self.add_item(self.answer)
        elif self.field_name == "contacts":
            self.answer = discord.ui.TextInput(label = "Enter contacts for this faction, 1 per line.", style = discord.TextStyle.paragraph, placeholder="Contact1\nContact2")
            self.add_item(self.answer)
        elif self.field_name == "clocks":
            if len(self.faction.clocks) <= 4:
                self.add_clock = discord.ui.TextInput(label = "Enter a new clock if you wish to add.", required=False, style=discord.TextStyle.paragraph)
                self.add_item(self.add_clock)
            self.clock_fields = []
            num = 1
            for clock in self.faction.clocks:
                place_holder = f"{clock.description}\n{clock.progress}\n{clock.total}"
                clock_field = discord.ui.TextInput(label = f"Modify Clock {num}.", placeholder=place_holder, style=discord.TextStyle.paragraph, required=False)
                self.clock_fields.append(clock_field)
                self.add_item(clock_field)
                num += 1

    async def on_submit(self, interaction: discord.Interaction):
        if self.field_name != "clocks" and self.field_name != "contacts":
            self.faction.set(self.field_name, self.answer.value)
        elif self.field_name == "contacts":
            contacts_list = self.answer.value.splitlines()
            self.faction.set("contacts", contacts_list)
        elif self.field_name == "clocks":
            clocks_list = []
            for clock_obj in self.clock_fields:
                user_input = clock_obj.value.splitlines()
                print(user_input)
                if user_input != "":
                    description = user_input[0]
                    progress = int(user_input[1])
                    total = int(user_input[2])
                    clock_obj = Clock(description, progress, total)
                    clocks_list.append(clock_obj)
            self.faction.set("clocks", clocks_list)
            if self.add_clock.value != "":
                user_input = self.add_clock.value.splitlines()
                self.faction.add_clock(user_input[0], int(user_input[1]), int(user_input[2]))
        await self.msg.edit(embed = self.faction.gm_display(ctx=self.ctx))
        await interaction.response.send_message(f'Thanks for your response. {self.faction.name} has been updated. Please see the edited embed.', ephemeral=True)
    
class ModifyFactionButtons(discord.ui.View):

    def __init__(self, bot, ctx, faction_obj : Faction, original_embed : discord.Message):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.faction_obj = faction_obj
        self.original_embed = original_embed
	
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
    

    @discord.ui.button(label = "Title", style = discord.ButtonStyle.primary)
    async def first_button_callback(self, interaction: discord.Interaction, button):
        response = GetResponse(title = "Title", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)
            
    @discord.ui.button(label = "Description", style = discord.ButtonStyle.primary)
    async def second_button_callback(self, interaction, button):
        response = GetResponse(title = "Description", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)

    @discord.ui.button(label = "Tier", style = discord.ButtonStyle.primary)
    async def third_button_callback(self, interaction, button):
        response = GetResponse(title = "Tier", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)

    @discord.ui.button(label = "Hold", style = discord.ButtonStyle.primary)
    async def fourth_button_callback(self, interaction, button):
        response = GetResponse(title = "Hold", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)

    @discord.ui.button(label = "Contacts", style = discord.ButtonStyle.primary)
    async def fifth_button_callback(self, interaction, button):
        response = GetResponse(title = "Contacts", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)

    @discord.ui.button(label = "Status", style = discord.ButtonStyle.primary)
    async def sixth_button_callback(self, interaction, button):
        response = GetResponse(title = "Status", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)

    @discord.ui.button(label = "Notes", style = discord.ButtonStyle.primary)
    async def seventh_button_callback(self, interaction, button):
        response = GetResponse(title = "Notes", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)

    @discord.ui.button(label = "Secret Notes", style = discord.ButtonStyle.primary)
    async def eigth_button_callback(self, interaction, button):
        response = GetResponse(title = "Secret Notes", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)

    @discord.ui.button(label = "Clocks", style = discord.ButtonStyle.primary)
    async def ninth_button_callback(self, interaction, button):
        response = GetResponse(title = "Clocks", faction = self.faction_obj, msg = self.original_embed, ctx=self.ctx)
        await interaction.response.send_modal(response)