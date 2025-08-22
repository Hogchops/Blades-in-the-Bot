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
        print("hi")
        if not (user in self.day_dict[day]): 
            print("HEY")
            self.add_user_to_day(user, day)
            print("added")
            if self.day_dict[day].__len__() >= self.session_confirmed:
                for player in self.day_dict[day]:
                    self.purge_user_from_other_days(player, day)
                return 1
            else:
                return 0 
        else:
            print("not found")
            if self.day_dict[day].__len__() >= self.session_confirmed:
                return -1
            else:
                self.remove_user_from_day(user, day)
                return 0
    
    def get_user_day(self, user: discord.User, day: str) -> int:
        day_list = self.day_dict[day.lower()]
        for i in range(day_list.__len__()):
            if day_list[i] == user:
                return i
        return -1

    def generate_embed(self) -> discord.Embed:
        embed = discord.Embed(title = "Session Signups", description = "If you see your name listed under a day, you are signed up for that day.", color = discord.Color.blurple())
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for i in range(7):
            embed.add_field(name = "__" + days[i] + "__", value = self.day_string(days[i]))
        return embed

    def day_string(self, day: str) -> str:
        day_list = self.day_dict[day.lower()]
        output = ""
        k = 1
        
        for i in day_list:
            output += f"{k}: {i.display_name}\n"
            k += 1
        return output