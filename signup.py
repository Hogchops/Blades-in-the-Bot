import discord
from discord.ext import commands
from discord import app_commands
from signup_interaction import SignupButtons
from week import Week

class Signup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.week = Week()

    @commands.hybrid_command(name="signup", description="Create the signup embed for the week.")
    async def get_signups(self, ctx: commands.Context):
        self.week = Week()
        await ctx.defer(ephemeral=True)
        embed = self.week.generate_embed()
        msg = await ctx.send(embed=embed)
        await ctx.send("Press the button to signup for that day. Press each button that you would be willing to make. When a day fills up to 4, you will be locked in for that day.\n\nTo remove your name from a day, press the button again.", view = SignupButtons(self.bot, ctx, msg, self.week))

async def setup(bot):
    await bot.add_cog(Signup(bot))