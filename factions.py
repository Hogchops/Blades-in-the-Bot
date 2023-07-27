import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from difflib import get_close_matches
import json
from asyncio import wait_for

def generate_embed():
	pass

class Clock:
	def __init__(self, description, progress, total):
		self.description = description
		self.progress = progress
		self.total = total
	
	def advance(self, tier):
		dice = [random.choice(range(1,7)) for _ in range(tier)]
		dice.sort()
		result = 0
		if dice[-1] == 6:
			result = 3
			if tier >= 2:
				if dice[-1] == 6:
					result += 2
		elif dice[-1] == 4 or dice[-1] == 5:
			result = 2
		else:
			result = 1
		self.progress += result
		return self.progress >= self.total

	def advance_manually(self, num):
		self.progress += num
		return self.progress >= self.total

	def to_json(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent = 4)

class Faction:
	def __init__(self, name, tier, hold, rep, description, contacts, notes, secret_notes):
		self.name = name
		self.tier = tier
		self.hold = hold
		self.rep = rep
		self.description = description
		self.contacts = contacts
		self.notes = notes
		self.secret_notes = secret_notes
		self.clocks = []

	def to_json(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent = 4)

	def add_clock(self, description, progress, total):
		clock_to_add = Clock(description, progress, total)
		self.clocks.append(clock_to_add)

	def player_display(self, ctx):
		embed = discord.Embed(title = self.name, description = self.description, color = ctx.author.color)
		embed.add_field(name = f'Tier {self.tier}', value = '')
		embed.add_field(name = f'Hold {self.hold}', value = '')
		names = ""
		for contact in self.contacts:
			names += contact + "\n"
		embed.add_field(name = 'Contacts', value = names)
		embed.add_field(name = 'Status', value = f'{self.rep}')
		if self.notes != "":
			embed.add_field(name = "Notes", value = self.notes)
		return embed
	
	def gm_display(self, ctx):
		embed = discord.Embed(title = self.name, description = self.description, color = ctx.author.color)
		embed.add_field(name = f'Tier {self.tier}', value = '')
		embed.add_field(name = f'Hold {self.hold}', value = '')
		names = ""
		for contact in self.contacts:
			names += contact + "\n"
		embed.add_field(name = 'Contacts', value = names)
		embed.add_field(name = 'Status', value = f'{self.rep}')
		if self.notes != "":
			embed.add_field(name = "Notes", value = self.notes)
		if self.secret_notes != "":
			embed.add_field(name = "Secret Notes", value = self.secret_notes)
		if len(self.clocks) > 0:
			for clock in self.clocks:
				embed.add_field(name = f'Clock {clock.progress}/{clock.total}', value = clock.description)
		return embed

class Factions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.faction_list = []
		name = "Leviathan Hunters"
		tier = 5
		hold = 'S'
		rep = "+2"
		description = "These guys like leviathans, yo"
		notes = "They like dead bodies too"
		contacts = ["that one guy we know", "that other guy we also know"]
		secret_notes = "they **really** like leviathans"
		self.faction_list.append(Faction(name, tier, hold, rep, description, contacts, notes, secret_notes))
		self.faction_list[0].add_clock("tier up", 3, 8)
		self.faction_list[0].add_clock("butt stuff", 0, 12)

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
				

	@commands.command(aliases = ['f'])
	async def display_faction(self, ctx, *, name):
		await self.search_func(ctx, name, False)

	@commands.command(aliases = ['fg'])
	async def display_faction_gm(self, ctx, *, name):
		await self.search_func(ctx, name, True)	

async def setup(bot):
	await bot.add_cog(Factions(bot))
