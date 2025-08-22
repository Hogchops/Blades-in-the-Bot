import discord
from datetime import date, timedelta

class Week():
    
    def __init__(self):
        self.sunday = []
        self.monday = []
        self.tuesday = []
        self.wednesday = []
        self.thursday = []
        self.friday = []
        self.saturday = []

        self.session_full = 5
        self.session_confirmed = 4

        self.day_dict = {
            "sunday": self.sunday,
            "monday": self.monday,
            "tuesday": self.tuesday,
            "wednesday": self.wednesday,
            "thursday": self.thursday,
            "friday": self.friday,
            "saturday": self.saturday
        }

    def to_dict(self):
        return {
            "sunday": [member.id for member in self.sunday],
            "monday": [member.id for member in self.monday],
            "tuesday": [member.id for member in self.tuesday],
            "wednesday": [member.id for member in self.wednesday],
            "thursday": [member.id for member in self.thursday],
            "friday": [member.id for member in self.friday],
            "saturday": [member.id for member in self.saturday]
        }

    @classmethod
    async def from_dict(cls, data, guild: discord.Guild):
        week = cls()
        dotw = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        for day in dotw:
            week_list = []
            for user_id in data.get(day, []):
                try:
                    member = await guild.fetch_member(user_id)
                except discord.NotFound:
                    continue
                week_list.append(member)
            setattr(week, day, week_list)

        week.day_dict = {day: getattr(week, day) for day in dotw}
        print(week.to_string())
        return week

    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(title = "Session Signups", description = "If you see your name listed under a day, you are signed up for that day. All times are 7:00 pm EST.", color = discord.Color.blurple())
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        week_dates = self.get_next_week_dates()
        for i in range(7):
            name = f"__{days[i]}__ __{week_dates[i].strftime('%m/%d')}__"
            embed.add_field(name = name, value = self.day_string(days[i]))
        return embed

    def day_string(self, day: str) -> str:
        day_list = self.day_dict[day.lower()]
        output = ""
        k = 1

        for i in day_list:
            if i:
                output += f"{k}: {i.display_name}\n"
        return output

    def add_user_to_day(self, user: discord.User, day: str):
        self.day_dict[day].append(user)

    def remove_user_from_day(self, user: discord.User, day: str) -> int:
        day_list = self.day_dict[day.lower()]
        if user in day_list:
            day_list.remove(user)
            return 0
        return -1
    
    def purge_user_from_other_days(self, user: discord.User, day: str):
        day_list = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        day_list.remove(day)
        for d in day_list:
            if user in self.day_dict[d]:
                self.remove_user_from_day(user, d)

    def button(self, user: discord.User, day: str) -> int:
        if self.day_dict[day].__len__() >= self.session_full:
            return -1
        if not (user in self.day_dict[day]): 
            self.add_user_to_day(user, day)
            if self.day_dict[day].__len__() >= self.session_confirmed:
                for player in self.day_dict[day]:
                    self.purge_user_from_other_days(player, day)
                return 1
            else:
                return 0 
        else:
            if self.day_dict[day].__len__() >= self.session_confirmed:
                return -1
            else:
                self.remove_user_from_day(user, day)
                return 0
    
    def get_user_day(self, user: discord.User, day: str) -> int:
        day_list = self.day_dict[day.lower()]
        for i in range(day_list.__len__()):
            if day_list[i].id == user.id:
                return i
        return -1

    def get_next_week_dates(self):
        today = date.today()

        days_ahead = (6 - today.weekday()) % 7
        next_sunday = today + timedelta(days=days_ahead)

        week_dates = [(next_sunday + timedelta(days=i)) for i in range(7)]
        return week_dates
    
    def to_string(self):
        output = ""
        dotw = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        for d in dotw:
            output += f"{d.title()}:\n"
            for i in self.day_dict[d]:
                output += f"{i.display_name()}\n"
            output += "\n"
        return output