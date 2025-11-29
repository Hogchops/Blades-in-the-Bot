import discord
from discord.ext import commands
from discord import app_commands
from interactions.signup_interaction import SignupButtons
from objects.week_obj import Week
from objects.reminder_obj import Reminder
from typing import List
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
import json
import asyncio
import os

EST = ZoneInfo("US/Eastern")

class Signup(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.week = None
        self.session_confirmed = 4
        self.saved_channel_id = None
        self.saved_embed_id = None
        self.saved_view_id = None

        self.reminders: List[Reminder] = []
        self.scheduled_tasks: dict[str, asyncio.Task] = {}

        for cmd in self.__cog_app_commands__:
            cmd.extras["cog"] = self.__cog_name__

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

        reminder_dir = "reminders"
        os.makedirs(reminder_dir, exist_ok=True)

        restored_count = 0
        for file_name in os.listdir(reminder_dir):
            if not file_name.endswith(".json"):
                continue
            fp = os.path.join(reminder_dir, file_name)
            try:
                with open(fp, "r") as f:
                    data = json.load(f)
                reminder = await Reminder.from_dict(data, guild) 

                now = datetime.now(EST)
                delay = (reminder.time - now).total_seconds()
                delay = max(delay, 0)

                task = asyncio.create_task(self.send_reminders(reminder.members, reminder.day, delay, fp))
                self.scheduled_tasks[fp] = task

                restored_count += 1
            except Exception as e:
                print(f"Could not restore reminder from {file_name}: {e}")
        print(f"Restored {restored_count} reminders.")

    @app_commands.command(name="signup", description="Create the signup embed for the week.")
    @app_commands.describe(
        game_name = "Enter the name of the game.",
        bgg_link = "Enter the link for the BGG page for the corresponding game.",
        min_players = "Enter the minimum player count for the game.",
        max_players = "Enter the maximum player count."
    )
    @app_commands.default_permissions(administrator=True)
    async def get_signups(self, interaction: discord.Interaction, game_name: str, bgg_link: str, min_players: int, max_players: int):
        if self.saved_channel_id and self.saved_view_id and self.saved_embed_id:
            try:
                old_channel = await self.bot.fetch_channel(self.saved_channel_id)
                if old_channel:
                    old_view = await old_channel.fetch_message(self.saved_view_id)
                    await old_view.delete()
            except Exception as e:
                print(f"Could not delete the old embed message: {e}")

        self.week = Week(min_players, max_players)

        await interaction.response.send_message(embed=self.week.generate_embed())
        msg = await interaction.original_response()
        self.saved_channel_id = msg.channel.id
        self.saved_embed_id = msg.id

        guild = await self.bot.fetch_guild(interaction.channel.guild.id)
        board_game_role = await guild.fetch_role(1444163673613664306)

        view_msg = await interaction.followup.send(
                    content=f"{board_game_role.mention} Signups are active for the next calendar week for **__{game_name}__**. " \
                    "Press a button to signup for the corresponding day. " \
                    "The times for all days are set at **7:00 pm EST**. Sign up for each day that you would be willing to make.\n" \
                    f"BGG Link: {bgg_link}\n"
                    f"Minimum Player Count: **{min_players}**\n" \
                    f"Maximum Player Count: **{max_players}**" \
                    "\n\nTo remove your name from a day, press the button again.",
                    wait=True,
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

    @app_commands.command(name="sr", description="Remove someone from a confirmed list.")
    @app_commands.autocomplete(day = autocomplete_dotw)
    @app_commands.default_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction, name: discord.User, day: str):
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
            embed_channel = await self.bot.fetch_channel(self.saved_channel_id)
            if embed_channel:
                msg = await embed_channel.fetch_message(self.saved_embed_id)
                if msg:
                    await msg.edit(embed = self.week.generate_embed())
                    await interaction.response.send_message(f"{name.display_name} removed from {day}.", ephemeral=True)
                else:
                    await interaction.response.send_message("Embed message not found.", ephemeral=True)
            else:
                await interaction.response.send_message("Channel not found.", ephemeral=True)
        else:
            await interaction.response.send_message("User not found.", ephemeral=True)

    @app_commands.command(name="sessions", description="List sessions.")
    @app_commands.default_permissions(administrator=True)
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

    @app_commands.command(name="pick-games", description="Gather interest for the board games.")
    @app_commands.describe(
        games = "List game names separated by a comma",
        bgg_links = "List the urls, separated by a comma, for the respective game."
    )
    async def pick_games(self, interaction: discord.Interaction, games: str, bgg_links: str):
        game_list = games.split(',')
        bgg_links_list = bgg_links.split(',')
        embed = discord.Embed(
            title = "Board Game Choices",
            description="Take a look at the following games, paying attention to game duration, mechanical weight, mechanics, and whether it's competitive or not.",
            color = discord.Color.blurple()
        )
        for i in range(game_list.__len__()):
            embed.add_field(name = f"{i+1}: {game_list[i]}", value=f"{bgg_links_list[i]}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="notify", description="Send a reminder to people locked in for sessions")
    @app_commands.default_permissions(administrator=True)
    async def remind_sessions(self, interaction: discord.Interaction):
        if not self.week:
            await interaction.response.send_message("No data found", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        
        dotw = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        now = datetime.now(EST)
        messages = []

        for i, day in enumerate(dotw):
            members = getattr(self.week, day, [])
            if len(members) >= self.session_confirmed:
                today = now.date()
                target_date = today + timedelta(days = (i - today.weekday()) % 7)
                session_time = datetime.combine(target_date, time(19,0), tzinfo=EST)

                remind_time = session_time - timedelta(days = 1)
                delay = (remind_time - now).total_seconds()
                
                fn = f"reminder_{remind_time.strftime('%Y-%m-%d')}.json"
                fp = os.path.join("reminders", fn)

                if fp in self.scheduled_tasks:
                    self.scheduled_tasks[fp].cancel()
                    try:
                        os.remove(fp)
                    except FileNotFoundError:
                        pass

                if delay > 0:
                    reminder = Reminder(remind_time, day)
                    reminder.members.extend(members)

                    with open(fp, "w") as f:
                        json.dump(reminder.to_dict(), f, indent=2)
                    
                    task = asyncio.create_task(self.send_reminders(members, day, delay, fp))
                    self.scheduled_tasks[fp] = task

                    output = (
                        f"Reminders scheduled for {remind_time.strftime('%Y-%m-%d %H:%M:%S %Z')}.\n"
                        f"The people receiving them are:\n" +
                        "\n".join(m.display_name for m in members)
                    )
                    messages.append(output)
                else:
                    task = asyncio.create_task(self.send_reminders(members, day, 0, fp))
                    self.scheduled_tasks[fp] = task
                    
                    output = (
                        f"Reminders sent immediately for {remind_time.strftime('%A, %Y-%m-%d')}.\n"
                        f"The people receiving them are:\n" +
                        "\n".join(m.display_name for m in members)
                    )
                    messages.append(output)
        if messages:
            await interaction.followup.send("\n\n".join(messages), ephemeral=True)
        else:
            await interaction.followup.send("No sessions qualified for reminders.", ephemeral=True)
    
    async def send_reminders(self, members, day, delay, fp: str | None):
        await asyncio.sleep(delay)
        print("Issuing reminders ->")
        for member in members:
            try:
                await member.send(f"Reminder: you are signed up for a board game tomorrow, {day} at 7pm EST.")
                print(f"I reminded {member.display_name}!")
            except Exception as e:
                print(f"Could not DM {member}: {e}")
        
        if fp:
            try:
                os.remove(fp)
                print(f"Deleted reminder file: {fp}")
            except FileNotFoundError:
                pass
        
        if fp and fp in self.scheduled_tasks:
            self.scheduled_tasks.pop(fp)
        
async def setup(bot):
    await bot.add_cog(Signup(bot))