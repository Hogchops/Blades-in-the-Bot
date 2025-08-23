import discord
from discord.ext import commands
from discord import app_commands
from faction_obj import Faction
from typing import List
import json
from pathlib import Path
import os

class Factions(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.factions: List[Faction] = []

    async def cog_load(self):
        folder = Path("Factions")
        if not folder.exists():
            print("Faction folder not found.")
            return
        
        for file in folder.glob("*.json"):
            try:
                with open(file, "r", encoding = "utf-8") as f:
                    data = json.load(f)
                    faction = Faction.from_dict(data)
                    self.factions.append(faction)
            except Exception as e:
                print(f"Error loading {file.name}: {e}")

    def is_owner():
        return commands.check(lambda ctx: ctx.author.id == 280116409852362754)
    
    def find_faction(self, title: str):
        for faction in self.factions:
            if faction.title == title:
                return faction
        return None
    
    @app_commands.command(name = "add-faction", description = "Create a faction.")
    @app_commands.describe(
        title = "Enter the faction title.",
        description = "Enter the faction description.",
        tier = "Enter the faction tier.",
        affiliation = "Enter the affiliation of the faction. Empire: 0, Hutt: 1, Rebel: 2",
        contact = "Enter the faction contact.",
        leader = "Enter the faction leader."
    )
    @is_owner()
    async def create_faction(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        tier: int,
        affiliation: int,
        contact: str,
        leader: str
    ):
        faction = Faction(title, description, tier, affiliation, contact, leader)
        self.factions.append(faction)

        folder = Path("Factions")
        filename = title.lower().replace(" ", "_") + ".json"
        filepath = folder / filename

        try:
            with open (filepath, "w", encoding = "utf-8") as f:
                json.dump(faction.to_dict(), f, indent=4)
            
            embed = faction.generate_embed()
            image = faction.get_image()
            embed.set_author(
                name = interaction.user.display_name,
                icon_url = interaction.user.display_icon.url
            )
            if image:
                embed.set_thumbnail(url = f"attachment://{image.filename}")
                await interaction.response.send_message(embed=embed, file=image, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to save faction: {e}")
    
    async def autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        choices = []
        for faction in self.factions:
            choices.append(faction.title)
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @app_commands.command(name = "faction", description = "View a faction.")
    @app_commands.autocomplete(title = autocomplete)
    @app_commands.describe(
        title = "Enter the faction title."
    )
    async def view_faction(self, interaction: discord.Interaction, title: str):
        faction = self.find_faction(title)
        if faction:
            embed = faction.generate_embed()
            image = faction.get_image()
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            if image:
                embed.set_thumbnail(url = f"attachment://{image.filename}")
                await interaction.response.send_message(embed = embed, file = image, ephemeral = True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"I could not find faction {title}.", ephemeral=True)
        
    @app_commands.command(name="remove-faction", description="Remove a faction.")
    @app_commands.autocomplete(title = autocomplete)
    @app_commands.describe(
        title = "The title of the faction you wish to remove."
    )
    @is_owner()
    async def delete_faction(self, interaction: discord.Interaction, title: str):
        faction = self.find_faction(title)
        if faction:
            self.factions.remove(faction)
            if os.path.exists(f"Factions/{title.lower().replace(' ', '_')}.json"):
                os.remove(f"Factions/{title.lower().replace(' ', '_')}.json")
                await interaction.response.send_message(f"Faction {title} successfully deleted.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Faction {title} removed but file not deleted.",ephemeral=True)
        else:
            await interaction.response.send_message(f"Faction {title} not found.")

async def setup(bot):
    await bot.add_cog(Factions(bot))