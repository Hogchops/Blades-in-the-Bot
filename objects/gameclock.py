import os
from discord import Embed, File, Color

# Directory this file lives in, e.g. .../YourBot/objects
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Adjust this to match where ClockImages actually sits relative to this file.
# If objects/gameclock.py and ClockImages/ are siblings under the project root:
#   YourBot/
#     objects/gameclock.py
#     ClockImages/
# then ClockImages is one level UP from this file's directory:
CLOCK_IMAGES_DIR = os.path.join(BASE_DIR, "..", "ClockImages")

class GameClock():

    def __init__(self, description: str, progress: int, total: int, embed_id: int = -1, channel_id: int = -1):
        self.description = description
        self.progress = progress
        self.total = total
        self.embed_id = embed_id
        self.channel_id = channel_id

    def generate_embed(self) -> Embed:
        embed = Embed(title=self.description, description="", color=Color.magenta())
        embed.set_footer(text=f"{self.progress}/{self.total}")
        return embed

    def get_image(self) -> File | None:
        if self.total in (4, 6, 8, 12):
            file_name = f"Blades_clock_{self.total}_{self.progress}.png"
            file_path = os.path.join(CLOCK_IMAGES_DIR, file_name)
            return File(file_path, file_name)
        else:
            return None