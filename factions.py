from discord.ext import commands
from difflib import get_close_matches
import json
from asyncio import wait_for
from asyncio import TimeoutError
import os
from faction_clock_objects import Faction
from button_interaction import ModifyFactionButtons
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
		faction_obj = Faction(name, tier, hold, rep, description, contacts, notes, secret_notes)
		for i in range(len(dict_obj["clocks"])):
			clock_description = dict_obj["clocks"][i]["description"]
			clock_progress = dict_obj["clocks"][i]["progress"]
			clock_total = dict_obj["clocks"][i]["total"]
			faction_obj.add_clock(clock_description, clock_progress, clock_total)
		self.faction_list.append(faction_obj)

	def init_info(self):
		for file in os.listdir("factions\\"):
			if file.endswith(".json"):
				with open(f"factions\\{file}", 'r') as infile:
					json_string = json.load(infile)
					json_obj = json.loads(json_string)
					self.add_faction_from_json(json_obj)

	def save_info(self):
		for faction in self.faction_list:
			file_name = faction.name.lower().replace(" ", "")
			with open(f'factions\\{file_name}.json', 'w') as outfile:
				json_string = faction.toJson()
				outfile.write(json.dumps(json_string))

	async def save_faction(self, ctx, faction_name):
		index = await self.search_func(ctx, faction_name)
		if index == -1:
			return -1
		file_name = self.faction_list[index].name.lower().replace(" ", "")
		with open(f"factions\\{file_name}.json", 'w') as outfile:
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
				
	async def autocomplete_gm(self, ctx, current: str) -> List[app_commands.Choice[str]]:
		choices = [faction.name for faction in self.faction_list if faction.creator == ctx.author]
		return [
			app_commands.Choice(name = choice, value = choice)
			for choice in choices if current.lower() in choice.lower()
		]
	
	async def autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
		choices = [faction.name for faction in self.faction_list]
		return [
			app_commands.Choice(name = choice, value = choice)
			for choice in choices if current.lower() in choice.lower()
		]
		
	@commands.hybrid_command(name="faction", aliases = ['f'], description = "Lookup the inputted faction.")
	#@app_commands.guilds(discord.Object(id = 807855936106135562))
	@app_commands.autocomplete(factions = autocomplete)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def display_faction(self, ctx, factions: str):
		await ctx.defer()
		factions = factions.lower()
		index = await self.search_func(ctx, factions)
		if index != -1:
			await ctx.send(embed = self.faction_list[index].player_display(ctx))

	@commands.hybrid_command(name="list", aliases = ['l'], description = "List the factions.")
	#@app_commands.guilds(discord.Object(id = 807855936106135562))
	async def list_factions(self, ctx):
		await ctx.defer(ephemeral = True)
		output = "**Factions:**\n"
		for faction in self.faction_list:
			output += f"{faction.name}\n"
		await ctx.send(output, ephemeral = True)

	#@commands.guild_only()
	#@commands.has_permissions(administrator = True)

	@commands.hybrid_group(name = "gm", aliases = ['dm'])
	@app_commands.guilds(discord.Object(id = 807855936106135562))
	@commands.has_permissions(administrator = True)
	async def gm(self, ctx):
		pass

	@gm.command(name="faction", aliases = ['f'])
	@app_commands.guilds(discord.Object(id = 807855936106135562))
	@app_commands.autocomplete(factions = autocomplete_gm)
	@commands.has_permissions(administrator = True)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def display_faction_gm(self, ctx, factions: str):
		await ctx.defer(ephemeral = True)
		index = await self.search_func(ctx, factions)
		if index != -1:
			await ctx.send(embed = self.faction_list[index].gm_display(ctx), ephemeral = True)

	@gm.command(name="add", aliases=["a"])
	@app_commands.guilds(discord.Object(id = 807855936106135562))
	@commands.has_permissions(administrator = True)
	@app_commands.describe(
		name = "Enter a faction name for this new faction."
	)
	async def add_faction(self, ctx, name: str):
		await ctx.defer(ephemeral = True)
		default_faction = Faction(f"{name.title()}", 0, "hold", "0", "description", [], "notes", "secret notes", ctx.author)
		self.faction_list.append(default_faction)
		await self.save_faction(ctx, name)
		await ctx.send(f"I have created a default faction with the name {name.title()}.\nPlease modify its values using `/gm m {name.title()}`", ephemeral = True)

	@gm.command(name="modify", aliases=["m"])
	@app_commands.guilds(discord.Object(id = 807855936106135562))
	@app_commands.autocomplete(factions = autocomplete_gm)
	@commands.has_permissions(administrator = True)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def modify_faction(self, ctx, factions: str):
		await ctx.defer(ephemeral = True)
		index = await self.search_func(ctx, factions)
		if index != -1:
			msg = await ctx.send(embed = self.faction_list[index].gm_display(ctx))
			await ctx.send(f"When you are done modifying, please save the faction via `/gm s {factions.title()}`", ephemeral = True)
			await ctx.send("Select the corresponding button to edit the faction.", view = ModifyFactionButtons(self.bot, ctx, self.faction_list[index], msg), ephemeral = True)
	
	@gm.command(name="save", aliases = ['s'])
	@app_commands.guilds(discord.Object(id = 807855936106135562))
	@app_commands.autocomplete(factions = autocomplete_gm)
	@commands.has_permissions(administrator = True)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def save_faction_input(self, ctx, factions: str):
		result = await self.save_faction(ctx, factions)
		if result == 1:
			await ctx.send(f"You have successfully saved {factions.title()}", ephemeral = True)
	
	@gm.command(name = "delete", aliases = ['d'])
	@app_commands.guilds(discord.Object(id = 807855936106135562))
	@app_commands.autocomplete(factions = autocomplete_gm)
	@commands.has_permissions(administrator = True)
	@app_commands.describe(
		factions = "Enter a faction name."
	)
	async def delete_faction(self, ctx, factions: str):
		index = await self.search_func(ctx, factions)
		if index != -1:
			file_name = self.faction_list[index].name.lower().replace(' ','')
			os.remove(f"factions/{file_name}.json")
			del self.faction_list[index]
			await ctx.send("Faction deleted successfully.", ephemeral = True)
	
async def setup(bot):
	await bot.add_cog(Factions(bot))