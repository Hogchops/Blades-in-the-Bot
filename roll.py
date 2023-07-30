import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from difflib import get_close_matches
from discord import app_commands
from discord.ext.commands import Context

def generate_embed(ctx, dice, num, zero, checking_result, num_dice_sides):
	embed = discord.Embed(title = '', description = '', color = discord.Color.magenta())
	embed.set_author(name = ctx.author.display_name, icon_url = str(ctx.author.display_avatar.url))	
	rolls = ""
	for i in range(num - 1):
		rolls += dice[i] + ", "
	rolls += dice[-1]
	num_dice = num
	if zero:
		num_dice = 0    
	embed.add_field(name = f'{num_dice}d{num_dice_sides}', value = rolls, inline = True)
	if checking_result:	
		dice.sort()
		if not zero:
			result = int(dice[-1])
		else:
			result = int(dice[0])
		value = f'**{result}** '
		if result == 6:
			if num >= 2:
				if int(dice[-2]) == 6:
					value += ":white_check_mark:"
			value += ":white_check_mark:"
		elif result == 4 or result == 5:
			value += ":warning:"
		else:
			value += ":x:"
		embed.add_field(name = "Result", value = value, inline = False)
	else:
		total = 0
		for d in dice:
			total += int(d)
		value = f"**{total}**"
		embed.add_field(name = "Total", value = value, inline = False)
	return embed

class Roll(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(name = "r", aliases = ["roll"], description = "Roll some dice.") 
	#@app_commands.guilds(discord.Object(id = 807855936106135562))
	@app_commands.describe(
		num = "Enter the number of dice you want to roll. Entering 0 will roll 2 dice.",
		num_dice_sides = "Enter the number of sides for each die. If you leave this blank or enter 6, we will provide results along with your role."
	)
	async def roll(self, ctx, num: int, num_dice_sides: int = 6):
		zero = False
		if num == 0:
			num = 2
			zero = True
		dice = [str(random.choice(range(1,num_dice_sides + 1))) for _ in range(num)]
		if num_dice_sides == 6:
			checking_result = True
		else:
			checking_result = False
		embed = generate_embed(ctx, dice, num, zero, checking_result, num_dice_sides)
		await ctx.send(embed = embed)

async def setup(bot):
	await bot.add_cog(Roll(bot)) 