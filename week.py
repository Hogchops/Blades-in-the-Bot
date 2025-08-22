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
            "sunday": self.sunday,
            "monday": self.monday,
            "tuesday": self.tuesday,
            "wednesday": self.wednesday,
            "thursday": self.thursday,
            "friday": self.friday,
            "saturday": self.saturday
        }

    @classmethod
    def from_dict(cls, data):
        week = cls()
        week.sunday = data.get("sunday", [])
        week.monday = data.get("monday", [])
        week.tuesday = data.get("tuesday", [])
        week.wednesday = data.get("wednesday", [])
        week.thursday = data.get("thursday", [])
        week.friday = data.get("friday", [])
        week.saturday = data.get("saturday", [])
        return week


    def add_user_to_day(self, user_id: int, day: str):
        self.day_dict[day].append(user_id)

    def remove_user_from_day(self, user_id: int, day: str) -> int:
        day_list = self.day_dict[day.lower()]
        if user_id in day_list:
            day_list.remove(user_id)
            return 0
        return -1
    
    def purge_user_from_other_days(self, user_id: int, day: str):
        day_list = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        day_list.remove(day)
        for d in day_list:
            if user_id in self.day_dict[d]:
                self.remove_user_from_day(user_id, d)

    def button(self, user_id: int, day: str) -> int:
        if self.day_dict[day].__len__() >= self.session_full:
            return -1
        if not (user_id in self.day_dict[day]): 
            self.add_user_to_day(user_id, day)
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
                self.remove_user_from_day(user_id, day)
                return 0
    
    def get_user_day(self, user_id: int, day: str) -> int:
        day_list = self.day_dict[day.lower()]
        for i in range(day_list.__len__()):
            if day_list[i] == user_id:
                return i
        return -1

    def get_next_week_dates(self):
        today = date.today()

        days_ahead = (6 - today.weekday()) % 7
        next_sunday = today + timedelta(days=days_ahead)

        week_dates = [(next_sunday + timedelta(days=i)) for i in range(7)]
        return week_dates