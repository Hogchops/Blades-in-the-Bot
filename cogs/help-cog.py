import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict

class HelpCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name = "help", description = "Show help for commands.") 
    async def help_slash(self, interaction: discord.Interaction):
        if interaction.guild and isinstance(interaction.user, discord.Member):
            is_admin = interaction.user.guild_permissions.administrator
        else:
            is_admin = False
        is_owner = interaction.user.id == 280116409852362754

        def is_command_visible(cmd: app_commands.Command):
            default_perms = getattr(cmd, "default_permissions", None)
            if default_perms is not None and default_perms.administrator:
                return is_admin or is_owner
            return True
        
        grouped_commands: Dict[str, List[app_commands.Command]] = {}
        for cmd in self.bot.tree.get_commands():
            if is_command_visible(cmd):
                cog_name = cmd.extras.get("cog", "Uncategorized")
                grouped_commands.setdefault(cog_name, []).append(cmd)
        
        embed = discord.Embed(
            title = "Help",
            description = "List of available commands",
            color = discord.Color.magenta()
        )
        embed.set_author(
            name = interaction.user.display_name,
            icon_url = interaction.user.display_avatar.url
        )
        
        for cog_name, cmds in grouped_commands.items():
            value = "\n".join(f"`/{cmd.name}` - {cmd.description or 'No description.'}" for cmd in cmds)
            embed.add_field(name = f"{cog_name}", value=value, inline=False)
            
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