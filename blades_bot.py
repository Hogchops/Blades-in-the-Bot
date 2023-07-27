import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from roll import Roll

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

blades_bot_filepath = r"C:\Users\admin\Desktop\blades-bot"

client = discord.Client()
bot = commands.Bot(command_prefix = '=')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


bot.add_cog(Roll(bot))

bot.run(TOKEN)