import discord
from discord.ext import commands
from discord import app_commands
from signup_interaction import SignupButtons
from week import Week
from typing import List
import json

class Signup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.week = None
        self.session_confirmed = 4
        self.saved_channel_id = None
        self.saved_embed_id = None
        self.saved_view_id = None

    async def cog_load(self):
        guild = await self.bot.fetch_guild(807855936106135562)
        try:
            with open("signup_state.json", "r") as f:
                data = json.load(f)
                self.saved_channel_id = data["channel_id"]
                self.saved_embed_id = data["embed_id"]
                self.saved_view_id = data["view_id"]
                self.week = await Week.from_dict(data["week"], guild) 
            if self.saved_channel_id and self.saved_view_id and self.saved_embed_id:
                try:
                    channel = await self.bot.fetch_channel(self.saved_channel_id)
                    view_msg = await channel.fetch_message(self.saved_view_id)
                    self.bot.add_view(SignupButtons(self.bot, self.week, self.saved_channel_id, self.saved_embed_id, self.saved_view_id))
                    print(f"Signup restored on message {view_msg.id}")
                except discord.NotFound:
                    print(f"Channel {self.saved_channel_id} not found. Skipping restore.")
                    return
        except FileNotFoundError:
            self.week = Week()
        except Exception as e:
            print("Could not restore signup:", e)
        
    def is_owner():
        return commands.check(lambda ctx: ctx.author.id == 280116409852362754)
    
    @commands.hybrid_command(name="signup", description="Create the signup embed for the week.")
    @is_owner()
    async def get_signups(self, ctx: commands.Context):
        if self.saved_channel_id and self.saved_view_id and self.saved_embed_id:
            try:
                old_channel = await self.bot.fetch_channel(self.saved_channel_id)
                if old_channel:
                    old_view = await old_channel.fetch_message(self.saved_view_id)
                    old_embed = await old_channel.fetch_message(self.saved_embed_id)
                    await old_view.delete()
                    await old_embed.delete()
            except Exception as e:
                print(f"Could not delete the old signup message: {e}")

        self.week = Week()

        msg = await ctx.send(embed=self.week.generate_embed())
        self.saved_channel_id = msg.channel.id
        self.saved_embed_id = msg.id

        view_msg = await ctx.send("@everyone Signups are active for the next calendar week. Press a button to signup for the corresponding day. The times for all days are set at **7:00 pm EST**. Sign up for each day that you would be willing to make. When a day fills up to 4, you will be locked in for that day.\n\nTo remove your name from a day, press the button again.",
                       allowed_mentions=discord.AllowedMentions(everyone=True))
        self.saved_view_id = view_msg.id
                       
        view = SignupButtons(self.bot, self.week, self.saved_channel_id, self.saved_embed_id, self.saved_view_id)     
        await view_msg.edit(view=view)


        state = {
            "channel_id": msg.channel.id,
            "embed_id": self.saved_embed_id,
            "view_id": self.saved_view_id,
            "week": self.week.to_dict()
        }
        with open("signup_state.json", "w") as f:
            json.dump(state, f)

    async def autocomplete_dotw(self, inter: discord.integrations.Integration, current: str) -> List[app_commands.Choice[str]]:
        choices = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @commands.hybrid_command(name="sr", description="Remove someone from a confirmed list.")
    @app_commands.autocomplete(day = autocomplete_dotw)
    @is_owner()
    async def remove(self, ctx: commands.Context, name: discord.User, day: str):
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

    @commands.hybrid_command(name="sessions", description="List sessions.")
    @is_owner()
    async def sessions(self, ctx: commands.Context):
        day_dict = {
                "sunday": self.week.sunday,
                "monday": self.week.monday,
                "tuesday": self.week.tuesday,
                "wednesday": self.week.wednesday,
                "thursday": self.week.thursday,
                "friday": self.week.friday,
                "saturday": self.week.saturday
        }
        dotw = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        week_dates = self.week.get_next_week_dates()
        date_index = 0
        for d in dotw:
            day_list = day_dict[d]
            if day_list.__len__() >= self.session_confirmed:
                msg = f"## Session Announcement: {d.title()} {week_dates[date_index].strftime('%m/%d')}\n"
                for user in day_list:
                    msg += user.mention + "\n"
                await ctx.channel.send(msg)
            date_index += 1
        
async def setup(bot):
    await bot.add_cog(Signup(bot))