from discord.ext import commands
from discord import app_commands
import discord
from help_func import MyHelp

class HelpCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "help", description = "Show help for commands.")
    async def help_slash(self, interaction: discord.Interaction):
        help_cmd = MyHelp()
        help_cmd.context = await self.bot.get_context(interaction)

        await help_cmd.send_bot_help(self.bot.cogs)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))