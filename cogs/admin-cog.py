import discord
from discord import app_commands
from discord.ext import commands

class Admin(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.notes = []

        for cmd in self.__cog_app_commands__:
            cmd.extras["cog"] = self.__cog_name__

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

    @app_commands.command(name = "note", description = "Make an gm note.")
    @app_commands.default_permissions(administrator=True)
    async def note(self, interaction: discord.Interaction, content: str):
        self.notes.append(content)
        await interaction.response.send_message("Note saved.", ephemeral=True)
    
    @app_commands.command(name = "list-notes", description="List all notes.")
    @app_commands.default_permissions(administrator=True)
    async def list_notes(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title = "GM Notes",
            color = discord.Color.magenta()
        )
        for i, note in enumerate(self.notes, 1):
            embed.add_field(name = f"Note {i}", value = note[:1024], inline=False)
        await interaction.response.send_message(embed = embed, ephemeral=True)
    
    @app_commands.command(name = "delete-notes", description="Delete the notes.")
    @app_commands.default_permissions(administrator=True)
    async def delete_notes(self, interaction: discord.Interaction):
        self.notes = []
        await interaction.response.send_message("Notes deleted.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))