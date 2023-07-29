import discord
import asyncio

class MyView(discord.ui.View):

    def __init__(self, bot, ctx, faction_obj):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.faction_obj = faction_obj
	
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
    async def first_button_callback(self, interaction, button):
        await interaction.response.send_message("Type a new title for this faction.")
        msg = await self.try_function()
        if msg != -1:
            self.faction_obj.name = msg.content.title()
            await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))

    @discord.ui.button(label = "Description", style = discord.ButtonStyle.primary)
    async def second_button_callback(self, interaction, button):
        await interaction.response.send_message("Type a new description for this faction.")
        msg = await self.try_function()
        if msg != -1:
            self.faction_obj.description = msg.content
            await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))

    @discord.ui.button(label = "Tier", style = discord.ButtonStyle.primary)
    async def third_button_callback(self, interaction, button):
        await interaction.response.send_message("Type a new tier for this faction.")
        msg = await self.try_function()
        if msg != -1:
            self.faction_obj.tier = int(msg.content)
            await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))

    @discord.ui.button(label = "Hold", style = discord.ButtonStyle.primary)
    async def fourth_button_callback(self, interaction, button):
        await interaction.response.send_message("Type a new hold for this faction.")
        msg = await self.try_function()
        if msg != -1:
            self.faction_obj.hold = msg.content
            await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))

    @discord.ui.button(label = "Contacts", style = discord.ButtonStyle.primary)
    async def fifth_button_callback(self, interaction, button):
        output = "**Contacts:**\n"
        for i in range(len(self.faction_obj.contacts)):
            output += f'**{i}:** {self.faction_obj.contacts[i]}\n'
        await interaction.response.send_message("Enter a number for the contact you wish to change, or `a` for a new contact.\n\n" + output)
        msg = await self.try_function()
        if msg != -1:
            if msg.content.lower() == 'a':
                await self.ctx.send("You have chosen to add a new contact. Please type a contact to add it to the faction.")
                new_contact_msg = await self.try_function()
                if new_contact_msg != -1:
                    self.faction_obj.contacts.append(new_contact_msg.content)
            else:
                index = int(msg.content)
                await self.ctx.send(f'The contact {self.faction_obj.contacts[index]} has been chosen. Please type a new contact.')
                contact_msg = await self.try_function()
                if contact_msg != -1:
                    self.faction_obj.contacts[index] = contact_msg.content
                    await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))

    @discord.ui.button(label = "Status", style = discord.ButtonStyle.primary)
    async def sixth_button_callback(self, interaction, button):
        await interaction.response.send_message("Type a new hold for this faction.")
        msg = await self.try_function()
        if msg != -1:
            self.faction_obj.status = msg.content
            await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))

    @discord.ui.button(label = "Notes", style = discord.ButtonStyle.primary)
    async def seventh_button_callback(self, interaction, button):
        await interaction.response.send_message("Type a new note for this faction.")
        msg = await self.try_function()
        if msg != -1:
            self.faction_obj.notes = msg.content
            await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))

    @discord.ui.button(label = "Secret Notes", style = discord.ButtonStyle.primary)
    async def eigth_button_callback(self, interaction, button):
        await interaction.response.send_message("Type a new secret note for this faction.")
        msg = await self.try_function()
        if msg != -1:
            self.faction_obj.secret_notes = msg.content
            await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))

    @discord.ui.button(label = "Clocks", style = discord.ButtonStyle.primary)
    async def ninth_button_callback(self, interaction, button):
        output = "**Clocks:**\n"
        for i in range(len(self.faction_obj.clocks)):
            output += f'**{i}:** {self.faction_obj.clocks[i].description} {self.faction_obj.clocks[i].progress}/{self.faction_obj.clocks[i].total}\n'
        await interaction.response.send_message("Enter a number for the clock you wish to change, or type 'a' to add a new clock.")
        msg = await self.try_function()
        if msg != -1:
            if msg.content.lower() == 'a':
                await self.ctx.send("Please enter a description for your clock.")
                clock_description = await self.try_function()
                if clock_description != -1:
                    await self.ctx.send("Please enter the starting progress and the total number on the clock. I.e.: 3 12")
                    progress_total = await self.try_function()
                    if progress_total != -1:
                        progress_total = progress_total.content.split(" ")
                        progress = int(progress_total[0])
                        total = int(progress_total[1])
                        self.faction_obj.add_clock(clock_description.content, progress, total)
                        await self.ctx.send(embed = self.faction_obj.gm_display(self.ctx))
            else:
                index = int(msg.content)
                await self.ctx.send("Select the corresponding buttons to edit the clock.", view = MyViewClocks(self.bot, self.ctx, self.faction_obj.clocks[index]))

class MyViewClocks(discord.ui.View):

    def __init__(self, bot, ctx, clock):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.clock = clock

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

    @discord.ui.button(label = "Description", style = discord.ButtonStyle.primary)
    async def description_button(self, interaction, button):
        await interaction.response.send_message("Type a description for this clock.")
        msg = await self.try_function()
        if msg != -1:
            self.clock.description = msg.content
        
    @discord.ui.button(label = "Progress", style = discord.ButtonStyle.primary)
    async def progress_button(self, interaction, button):
        await interaction.response.send_message("Type a progress number for this clock.")
        msg = await self.try_function()
        if msg != -1:
            self.clock.progress = int(msg.content)

    @discord.ui.button(label = "Total", style = discord.ButtonStyle.primary)
    async def total_button(self, interaction, button):
        await interaction.response.send_message("Type a total number for this clock.")
        msg = await self.try_function()
        if msg != -1:
            self.clock.total = int(msg.content)