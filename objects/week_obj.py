import discord
from datetime import date, timedelta

class Week():
    
    def __init__(self, min_players = -1, max_players = -1):
        self.sunday = []
        self.monday = []
        self.tuesday = []
        self.wednesday = []
        self.thursday = []
        self.friday = []
        self.saturday = []

        self.max_players = max_players
        self.min_players = min_players

        self.day_dict = {
            "min_players": self.min_players,
            "max_players": self.max_players,
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
            "min_players": self.min_players,
            "max_players": self.max_players,
            "sunday": [member.id for member in self.sunday],
            "monday": [member.id for member in self.monday],
            "tuesday": [member.id for member in self.tuesday],
            "wednesday": [member.id for member in self.wednesday],
            "thursday": [member.id for member in self.thursday],
            "friday": [member.id for member in self.friday],
            "saturday": [member.id for member in self.saturday]
        }

    @classmethod
    async def from_dict(cls, data: dict, guild: discord.Guild):
        week = cls()
        dotw = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        for day in dotw:
            week_list = []
            for user_id in data.get(day, []):
                try:
                    member = await guild.fetch_member(user_id)
                    week_list.append(member)
                except discord.NotFound:
                    continue
            setattr(week, day, week_list)
        week.min_players = data.get("min_players")
        week.max_players = data.get("max_players")
        week.day_dict = {day: getattr(week, day) for day in dotw}
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
                k = k + 1
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
        if self.day_dict[day].__len__() >= self.max_players:
            return -1
        if not (user in self.day_dict[day]): 
            self.add_user_to_day(user, day)
            if self.day_dict[day].__len__() >= self.min_players:
                if self.day_dict[day].__len__() == self.max_players:
                    return 2
                return 1
            else:
                return 0 
        else:
            self.remove_user_from_day(user, day)
            if self.day_dict[day].__len__() >= self.min_players:
                return 3
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
                output += f"{i.display_name}\n"
            output += "\n"
        return output