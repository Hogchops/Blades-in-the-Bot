import discord
import random
from dotenv import load_dotenv # type: ignore
from discord.ext import commands
from difflib import get_close_matches
from discord import app_commands
from typing import List

def generate_embed(interaction: discord.Interaction, dice, num, zero, position: str, effect: str):
	embed = discord.Embed(title = '', description = '', color = discord.Color.magenta())
	embed.set_author(name = interaction.user.display_name, icon_url = str(interaction.user.display_avatar.url))	
	rolls = ""
	for i in range(num - 1):
		rolls += str(dice[i]) + ", "
	rolls += str(dice[-1])
	num_dice = num
	if zero:
		num_dice = 0    
	embed.add_field(name = f'{num_dice}d6', value = rolls, inline = True)
	dice.sort()
	result_text = ""
	if not zero:
		result = dice[-1]
	else:
		result = dice[0]
	value = f'**{result}** '
	if result == 6:
		result_text = "Success"
		if num >= 2 and not zero:
			if dice[-2] == 6:
				value += ":white_check_mark:"
				result_text = "Critical"
		value += ":white_check_mark:"
	elif result == 4 or result == 5:
		value += ":warning:"
		result_text = "Partial"
	else:
		value += ":x:"
		result_text = "Fail"
	embed.add_field(name = f"{result_text}", value = value, inline = True)
	if position and effect:
		embed.description = f"{position}, {effect}"
	return embed

class Roll(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.gambits = 0
		self.gambit_msg = None
		self.gambit_channel = None

		for cmd in self.__cog_app_commands__:
			cmd.extras["cog"] = self.__cog_name__
	
	async def position_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
		choices = ["Desperate", "Risky", "Controlled"]
		return [
			app_commands.Choice(name = choice, value = choice)
			for choice in choices if current.lower() in choice.lower()
		]
	
	async def effect_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
		choices = ["Limited", "Standard", "Great"]
		return [
			app_commands.Choice(name = choice, value = choice)
			for choice in choices if current.lower() in choice.lower()
		]

	@app_commands.command(name = "r", description = "Roll some dice.") 
	@app_commands.describe(
		num = "Enter the number of dice you want to roll. Entering 0 will roll 2 dice.",
	)
	async def roll(self, interaction: discord.Interaction, num: int):
		zero = False
		if num == 0:
			num = 2
			zero = True
		dice = [random.choice(range(1,7)) for _ in range(num)]
		embed = generate_embed(interaction, dice, num, zero, None, None)
		await interaction.response.send_message(embed = embed)
	
	@app_commands.command(name = "roll", description = "Roll some dice with position, effect, and modify the gambit pool.")
	@app_commands.describe(
		num = "Enter the number of dice you want to roll. Entering 0 will roll 2 dice.",
		position = "Desperate, Risky, or Controlled.",
		effect = "Limited, Standard, or Great"
	)
	@app_commands.autocomplete(position = position_autocomplete)
	@app_commands.autocomplete(effect = effect_autocomplete)
	async def roll_expanded(self, interaction: discord.Interaction, num: int, position: str = "Risky", effect: str = "Standard"):
		zero = False
		if num == 0:
			num = 2
			zero = True
		dice = [random.choice(range(1,7)) for _ in range(num)]
		embed = generate_embed(interaction, dice, num, zero, position, effect)
		if position == "Risky" and self.gambit_msg and self.gambit_channel == interaction.channel_id:
			dice.sort()
			if not zero:
				result = dice[-1]
			else:
				result = dice[0]
			if result == 6:
				await self.change_gambit(interaction, 1)
				embed.set_footer(text="+1 gambit!")
		await interaction.response.send_message(embed = embed)
	
	@app_commands.command(name="groll", description="Roll and spend a gambit, giving you +1d.")
	@app_commands.describe(
		num = "Enter the original number of dice you wish to roll.",
		position = "Desperate, Risky, or Controlled.",
		effect = "Limited, Standard, or Great"
	)
	@app_commands.autocomplete(position = position_autocomplete)
	@app_commands.autocomplete(effect = effect_autocomplete)
	async def gambit_roll(self, interaction: discord.Interaction, num: int, position: str = "Risky", effect: str = "Standard"):
		num += 1
		dice = [random.choice(range(1,7)) for _ in range(num)]
		embed = generate_embed(interaction, dice, num, False, position, effect)
		embed.set_footer(text = "-1 gambit!")
		await self.change_gambit(interaction, -1)
		await interaction.response.send_message(embed = embed)

	@app_commands.command(name = "gr", description = "Roll hidden dice.")
	@app_commands.describe(
		num = "Enter the number of dice you want to roll. Entering 0 will roll 2 dice.",
	)
	@app_commands.default_permissions(administrator=True)
	async def gr(self, interaction: discord.Interaction, num: int):
		zero = False
		if num == 0:
			num = 2
			zero = True
		dice = [random.choice(range(1,7)) for _ in range(num)]
		embed = generate_embed(interaction, dice, num, zero, None, None)
		await interaction.response.send_message(embed = embed, ephemeral = True)

	def generate_gambit_embed(self, interaction: discord.Interaction):
		embed = discord.Embed(
			title = "Gambit Pool",
			color = discord.Color.magenta()
		)
		embed.add_field(name=' '.join('🎲' for _ in range(self.gambits)), value="")
		embed.set_author(
			name = interaction.user.display_name,
			icon_url = interaction.user.display_avatar.url
		)
		return embed
	
	async def change_gambit(self, interaction: discord.Interaction, change: int):
		self.gambits += change
		if self.gambits < 0:
			self.gambits = 0
		elif self.gambits > 8:
			self.gambits = 8
		await self.modify_gambit_message(interaction)

	async def modify_gambit_message(self, interaction: discord.Interaction):
		if self.gambit_msg and self.gambit_channel:
			try:
				old_channel = await self.bot.fetch_channel(self.gambit_channel)
				msg = await old_channel.fetch_message(self.gambit_msg)
				embed = self.generate_gambit_embed(interaction)
				embed.set_author(
					name = interaction.user.display_name,
					icon_url = interaction.user.display_avatar.url
				)
				await msg.edit(embed = embed)
			except Exception as e:
				print(f"Could not edit old gambit message: {e}")
	
	@app_commands.command(name = "gambit-pool", description = "Create the gambit pool.")
	@app_commands.describe(
		initial_value = "Number of gambits for the pool to start with.",
	)
	@app_commands.default_permissions(administrator=True)
	async def gambit_pool(self, interaction: discord.Interaction, initial_value: int = 0):
		if self.gambit_msg and self.gambit_channel:
			try:
				old_channel = await self.bot.fetch_channel(self.gambit_channel)
				if old_channel:
					msg = await old_channel.fetch_message(self.gambit_msg)
					await msg.delete()
			except Exception as e:
				pass
		self.gambits = initial_value
		embed = self.generate_gambit_embed(interaction)
		await interaction.response.send_message(embed = embed)
		msg = await interaction.original_response()
		await msg.pin()
		self.gambit_msg = msg.id
		self.gambit_channel = interaction.channel.id
		
	@app_commands.command(name = "spend", description = "Spend a gambit")
	async def gambit_spend(self, interaction: discord.Interaction):
		if self.gambit_msg and self.gambit_channel:
			await self.change_gambit(interaction, -1)
			await interaction.response.send_message(f"You spent a gambit! You're now at {self.gambits}.", ephemeral=True)
		else:
			await interaction.response.send_message("There's no gambit pool to modify!", ephemeral=True)
	
	@app_commands.command(name = "add", description = "Add a gambit.")
	async def gambit_add(self, interaction: discord.Interaction):
		if self.gambit_msg and self.gambit_channel:
			await self.change_gambit(interaction, 1)
			await interaction.response.send_message(f"You added a gambit! You're now at {self.gambits}.", ephemeral=True)
		else:
			await interaction.response.send_message("There's no gambit pool to modify!", ephemeral=True)

	@app_commands.command(name = "how-to-roll", description="How to roll.")
	async def roll_help(self, interaction: discord.Interaction):
		embed = discord.Embed(
			title = "How to Roll",
			description = "`/r [n]` for a basic nd6 roll.\n\n`/roll [n] <position> <effect>` for an advanced roll that will modify the gambit pool.\n\n"
			"`/groll [n] <position> <effect>` for a (n+1)d6 roll, since you're spending a gambit!",
			color = discord.Color.magenta()
		)
		embed.add_field(name="Modifying the Gambit Pool Directly", value="You can modify the pool directly by using:\n`/add` to add a gambit\n`/spend` to spend a gambit.")
		embed.add_field(name="Position and Effect",value="The `/roll` and `/groll` commands will assume risky/standard.\nMake sure to choose different values if you need to roll otherwise!")
		embed.set_author(
			name = interaction.user.display_name,
			icon_url = interaction.user.display_avatar.url
		)
		await interaction.response.send_message(embed = embed, ephemeral=True)

	@app_commands.command(name="engagement", description="List engagement information.")
	async def engagement(self, interaction: discord.Interaction):
		embed = discord.Embed(
			title = "Engagement",
			description = "Start with 1d for sheer luck!",
			color = discord.Color.magenta()
		)
		embed.add_field(name="Is this operation particularly bold or daring? Take +1d. Is this operation overly complex or contingent on many factors? Take -1d.", value="")
		embed.add_field(name="Does the plan's detail expose a vulnerability of the target or hit them where they're weakest? Take +1d. Is the target strongest against this approach, or do they have particular defenses or special preparations? Take -1d.", value="")
		embed.add_field(name="Can any of your friends or contacts provide aid or insight for this operation? Take +1d. Are any enemies or rivals interfering in the operation? Take -1d.", value="")
		embed.add_field(name="Are there any other elements that you want to consider? Maybe a lower-Tier target will give you +1d. Maybe a higher-Tier target will give you -1d. Maybe there's a situation in the system that makes the operation more or less tricky.", value="")
		embed.set_author(
			name = interaction.user.display_name,
			icon_url = interaction.user.display_avatar.url
		)
		await interaction.response.send_message(embed = embed)

async def setup(bot):
	await bot.add_cog(Roll(bot)) 