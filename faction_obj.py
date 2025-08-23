from discord import Embed, File, Color

class Faction():

    def __init__(self, title: str, description: str, tier: int, affiliation: int, contact: str, leader: str):
        self.title = title
        self.description = description
        self.tier = tier
        self.affiliation = affiliation
        self.contact = contact
        self.leader = leader
    
    def generate_embed(self) -> Embed:
        if self.affiliation == 0:
            color = Color.light_gray
        elif self.affiliation == 1:
            color = Color.orange
        elif self.affiliation == 2:
            color = Color.red
        else:
            color = Color.magenta

        embed = Embed(title = self.title, description = self.description, color = color)
        embed.add_field(name = "Tier", value = self.tier)
        embed.add_field(name = "Contact", value = self.contact)
        embed.add_field(name = "Leader", value = self.leader)
        return embed
        
    def get_image(self) -> File:
        if self.affiliation == 0:
            fp = f"FactionImages\\empire_png.png"
            fn = f"empire_png.png"
        elif self.affiliation == 1:
            fp = f"FactionImages\\hutt_png.png"
            fn = f"hutt_png.png"
        elif self.affiliation == 2:
            fp = f"FactionImages\\rebellion_png.png"
            fn = f"rebellion_png.png"
        else:
            return None
        file = File(fp=fp, filename=fn)
        return file

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "tier": self.tier,
            "affiliation": self.affiliation,
            "contact": self.contact,
            "leader": self.leader
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            title = data["title"],
            description = data["description"],
            tier = data["tier"],
            affiliation = data["affiliation"],
            contact = data["contact"],
            leader = data["leader"]
        )

        