import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from difflib import get_close_matches

def generate_embed(ctx, dice):
    num = len(dice)
    
    embed = discord.Embed(title = f'{ctx.author.display_name} makes a roll!', url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', description = f'Number of rolls: {num}!', color = 0xFF5733)

    for i in range(num):
        
        embed.add_field(name = f'Die {i+1}', value = f'**{dice[i]}**', inline = True)

        footer_string = ''
        
        maximum = int(sorted(dice)[-1])
        if maximum == 6:
            footer_string = "You got a success!"
        elif maximum == 4 or maximum == 5:
            footer_string = "You got a partial success!"
        else:
            footer_string = "You failed the roll!"
        embed.set_footer(text = footer_string)
    return embed


class Roll(commands.Cog):
    """Category documentation"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'r', help = 'Roll some d6s.\nUsage: =r [number of d6s]')
    async def roll(self, ctx, num = 2, dc = 0,  dif = -1):
        dice = [str(random.choice(range(1,7))) for _ in range(num)]
        embed = generate_embed(ctx, dice, dc, dif)
        await ctx.send(embed = embed)