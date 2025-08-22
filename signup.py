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
        self.week = Week()
        self.session_confirmed = 4
        self.saved_channel_id = None
        self.saved_embed_id = None
        self.saved_view_id = None

        try:
            with open("signup_state.json", "r") as f:
                data = json.load(f)
                self.saved_channel_id = data["channel_id"]
                self.saved_embed_id = data["embed_id"]
                self.saved_view_id = data["view_id"]
                self.week = Week.from_dict(data["week"])
        except FileNotFoundError:
            pass

    async def cog_load(self):
        if self.saved_channel_id and self.saved_view_id and self.saved_embed_id:
            channel = self.bot.get_channel(self.saved_channel_id)
            if channel:
                try:
                    view_msg = await channel.fetch_message(self.saved_view_id)
                    self.bot.add_view(SignupButtons(self.bot, self.week), message_id=view_msg.id)
                    print(f"Signup restored on message {view_msg.id}\n")
                except Exception as e:
                    print("Could not restore signup:", e)
    
    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(title = "Session Signups", description = "If you see your name listed under a day, you are signed up for that day. All times are 7:00 pm EST.", color = discord.Color.blurple())
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        week_dates = self.week.get_next_week_dates()
        for i in range(7):
            name = f"__{days[i]}__ __{week_dates[i].strftime('%m/%d')}__"
            embed.add_field(name = name, value = self.day_string(days[i]))
        return embed
    
    def day_string(self, day: str) -> str:
        day_list = self.week.day_dict[day.lower()]
        output = ""
        k = 1
        guild = self.bot.get_guild(807855936106135562)
        if not guild:
            return "(Could not fetch guild)"
        for i in day_list:
            member = guild.get_member(i)
            if member:
                output += f"{k}: {member.display_name}\n"
            else:
                output += f"{k}: <Unknown User {i}>\n"
        return output

    @commands.hybrid_command(name="signup", description="Create the signup embed for the week.")
    async def get_signups(self, ctx: commands.Context):
        if self.saved_channel_id and self.saved_view_id and self.saved_embed_id:
            try:
                old_channel = self.bot.get_channel(self.saved_channel_id)
                if old_channel:
                    old_view = await old_channel.fetch_message(self.saved_view_id)
                    old_embed = await old_channel.fetch_message(self.saved_embed_id)
                    await old_view.delete()
                    await old_embed.delete()
            except Exception as e:
                print(f"Could not delete the old signup message: {e}")

        self.week = Week()

        msg = await ctx.send(embed=self.generate_embed())
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
    async def remove(self, ctx: commands.Context, name: discord.User, day: str):
        if ctx.author.id == 280116409852362754:
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

    @commands.hybrid_command(name="sessions", description="List sessions.")
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