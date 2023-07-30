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

class MyHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=discord.Color.blurple())

        for cog, commands in mapping.items():
           filtered = await self.filter_commands(commands, sort=True)
           command_signatures = [self.get_command_signature(c) for c in filtered]

           if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

bot.help_command = MyHelp()

bot.run(TOKEN)