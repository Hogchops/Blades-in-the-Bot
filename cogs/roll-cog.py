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
	if not zero:
		result = dice[-1]
	else:
		result = dice[0]
	value = f'**{result}** '
	if result == 6:
		if num >= 2 and not zero:
			if dice[-2] == 6:
				value += ":white_check_mark:"
		value += ":white_check_mark:"
	elif result == 4 or result == 5:
		value += ":warning:"
	else:
		value += ":x:"
	embed.add_field(name = "Result", value = value, inline = True)
	if position != "" and effect != "":
		embed.add_field(name = f"{position}\n{effect}", value = "", inline = False)
	return embed

class Roll(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

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
		position = "Desperate, Risky, or Controlled.",
		effect = "Limited, Standard, or Greater"
	)
	@app_commands.autocomplete(position = position_autocomplete)
	@app_commands.autocomplete(effect = effect_autocomplete)
	async def roll(self, interaction: discord.Interaction, num: int, position: str = "Risky", effect: str = "Standard"):
		zero = False
		if num == 0:
			num = 2
			zero = True
		dice = [random.choice(range(1,7)) for _ in range(num)]
		embed = generate_embed(interaction, dice, num, zero, position, effect)
		await interaction.response.send_message(embed = embed)

	@app_commands.command(name = "gr", description = "Roll hidden dice.")
	@app_commands.describe(
		num = "Enter the number of dice you want to roll. Entering 0 will roll 2 dice.",
		num_dice_sides = "Enter the number of sides for each die. If you leave this blank or enter 6, we will provide results along with your role."
	)
	@app_commands.default_permissions(administrator=True)
	async def groll(self, interaction: discord.Interaction, num: int, num_dice_sides: int = 6):
		zero = False
		if num == 0:
			num = 2
			zero = True
		dice = [random.choice(range(1,num_dice_sides + 1)) for _ in range(num)]
		if num_dice_sides == 6:
			checking_result = True
		else:
			checking_result = False
		embed = generate_embed(interaction, dice, num, zero, checking_result, num_dice_sides)
		await interaction.response.send_message(embed = embed, ephemeral = True)
	
async def setup(bot):
	await bot.add_cog(Roll(bot)) 