import random
import json
import discord

class Clock():

    def __init__(self, description, progress, total):
        self.description = description
        self.progress = progress
        self.total = total

    def advance(self, tier):
        dice = [random.choice(range(1,7)) for _ in range(tier)]
        dice.sort()
        result = 0
        if dice[-1] == 6:
            result = 3
            if tier >= 2:
                if dice[-2] == 6:
                    result += 2
        elif dice[-1] == 4 or dice[-1] == 5:
            result = 2
        else:
            result = 1
        self.progress += result
        return self.progress >= self.total
    
    def advance_manually(self, num):
        self.progress += num
        return self.progress >= self.total
    
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent = 4)
    

class Faction:

    def __init__(self, name, tier, hold, rep, description, contacts, notes, secret_notes):
        self.name = name
        self.tier = tier
        self.hold = hold
        self.rep = rep
        self.description = description
        self.contacts = contacts
        self.notes = notes
        self.secret_notes = secret_notes
        self.clocks = []
    
    def set(self, field: str, value):
        field = field.lower()
        if field == "title":
            self.name = value
        elif field == "tier":
            self.tier = value
        elif field == "hold":
            self.hold = value
        elif field == "status":
            self.rep = value
        elif field == "description":
            self.description = value
        elif field == "contacts":
            self.contacts = value
        elif field == "notes":
            self.notes = value
        elif field == "secret notes":
            self.secret_notes = value
        elif field == "clocks":
            self.clocks = value

    def get(self, field: str):
        dict_obj = {
            "name": self.name,
            "tier": self.tier,
            "hold": self.hold,
            "rep": self.rep,
            "description": self.description,
            "contacts": self.contacts,
            "notes": self.notes,
            "secret notes": self.secret_notes,
            "clocks": self.clocks
        }
        field = field.lower()
        return dict_obj.get(field)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def add_clock(self, description, progress, total):
        clock_to_add = Clock(description, progress, total)
        self.clocks.append(clock_to_add)
    
    def remove_clock(self, index):
        del self.clocks[index]

    def player_display(self, ctx):
        embed = discord.Embed(title = self.name, description = self.description, color = ctx.author.color)
        embed.add_field(name = f'Tier {self.tier}', value = '')
        embed.add_field(name = f'Hold {self.hold}', value = '')
        names = ""
        for contact in self.contacts:
            names += contact + "\n"
        embed.add_field(name = 'Contacts', value = names)
        embed.add_field(name = 'Status', value = f'{self.rep}')
        if self.notes != "":
            embed.add_field(name = "Notes", value = self.notes)
        return embed
    
    def gm_display(self, ctx):
        embed = discord.Embed(title = self.name, description = self.description, color = ctx.author.color)
        embed.add_field(name = f'Tier {self.tier}', value = '')
        embed.add_field(name = f'Hold {self.hold}', value = '')
        names = ""
        for contact in self.contacts:
            names += contact + "\n"
        embed.add_field(name = 'Contacts', value = names)
        embed.add_field(name = 'Status', value = f'{self.rep}')
        if self.notes != "":
            embed.add_field(name = "Notes", value = self.notes)
        if self.secret_notes != "":
            embed.add_field(name = "Secret Notes", value = self.secret_notes)
        if len(self.clocks) > 0:
            for clock in self.clocks:
                embed.add_field(name = f'Clock {clock.progress}/{clock.total}', value = clock.description)
        return embed