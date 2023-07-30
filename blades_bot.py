import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

bot = commands.Bot(command_prefix = '=', intents=intents)

@bot.event
async def on_ready():
	await load_cogs()
	await setup_hook()
	print(f'{bot.user} has connected to Discord!')

async def setup_hook():
	await bot.tree.sync(guild = discord.Object(id = 807855936106135562))
	print(f'Synced slash commands for the guild.')

@bot.event
async def on_command_error(ctx, error):
	await ctx.send(f"An error has occurred: {str(error)}")

async def load_cogs():
	await bot.load_extension("roll")
	await bot.load_extension("factions")
	await bot.load_extension("game_clocks")
	await bot.load_extension("movies")	

@tree.command(name = "help", with_app_command = True, description = "Display a help page.")
@app_commands.guilds(discord.Object(id = 807855936106135562))
async def test(interaction: discord.Interaction):
	await interaction.response.defer(ephemeral = True)
	embed = discord.Embed(title = "Blades in the Bot", description="Play Blades in the Dark or more Forged in the Dark games over discord! Features faction displaying, clock management, as well as standard rolling (with some other features thrown in for good measure).\nFor more assistance, please use `=help` for a list of the commands.")
	embed.set_author(name = interaction.message.author.display_name, icon_url = str(interaction.message.author.display_avatar.url))
	embed.add_field(name = "Slash Commands", value = "Blades in the Bot is fully equipped with discord's *slash commands*. It is recommended that you use them since it comes equipped with autocomplete and fillable parameter forms when you wish to execute a command. However, you can use the `=` prefix for commands as well. These two commands have the same output: `=r 2` and `/r 2`.")
	embed.add_field(name = "Rolling", value = "Blades in the Bot can help you roll dice, and is pre-programmed with *Forged in the Dark* dice rolling mechanics. Use `/r [num]` to roll `num` amount of dice, including zero. The result will indicate whether you received a failure, mixed, success, or critical success. It will also display the values of each die rolled.")
	embed.add_field(name = "Factions", value = "Blades in the Bot handles faction information well. The GM will establish various factions, and you can view the public information by using `/faction [name]`.")
	embed.add_field(name = "Clocks", value = "During play, you may wish to create some clocks. Blades in the Bot can create clocks using the `/clock` command, and can tick clocks using the `/tick` command. There are other features as well.")
	embed.add_field(name = "Bugs and Errors", value = "If I roll eels (bug), please contact the developer `hogchops` with the commands and inputted values, as well as the error message.")
	await interaction.response.send_message(embed = embed)

bot.run(TOKEN)