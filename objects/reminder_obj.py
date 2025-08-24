import discord
from datetime import datetime
from typing import List

class Reminder():

    def __init__(self, time: datetime, day: str):
        self.members: List[discord.User] = []
        self.time = time
        self.day = day
    
    def to_dict(self):
        return {
            "members": [member.id for member in self.members],
            "time": self.time.isoformat(),
            "day": self.day
        }

    @classmethod
    async def from_dict(cls, data, guild: discord.Guild):
        reminder = Reminder(
            time = datetime.fromisoformat(data["time"]),
            day = data["day"]
        )
        for user_id in data["members"]:
            try:
                member = await guild.fetch_member(user_id)
                reminder.members.append(member)
            except discord.NotFound:
                continue
        return reminder