from discord.ext import commands
from difflib import get_close_matches
import json
from asyncio import wait_for
from asyncio import TimeoutError
import os
from faction_clock_objects import Faction
from interactions.button_interaction import ModifyFactionButtons
from discord import app_commands
from typing import List
import discord


class Factions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.faction_list = []
		self.init_info()
		self.faction_choices = []
		for faction in self.faction_list:
			self.faction_choices.append(app_commands.Choice(name = faction.name, value = faction.name))
		
	def list_factions(self):
		output = "**Factions:**\n"
		for faction in self.faction_list:
			output += faction.name + "\n"
		return output

	def add_faction_from_json(self, dict_obj: dict):
		name = dict_obj["name"]
		tier = dict_obj["tier"]
		hold = dict_obj["hold"]
		rep = dict_obj["rep"]
		description = dict_obj["description"]
		notes = dict_obj["notes"]
		contacts = dict_obj["contacts"]
		secret_notes = dict_obj["secret_notes"]
		creator = dict_obj["creator"]
		faction_obj = Faction(name, tier, hold, rep, description, contacts, notes, secret_notes, creator)
		for i in range(len(dict_obj["clocks"])):
			clock_description = dict_obj["clocks"][i]["description"]
			clock_progress = dict_obj["clocks"][i]["progress"]
			clock_total = dict_obj["clocks"][i]["total"]
			faction_obj.add_clock(clock_description, clock_progress, clock_total)
		self.faction_list.append(faction_obj)

	def init_info(self):
		for file in os.listdir("Factions\\"):
			if file.endswith(".json"):
				with open(f"Factions\\{file}", 'r') as infile:
					json_string = json.load(infile)
					json_obj = json.loads(json_string)
					self.add_faction_from_json(json_obj)

	def save_info(self):
		for faction in self.faction_list:
			file_name = faction.name.lower().replace(" ", "")
			with open(f'Factions\\{file_name}.json', 'w') as outfile:
				json_string = faction.toJson()
				outfile.write(json.dumps(json_string))

	async def save_faction(self, ctx, faction_name):
		index = await self.search_func(ctx, faction_name)
		if index == -1:
			return -1
		if ctx.author.id != self.faction_list[index].creator:
			return -1
		file_name = self.faction_list[index].name.lower().replace(" ", "")
		if file_name in os.listdir("Factions\\"):
			return -1
		with open(f"Factions\\{file_name}.json", 'w') as outfile:
			json_string = self.faction_list[index].toJson()
			outfile.write(json.dumps(json_string))
		return 1

	def find(self, name):
		for i in range(len(self.faction_list)):
			if self.faction_list[i].name.lower() == name.lower():
				return i
		return -1

	def player_gm_display(self, ctx, gm, index):
		if gm:
			embed = self.faction_list[index].gm_display(ctx)
		else:
			embed = self.faction_list[index].player_display(ctx)
		return embed

	async def search_func(self, ctx, name):
		index = self.find(name)
		if index != -1:
			return index
		else:
			title_list = []
			for f in self.faction_list:
				title_list.append(f.name.lower())
			close_matches = get_close_matches(name.lower(), title_list, 5, 0.6)
			if len(close_matches) == 1:
				chosen = self.find(close_matches[0])
				return chosen
			elif len(close_matches) == 0:
				await ctx.send(f"I could not find a faction matching {name}.", ephemeral = True)
				return -1
			else:
				output = f"Enter the number corresponding to what you are searching for:"
				for i in range(len(close_matches)):
					output += f"\n**{i+1}**: {close_matches[i]}"
				await ctx.send(output, ephemeral = True)
			
				def check(m):
					return m.author == ctx.message.author and m.content.isdigit() and int(m.content) <= 5

				try:
					msg = await self.bot.wait_for('message', timeout = 8.0, check = check)
				except TimeoutError:
					await ctx.send("Query timed out.", ephemeral = True)
					return -1
				else:
					await msg.delete()
					chosen = self.find(close_matches[int(msg.content)-1])
					return chosen
				
	async def autocomplete_gm(self, inter: discord.interactions.Interaction, current: str) -> List[app_commands.Choice[str]]:
		choices = []
		for faction in self.faction_list:
			if faction.creator == inter.user.id:
				choices.append(faction.name)
		return [
			app_commands.Choice(name = choice, value = choice)
			for choice in choices if current.lower() in choice.lower()
		]
	
	async def autocomplete(self, inter: discord.interactions.Interaction, current: str) -> List[app_commands.Choice[str]]:
		choices = [faction.name for faction in self.faction_list]
		return [
			app_commands.Choice(name = choice, value = choice)
			for choice in choices if current.lower() in choice.lower()
		]
	
	@commands.hybrid_command(name="faction", aliases = ['f'], description = "Lookup the inputted faction.")
	@app_commands.autocomplete(factions = autocomplete)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def display_faction(self, ctx, factions: str):
		await ctx.defer()
		factions = factions.lower()
		index = await self.search_func(ctx, factions)
		if index != -1:
			await ctx.send(embed = self.faction_list[index].player_display())

	@commands.hybrid_command(name="list", aliases = ['l'], description = "List the factions.")
	async def list_factions(self, ctx: commands.Context):
		await ctx.defer(ephemeral = True)
		embed = discord.Embed(name = "Factions", description = "The list of factions created using this bot.", color = discord.Color.magenta())
		embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.display_avatar.url)
		value = ""
		for faction in self.faction_list:
			value += f"{faction.name.title()}\n"
		embed.add_field(name = "Factions", value = value)
		await ctx.send(embed = embed, ephemeral = True)

	@commands.hybrid_group(name = "gm", aliases = ['dm'])
	async def gm(self, ctx):
		pass

	@gm.command(name="faction", aliases = ['f'], description = "Display the GM version of a faction that you've created.")
	@app_commands.autocomplete(factions = autocomplete_gm)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def display_faction_gm(self, ctx, factions: str):
		await ctx.defer(ephemeral = True)
		index = await self.search_func(ctx, factions)
		if index != -1:
			if self.faction_list[index].creator != ctx.author.id:
				await ctx.send("You are not the GM for this faction.")
			else:
				await ctx.send(embed = self.faction_list[index].gm_display(), ephemeral = True)

	@gm.command(name="add", aliases=["a"], description = "Create a new faction.")
	@app_commands.describe(
		name = "Enter a faction name for this new faction."
	)
	async def add_faction(self, ctx, name: str):
		await ctx.defer(ephemeral = True)
		index = self.find(name)
		if index != -1:
			await ctx.send("There is already a faction with that name.")
		else:
			default_faction = Faction(f"{name.title()}", 0, "hold", "0", "description", [], "notes", "secret notes", ctx.author.id)
			self.faction_list.append(default_faction)
			await self.save_faction(ctx, name)
			await ctx.send(f"I have created a default faction with the name {name.title()}.\nPlease modify its values using `/gm modify {name.title()}`", ephemeral = True)

	@gm.command(name="modify", aliases=["m"], description = "Modify a faction that you've created.")
	@app_commands.autocomplete(factions = autocomplete_gm)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def modify_faction(self, ctx, factions: str):
		await ctx.defer(ephemeral = True)
		index = await self.search_func(ctx, factions)
		if index != -1:
			if self.faction_list[index].creator != ctx.author.id:
				await ctx.send("You are not the GM of this faction.")
			else:
				msg = await ctx.send(embed = self.faction_list[index].gm_display())
				await ctx.send(f"When you are done modifying, please save the faction via `/gm save {factions.title()}`", ephemeral = True)
				await ctx.send("Select the corresponding button to edit the faction.", view = ModifyFactionButtons(self.bot, ctx, self.faction_list[index], msg), ephemeral = True)
	
	@gm.command(name="save", aliases = ['s'], description = "Save a faction that you created.")
	@app_commands.autocomplete(factions = autocomplete_gm)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def save_faction_input(self, ctx, factions: str):
		await ctx.defer(ephemeral = True)
		result = await self.save_faction(ctx, factions)
		if result == 1:
			await ctx.send(f"You have successfully saved {factions.title()}", ephemeral = True)
		else:
			await ctx.send("Something went wrong, either no faction was found or you are not the gm of this faction.", ephemeral = True)
	
	@gm.command(name = "delete", aliases = ['d'], description = "Delete a faction that you created")
	@app_commands.autocomplete(factions = autocomplete_gm)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def delete_faction(self, ctx, factions: str):
		await ctx.defer(ephemeral = True)
		index = await self.search_func(ctx, factions)
		if index != -1:
			if self.faction_list[index].creator != ctx.author.id:
				await ctx.send("You are not the gm of this faction.")
			else:
				file_name = self.faction_list[index].name.lower().replace(' ','')
				os.remove(f"factions/{file_name}.json")
				del self.faction_list[index]
				await ctx.send("Faction deleted successfully.", ephemeral = True)
	

	async def get_all_parts(self, inter: discord.interactions.Interaction, current):
		choices = []
		final_choices = []
		faction_name = inter.namespace.faction

		index = self.find(faction_name)
		faction_obj = self.faction_list[index]
		for clock_obj in faction_obj.clocks:
			choices.append(clock_obj.description)

		for choice in choices:
			if current.lower() in choice.lower():
				final_choices.append(app_commands.Choice(name = choice, value = choice))
		return final_choices

	@gm.command(name = "tick", aliases = ['t'], description = "Tick a faction's clock.")
	@app_commands.autocomplete(faction = autocomplete_gm, clock = get_all_parts)
	@app_commands.describe(
		faction = "Enter the faction name that has the clock you want to tick.",
		clock = "Enter the description of the clock that you wish to tick.",
		amount = "Enter the amount you wish to tick. Enter 0 to roll the tier and have it manually be ticked. If you enter a positive or negative amount, the clock will tick by that amount."
	)
	async def tick_faction_clock(self, ctx, faction: str, clock: str, amount: int):
		await ctx.defer(ephemeral = True)
		index = self.find(faction)
		if index == -1:
			await ctx.send(f"There is no faction matching {faction.title()} that you have access to.")
		elif self.faction_list[index].creator == ctx.author.id:
			faction_obj = self.faction_list[index]
			clock_index = faction_obj.find_clock(clock)
			if amount == 0:
				embed = faction_obj.clocks[clock_index].advance(int(faction_obj.tier), ctx)
				await ctx.send(embed = embed, ephemeral = True)
				await ctx.send(embed = faction_obj.gm_display(), ephemeral = True)
			else:
				faction_obj.clocks[clock_index].progress += amount
				if faction_obj.clocks[clock_index].progress > faction_obj.clocks[clock_index].total:
					faction_obj.clocks[clock_index].progress = faction_obj.clocks[clock_index].total	
				elif faction_obj.clocks[clock_index].progress < 0:
					faction_obj.clocks[clock_index].progress = 0
					await ctx.send(embed = faction_obj.gm_display(), ephemeral = True)
			await self.save_faction(ctx, faction_obj.name)
		else:
			await ctx.send(f"There is no faction matching {faction.title()} that you have access to.")
		
	
async def setup(bot):
	await bot.add_cog(Factions(bot))