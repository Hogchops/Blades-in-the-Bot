from discord import Embed, File, Color

class Faction():

    def __init__(self, title: str, description: str, tier: int, affiliation: int, contact: str, leader: str):
        self.title = title
        self.description = description
        self.tier = tier
        self.affiliation = affiliation
        self.contact = contact
        self.leader = leader
    
    def generate_embed(self):
        if self.affiliation == 0:
            color = Color.light_gray
        elif self.affiliation == 1:
            color = Color.orange
        elif self.affiliation == 2:
            color = Color.red
        else:
            color = Color.magenta

        embed = Embed(title = self.title, description = self.description, color = color)
        