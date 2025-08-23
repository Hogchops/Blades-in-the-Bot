import discord
from discord.ext import commands
from discord import app_commands
from help_func import MyHelp

class HelpCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "help", description = "Show help for commands.")
    async def help_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title = "Help",
            description = "List of available commands",
            color = discord.Color.magenta()
        )
        embed.set_author(
            name = interaction.user.display_name,
            icon_url = interaction.user.display_avatar.url
        )

        for cog_name, cog in self.bot.cogs.items():
            commands_list = await self.get_cog_commands(cog)
            if commands_list:
                embed.add_field(name = cog_name, value = "\n".join(commands_list), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def get_cog_commands(self, cog):
        cmds = []
        for command in cog.get_commands():
            if getattr(command, "hidden", False):
                continue
            signature = f"/{command.name} {command.signature}" if hasattr(command, "signature") else f"/{command.name}"
            cmds.append(signature)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))