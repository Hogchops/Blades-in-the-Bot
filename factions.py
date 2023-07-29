import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from difflib import get_close_matches
import json
from asyncio import wait_for
import os
from faction_clock_objects import Clock
from faction_clock_objects import Faction


class Factions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.faction_list = []
		self.init_info()
		
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
		for file in os.listdir("factions/"):
			if file.endswith(".json"):
				with open(f"factions/{file}", 'r') as infile:
					json_string = json.load(infile)
					json_obj = json.loads(json_string)
					self.add_faction_from_json(json_obj)
	

	def save_info(self):
		for faction in self.faction_list:
			file_name = faction.name.lower().replace(" ", "")
			with open(f'factions/{file_name}.json', 'w') as outfile:
				json_string = faction.toJson()
				outfile.write(json.dumps(json_string))

	def save_faction(self, faction_name):
		index = self.find(faction_name)
		if index == -1:
			return -1
		file_name = self.faction_list[index].name.lower().replace(" ", "")
		with open(f"factions/{file_name}.json", 'w') as outfile:
			json_string = self.faction_list[index].toJson()
			outfile.write(json.dumps(json_string))

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

	async def search_func(self, ctx, name, gm):
		index = self.find(name)
		if index != -1:
			await ctx.send(embed = self.player_gm_display(ctx, gm, index))
		else:
			title_list = []
			for f in self.faction_list:
				title_list.append(f.name.lower())
			close_matches = get_close_matches(name.lower(), title_list, 5, 0.3)
			if len(close_matches) == 1:
				chosen = self.find(close_matches[0])
				await ctx.send(embed = self.player_gm_display(ctx, gm, chosen))
			elif len(close_matches) == 0:
				await ctx.send(f"I could not find a faction matching {name}.")
			else:
				output = f"Enter the number corresponding to what you are searching for:"
				for i in range(len(close_matches)):
					output += f"\n**{i+1}**: {close_matches[i]}"
				await ctx.send(output)
			
				def check(m):
					return m.author == ctx.message.author and m.content.isdigit() and int(m.content) <= 5

				try:
					msg = await self.bot.wait_for('message', timeout = 8.0, check = check)
				except self.asyncio.TimeoutError:
					await ctx.send("Query timed out.")
				else:
					chosen = self.find(close_matches[int(msg.content)-1])
					await ctx.send(embed = self.player_gm_display(ctx, gm, chosen)) 
				

	@commands.command(name="faction", aliases = ['f'])
	async def display_faction(self, ctx, *, name):
		await self.search_func(ctx, name, False)

	@commands.group(name="gm", aliases=["dm"])
	async def gm(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.author.send("Hi!")

	@gm.command(name="faction", aliases = ['f'])
	async def display_faction_gm(self, ctx, *, name):
		await self.search_func(ctx, name, True)

	@gm.command(name="add", aliases=["a"])
	async def add_faction(self, ctx):
		await ctx.author.send("Still implementing!")


async def setup(bot):
	await bot.add_cog(Factions(bot))
