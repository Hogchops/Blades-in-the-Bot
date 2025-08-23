import discord
from discord.ext import commands
from discord import app_commands
from gameclock import GameClock
from typing import List

class GameClocks(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.clocks: List[GameClock] = []

    async def autocomplete(self, ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        choices = []
        for clock in self.clocks:
            if ctx.channel_id == clock.channel_id:
                choices.append(clock.description)
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]
    
    @app_commands.command(name = "clock", description = "Create a clock with a description, a total, and some parts already ticked.")
    @app_commands.describe(
        description = "Enter a description for the clock.",
        total = "Enter the total number of ticks this clock should have. Entering 4, 6, 8, or 12 will yield pictures with the clock.",
        progress = "Enter the number of ticks that the clock should start with.",
    )
    async def clock(self, ctx: discord.Interaction, description: str, total: int, progress: int = 0):
        clock = GameClock(description, progress, total)
        embed = clock.generate_embed()
        image = clock.get_image()
        embed.set_image(url = f"attachment://Blades_clock_{clock.total}_{clock.progress}.png")
        await ctx.response.send_message(file=image, embed=embed)
        msg = await ctx.original_response()
        await msg.pin()
        clock.embed_id = msg.id
        clock.channel_id = msg.channel.id
        self.clocks.append(clock)


    @app_commands.command(name = "tick", description = "Tick a clock by an amount.")
    @app_commands.autocomplete(description = autocomplete)
    @app_commands.describe(
        description = "Enter the description for the clock you want to tick.",
        amount = "Enter a number for how much you want to tick the clock. Entering a negative amount will lower the clock."
    )
    async def tick_clock(self, ctx: discord.Interaction, description: str, amount: int):
        description = description.lower()
        clock = next((c for c in self.clocks if c.description.lower() == description), None)
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
            await ctx.response.send_message("Updated the clock.",ephemeral = True)
        else:
            await ctx.response.send_message("No clock found matching the description entered.", ephemeral=True)
    
    @app_commands.command(name = "delete", description = "Delete a clock.")
    @app_commands.autocomplete(description = autocomplete)
    @app_commands.describe(
        description = "Enter the description for the clock you wish to delete."
    )
    async def delete_clock(self, ctx: discord.Interaction, description: str):
        description = description.lower()
        clock = next((c for c in self.clocks if c.description.lower() == description), None)
        if clock:
            clock_channel = await self.bot.fetch_channel(clock.channel_id)
            embed_msg = await clock_channel.fetch_message(clock.embed_id)

            await embed_msg.delete()
            await ctx.response.send_message("Deleted the clock.", ephemeral=True)
        else:
            await ctx.response.send_message("Clock not found.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GameClocks(bot))