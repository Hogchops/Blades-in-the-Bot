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
    
async def setup(bot):
    await bot.add_cog(Sheets(bot))