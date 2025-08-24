from discord import Embed, File, Color

class GameClock():

    def __init__(self, description: str, progress: int, total: int, embed_id: int = -1, channel_id: int = -1):
        self.description = description
        self.progress = progress
        self.total = total
        self.embed_id = embed_id
        self.channel_id = channel_id
    
    def generate_embed(self) -> Embed:
        embed = Embed(title=self.description, description="", color = Color.magenta())
        embed.set_footer(text = f"{self.progress}/{self.total}")
        return embed
    
    def get_image(self) -> File:
        if self.total == 4 or self.total == 6 or self.total == 8 or self.total == 12:
            file_path = f"ClockImages\\Blades_clock_{self.total}_{self.progress}.png"
            file_name = f"Blades_clock_{self.total}_{self.progress}.png"
            file = File(file_path, file_name)
            return file
        else:
            return None