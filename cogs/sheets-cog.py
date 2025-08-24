import discord
from discord.ext import commands
from discord import app_commands
from interactions.signup_interaction import SignupButtons
import gspread
from typing import List
from oauth2client.service_account import ServiceAccountCredentials

class Sheets(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        creds = ServiceAccountCredentials.from_json_keyfile_name("patrickbot-269c09afae39.json", self.scope)
        client = gspread.authorize(creds)

        self.alderaan = client.open("Planets and Sectors").worksheet("Alderaan")
        self.coruscant = client.open("Planets and Sectors").worksheet("Coruscant")
        self.kuat = client.open("Planets and Sectors").worksheet("Kuat")
        self.mygeeto = client.open("Planets and Sectors").worksheet("Mygeeto")
        self.narshaddaa = client.open("Planets and Sectors").worksheet("Nar Shaddaa")
        self.ordmantell = client.open("Planets and Sectors").worksheet("Ord Mantell")
        self.frontier = client.open("Planets and Sectors").worksheet("Frontier Worlds")

        self.alderaan_link = "https://docs.google.com/spreadsheets/d/1L4QFtJcSucSgeBAxdpLM4tIAwiZDyeSsmTXeub7iJEQ/edit?gid=1024827348#gid=1024827348"
        self.coruscant_link = "https://docs.google.com/spreadsheets/d/1L4QFtJcSucSgeBAxdpLM4tIAwiZDyeSsmTXeub7iJEQ/edit?gid=1910238740#gid=1910238740"
        self.kuat_link = "https://docs.google.com/spreadsheets/d/1L4QFtJcSucSgeBAxdpLM4tIAwiZDyeSsmTXeub7iJEQ/edit?gid=1464517251#gid=1464517251"
        self.mygeeto_link = "https://docs.google.com/spreadsheets/d/1L4QFtJcSucSgeBAxdpLM4tIAwiZDyeSsmTXeub7iJEQ/edit?gid=285102036#gid=285102036"
        self.narshaddaa_link = "https://docs.google.com/spreadsheets/d/1L4QFtJcSucSgeBAxdpLM4tIAwiZDyeSsmTXeub7iJEQ/edit?gid=310258739#gid=310258739"
        self.ordmantell_link = "https://docs.google.com/spreadsheets/d/1L4QFtJcSucSgeBAxdpLM4tIAwiZDyeSsmTXeub7iJEQ/edit?gid=1650912478#gid=1650912478"
        self.frontier_link = "https://docs.google.com/spreadsheets/d/1L4QFtJcSucSgeBAxdpLM4tIAwiZDyeSsmTXeub7iJEQ/edit?gid=1591646957#gid=1591646957"

    def planet_dict(self, planet_name: str):
        planet_sheet = getattr(self, planet_name.lower().replace(" ", ''))
        return {
            "title": planet_sheet.acell("G17").value,
            "heat": planet_sheet.acell("G19").value,
            "wanted": planet_sheet.acell("I19").value,
            "agency": planet_sheet.acell("K19").value,
            "description": planet_sheet.acell("G24").value,
            "modifier": planet_sheet.acell("G30").value,
            "progress": planet_sheet.acell("J34").value,
            "total": planet_sheet.acell("L34").value,
            "fp": f"Systems/{planet_name.lower().replace(' ', '_')}.jpg",
            "fn": f"{planet_name.lower().replace(' ', '_')}.jpg"
        }

    def is_owner():
        return commands.check(lambda ctx: ctx.author.id == 280116409852362754)
    
    async def autocomplete_planets(self, inter: discord.integrations.Integration, current: str) -> List[app_commands.Choice[str]]:
        choices = ["Alderaan", "Coruscant", "Kuat", "Mygeeto", "Nar Shaddaa", "Ord Mantell", "Frontier"]
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]
    
    async def send_planet_embed(self, interaction: discord.Interaction, planet_name: str):
        planet = getattr(self, planet_name.lower().replace(" ", ''))
        if planet:
            planet_dict = self.planet_dict(planet_name)
            if planet_dict["agency"] == "ISB":
                color = discord.Color.light_grey()
            elif planet_dict["agency"] == "The Eye":
                color = discord.Color.orange()
            else:
                color = discord.Color.magenta()
            embed = discord.Embed(
                title = planet_dict["title"],
                description = planet_dict["description"],
                color = color
            )
            embed.set_author(
                name = interaction.user.display_name,
                icon_url = interaction.user.display_avatar.url
            )
            planet_name = planet_name.lower().replace(' ', '')
            embed.add_field(name="Planet Modifier", value=planet_dict["modifier"], inline=False)
            embed.add_field(name="Heat:", value=planet_dict["heat"], inline=True)
            embed.add_field(name="Wanted:", value=planet_dict["wanted"], inline=True)
            embed.add_field(name="Agency:", value=planet_dict["agency"], inline=True)
            embed.add_field(name="Sheet: ", value=f"[link]({getattr(self, f'{planet_name}_link')})")
            embed.add_field(name="Wanted Clock:", value=f"{planet_dict['progress']}/{planet_dict['total']}", inline=True)
            fp = planet_dict["fp"]
            fn = planet_dict["fn"]
            file = discord.File(fp, fn)
            embed.set_image(url = f"attachment://{fn}")
            await interaction.followup.send(embed=embed, file=file, ephemeral=True)

    @app_commands.command(name="planet", description="List the information for a planet.")
    @app_commands.describe(
        planet_name = "Enter a planet name."
    )
    @app_commands.autocomplete(planet_name = autocomplete_planets)
    async def planet(self, interaction: discord.Interaction, planet_name: str):
        await interaction.response.defer()
        await self.send_planet_embed(interaction, planet_name)

    async def send_heat_embed(self, interaction: discord.Interaction):
        a_heat = self.alderaan.acell("G19").value
        a_wanted = self.alderaan.acell("I19").value
        c_heat = self.coruscant.acell("G19").value
        c_wanted = self.coruscant.acell("I19").value
        k_heat = self.kuat.acell("G19").value
        k_wanted = self.kuat.acell("I19").value
        m_heat = self.mygeeto.acell("G19").value
        m_wanted = self.mygeeto.acell("I19").value
        n_heat = self.narshaddaa.acell("G19").value
        n_wanted = self.narshaddaa.acell("I19").value
        o_heat = self.ordmantell.acell("G19").value
        o_wanted = self.ordmantell.acell("I19").value
        f_heat = self.frontier.acell("G19").value
        f_wanted = self.frontier.acell("I19").value

        embed = discord.Embed(
            title = "Heat and Wanted Levels",
            color = discord.Color.light_grey()
        )
        embed.set_author(
            name = interaction.user.display_name,
            icon_url = interaction.user.display_avatar.url
        )

        embed.add_field(name = "Alderaan", value = f"H: {a_heat}\nW: {a_wanted}")
        embed.add_field(name = "Coruscant", value = f"H: {c_heat}\nW: {c_wanted}")
        embed.add_field(name = "Kuat", value = f"H: {k_heat}\nW: {k_wanted}")
        embed.add_field(name = "Mygeeto", value = f"H: {m_heat}\nW: {m_wanted}")
        embed.add_field(name = "Nar Shaddaa", value = f"H: {n_heat}\nW: {n_wanted}")
        embed.add_field(name = "Ord Mantell", value = f"H: {o_heat}\nW: {o_wanted}")
        embed.add_field(name = "Frontier Worlds", value = f"H: {f_heat}\nW: {f_wanted}")
        fp = "FactionImages/empire.jpg"
        fn = "empire.jpg"
        file = discord.File(fp, fn)
        embed.set_thumbnail(url = f"attachment://{fn}")
        await interaction.followup.send(embed=embed, file=file, ephemeral=True)

    @app_commands.command(name="heat", description="List the heat and wanted levels of all the systems.")
    async def heat(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.send_heat_embed(interaction)

    @app_commands.command(name="add-heat", description="Add heat to a system.")
    @app_commands.describe(
        planet_name = "Enter a planet name.",
        heat = "Enter an amount of heat you wish to add."
    )
    @app_commands.autocomplete(planet_name = autocomplete_planets)
    @is_owner()
    async def add_heat(self, interaction: discord.Interaction, planet_name: str, heat: int):
        await interaction.response.defer()
        old_planet_name = planet_name
        planet_name = planet_name.lower().replace(' ', '')
        planet_sheet = getattr(self, planet_name)
        current_heat = int(planet_sheet.acell("G19").value)

        if heat >= 0:
            if current_heat + heat >= 7:
                new_heat = current_heat + heat - 7
                old_wanted_level = planet_sheet.acell("I19").value
                planet_sheet.update_acell("G19",  new_heat)
                if old_wanted_level < 3:
                    planet_sheet.update_acell("I19", old_wanted_level + 1)
            else:
                new_heat = current_heat + heat
                planet_sheet.update_acell("G19", new_heat)
        else:
            if current_heat + heat < 0:
                new_heat = 7 - current_heat + heat
                old_wanted_level = planet_sheet.acell("I19").value
                planet_sheet.update_acell("G19", new_heat)
                if old_wanted_level > 0:
                    planet_sheet.update_acell("I19", old_wanted_level - 1)
            else:
                new_heat = current_heat + heat
                planet_sheet.update_acell("G19", new_heat)
        await self.send_heat_embed(interaction)
    
async def setup(bot):
    await bot.add_cog(Sheets(bot))