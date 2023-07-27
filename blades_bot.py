import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
blades_bot_filepath = r"C:\Users\admin\Desktop\blades-bot"

bot = commands.Bot(command_prefix = '=', intents=intents)

@bot.event
async def on_ready():
	await load_cogs()
	print(f'{bot.user} has connected to Discord!')

async def load_cogs():
	await bot.load_extension("roll")
	await bot.load_extension("factions")
	# await bot.load_extension("greetings")

bot.run(TOKEN)
