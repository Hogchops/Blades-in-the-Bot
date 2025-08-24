import discord
from discord import app_commands
from discord.ext import commands

class Admin(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "clear-channel", description="Delete all messages in a channel.")
    @app_commands.default_permissions(administrator=True)
    async def clear_channel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel

        try:
            deleted = await channel.purge(limit=None)
            await interaction.followup.send(f"Deleted {len(deleted)} messages from {channel.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to delete messages.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to delete messages: {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))