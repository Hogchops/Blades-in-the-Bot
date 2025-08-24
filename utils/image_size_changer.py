
from PIL import Image
import os

THUMBNAIL_SIZE = (80,80)

def resize_to_discord_thumbnail(input_path, output_path):
    try:
        img = Image.open(input_path)

        img = img.resize(THUMBNAIL_SIZE, Image.LANCZOS)

        img.save(output_path)

        print(f"Resized and saved: {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

path1 = "FactionImages\\rebellion_png.png"
path2 = "FactionImages\\empire_png.png"
path3 = "FactionImages\\hutt_png.png"

newpath1 = "FactionImagesNew\\rebellion_png.png"
newpath2 = "FactionImagesNew\\empire_png.png"
newpath3 = "FactionImagesNew\\hutt_png.png"

resize_to_discord_thumbnail(path1, newpath1)
resize_to_discord_thumbnail(path2, newpath2)
resize_to_discord_thumbnail(path3, newpath3)