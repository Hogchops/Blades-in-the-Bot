import discord

class Week():
    
    def __init__(self):
        self.sunday = []
        self.monday = []
        self.tuesday = []
        self.wednesday = []
        self.thursday = []
        self.friday = []
        self.saturday = []

        self.day_dict = {
            "sunday": self.sunday,
            "monday": self.monday,
            "tuesday": self.tuesday,
            "wednesday": self.wednesday,
            "thursday": self.thursday,
            "friday": self.friday,
            "saturday": self.saturday
        }
    
    def add_user_to_day(self, name: str, day: str):
        self.day_dict[day].append(name)

    def remove_user_from_day(self, name: str, day: str) -> int:
        day_list = self.day_dict[day.lower()]
        i = self.get_user_day(name, day)
        if i != -1:
            day_list.remove(name)
            return 0
        return -1
    
    def purge_user_from_other_days(self, name: str, day: str):
        day_list = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        day_list.remove(day)
        for d in day_list:
            i = self.get_user_day(name, d)
            if i != -1:
                self.remove_user_from_day(name, d)

    def button(self, name: str, day: str) -> int:
        if self.day_dict[day].__len__() > 5:
            return -1
        i = self.get_user_day(name, day)
        if i == -1:
            self.add_user_to_day(name, day)
            if self.day_dict[day].__len__() > 1:
                for user in self.day_dict:
                    self.purge_user_from_other_days(user, day)
                return 1
            else:
                return 0 
        else:
            if self.day_dict[day].__len__() > 1:
                return -1
            else:
                self.remove_user_from_day(name, day)
                return 0
    
    def get_user_day(self, name: str, day: str) -> int:
        day_list = self.day_dict[day.lower()]
        for i in range(day_list.__len__()):
            if day_list[i].lower() == name.lower():
                return i
        return -1

    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(title = "Session Signups", description = "If you see your name listed under a day, you are signed up for that day.", color = discord.Color.blurple())
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for i in range(7):
            embed.add_field(name = days[i], value = self.day_string(days[i]))
        return embed

    def day_string(self, day: str) -> str:
        day_list = self.day_dict[day.lower()]
        output = ""
        for i in day_list:
            output += i + "\n"
        return output