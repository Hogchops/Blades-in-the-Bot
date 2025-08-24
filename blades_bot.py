import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from help_func import MyHelp

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix = '=', intents=intents)

@bot.event
async def on_ready():
	await load_cogs()
	await setup_hook()
	print(f'{bot.user} has connected to Discord!')

async def setup_hook():
	#guild = discord.Object(id = 807855936106135562)
	#bot.tree.clear_commands(guild=guild)
	await bot.tree.sync()#

@bot.event
async def on_command_error(ctx, error):
	await ctx.send(f"An error has occurred: {str(error)}")

async def load_cogs():
	await bot.load_extension("cogs.roll-cog")
	await bot.load_extension("cogs.signup-cog")
	await bot.load_extension("cogs.clocks-cog")
	await bot.load_extension("cogs.help-cog")
	await bot.load_extension("cogs.faction-cog")
	await bot.load_extension("cogs.sheets-cog")
	
bot.help_command = MyHelp()
bot.run(TOKEN)