import discord
from discord.ext import commands
from discord import app_commands
from gameclock import GameClock
from typing import List

class GameClocks(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.clocks: List[GameClock] = []

    async def autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        choices = []
        for clock in self.clocks:
            if ctx.channel_id == clock.channel_id:
                choices.append(clock.description)
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]
    
    @commands.hybrid_command(name = "pclock", aliases = ['pc'], description = "Create a clock with a description, a total, and some parts already ticked.")
    @app_commands.describe(
        description = "Enter a description for the clock.",
        total = "Enter the total number of ticks this clock should have. Entering 4, 6, 8, or 12 will yield pictures with the clock.",
        progress = "Enter the number of ticks that the clock should start with.",
    )
    async def clock(self, ctx: commands.Context, description: str, total: int, progress: int = 0):
        await ctx.defer()
        clock = GameClock(description, progress, total)
        embed = clock.generate_embed()
        image = clock.get_image()
        embed.set_image(url = f"attachment://Blades_clock_{clock.total}_{clock.progress}.png")
        msg = await ctx.send(file=image, embed=embed)
        await msg.pin()
        clock.embed_id = msg.id
        clock.channel_id = msg.channel.id
        self.clocks.append(clock)


    @commands.hybrid_command(name = "ptick", aliases = ['pt'], description = "Tick a clock by an amount.")
    @app_commands.autocomplete(description = autocomplete)
    @app_commands.describe(
        description = "Enter the description for the clock you want to tick.",
        amount = "Enter a number for how much you want to tick the clock. Entering a negative amount will lower the clock."
    )
    async def tick_clock(self, ctx, description: str, amount: int):
        await ctx.defer()
        description = description.lower()
        clock = next((c for c in self.clocks if c.description == description), None)
        if clock:
            clock.progress += amount
            if clock.progress > clock.total:
                clock.progress = clock.total
            if clock.progress < 0:
                clock.progress = 0
            
            clock_channel = await self.bot.fetch_channel(clock.channel_id)
            embed_msg = await clock_channel.fetch_message(clock.embed_id)

            embed = clock.generate_embed()
            image = clock.get_image()
            embed.set_image(url = f"attachment://Blades_clock_{clock.total}_{clock.progress}.png")
            await embed_msg.edit(embed=embed, attachments=[image])
        else:
            await ctx.send("No clock found matching the description entered.")   

async def setup(bot):
    await bot.add_cog(GameClocks(bot))