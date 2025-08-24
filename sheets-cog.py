import discord
from discord.ext import commands
from discord import app_commands
from signup_interaction import SignupButtons
import gspread
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

    
    @app_commands.command(name="heat", description="List the heat and wanted levels of all the systems.")
    async def heat(self, interaction: discord.Interaction):
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

        print(f"A heat: {a_heat}, A wanted: {a_wanted}")
    
async def setup(bot):
    await bot.add_cog(Sheets(bot))