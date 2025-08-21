import discord
from discord.ext import commands
from discord import app_commands
from signup_interaction import SignupButtons
from week import Week
from typing import List

class Signup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.week = Week()
        self.embed_msg = None

    @commands.hybrid_command(name="signup", description="Create the signup embed for the week.")
    async def get_signups(self, ctx: commands.Context):
        self.week = Week()
        embed = self.week.generate_embed()
        msg = await ctx.send(embed=embed)
        self.embed_msg = msg
        await ctx.send("Press the button to signup for that day. Press each button that you would be willing to make. When a day fills up to 4, you will be locked in for that day.\n\nTo remove your name from a day, press the button again.", view = SignupButtons(self.bot, ctx, msg, self.week))

    async def autocomplete_dotw(self, inter: discord.integrations.Integration, current: str) -> List[app_commands.Choice[str]]:
        choices = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @commands.hybrid_command(name="schedule remove", aliases=["r"], description="Remove someone from a confirmed list.")
    @app_commands.autocomplete(day = autocomplete_dotw)
    async def remove(self, ctx: commands.Context, name: str, day: str):
        if ctx.author.get_role(814732436054867968) != None:
            day_dict = {
                "sunday": self.week.sunday,
                "monday": self.week.monday,
                "tuesday": self.week.tuesday,
                "wednesday": self.week.wednesday,
                "thursday": self.week.thursday,
                "friday": self.week.friday,
                "saturday": self.week.saturday
            }
            day_list = day_dict[day.lower()]
            if name in day_list:
                day_list.remove(name)
                await self.embed_msg.edit(embed=self.week.generate_embed())
        else:
            await ctx.send("You do not have permissions for this.", ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(Signup(bot))