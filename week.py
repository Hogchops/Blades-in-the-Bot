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
        day_list = self.day_dict[day]
        i = self.get_user_day(name, day)
        if i != -1:
            day_list.remove(name.lower())
            return 0
        return -1
    
    def button(self, name: str, day: str):
        i = self.get_user_day(name, day)
        if i == -1:
            self.add_user_to_day(name, day)
        else:
            self.remove_user_from_day(name, day)
    
    def get_user_day(self, name: str, day: str) -> int:
        day_list = self.day_dict[day]
        for i in range(day_list.__len__()):
            if day_list[i].lower() == name.lower():
                return i
        return -1

    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(title = "Session Signups", description = "If you see your name listed under a day, you are signed up for that day.", color = discord.Color.blurple())
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for i in range(7):
            embed.add_field(name = days[i], description = self.day_string(days[i]))
        return embed

    def day_string(self, day) -> str:
        day_list = self.day_dict[day]
        output = ""
        for i in day_list:
            output += i + "\n"
        return output