import discord
from discord.ext import commands
from faction_clock_objects import Clock
from difflib import get_close_matches
from asyncio import TimeoutError
from asyncio import wait_for
from discord import app_commands
from typing import List

class Clocks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.clocks = []

    async def generate_embed(self, ctx, clock: Clock):
        if clock.total == 4 or clock.total == 6 or clock.total == 8 or clock.total == 12:
            image_path = f"ClockImages\\Blades_clock_{clock.total}_{clock.progress}.png"
            file = discord.File(image_path, filename = f"Blades_clock_{clock.total}_{clock.progress}.png")
            embed = discord.Embed(title = clock.description, description = "", color = discord.Color.magenta())
            embed.set_image(url=f"attachment://Blades_clock_{clock.total}_{clock.progress}.png")
            embed.set_footer(text = f"{clock.progress}/{clock.total}")
            await ctx.send(file = file, embed = embed)
        else:
            embed = discord.Embed(title = clock.description, description = "", color = discord.Color.magenta())
            embed.add_field(name=f"{clock.progress}/{clock.total}", value="")
            await ctx.send(embed = embed)
    
    def find_clock(self, description):
        for i in range(len(self.clocks)):
            if self.clocks[i].description.lower() == description:
                return i
        return -1
    
    async def search_func(self, ctx, description):
        index = self.find_clock(description)
        if index != -1:
            return index
        potential_clocks = [clock.description for clock in self.clocks]
        close_matches = get_close_matches(description.lower(), potential_clocks, 5)

        if len(close_matches) == 1:
            return self.find_clock(close_matches[0])
        elif len(close_matches == 0):
            await ctx.send(f"I could not find a clock matching '{description}'.")
            return -1
        else:
            output = f"Enter the number corresponding to the clock you are searching for:\n"
            for i in range(len(close_matches)):
                output += f"**{i+1}:** {close_matches[i]}\n"
            await ctx.send(output)

            def check(m):
                return m.author == ctx.message.author and m.content.isdigit() and int(m.content) <= 5
            
            try:
                msg = await self.bot.wait_for('message', timeout = 8.0, check = check)
            except TimeoutError:
                await ctx.send("Timeout error, please try again.")
            else:
                chosen = self.find_clock(close_matches[int(msg.content) - 1])
                return self.find_clock[chosen]

    @commands.hybrid_command(name = "clock", aliases = ['c'], description = "Create a clock with a description, a total, and some parts already ticked.")
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @app_commands.describe(
        description = "Enter a description for the clock.",
        total = "Enter the total number of ticks this clock should have. Entering 4, 6, 8, or 12 will yield pictures with the clock.",
        progress = "Enter the number of ticks that the clock should start with."
    )
    async def clock(self, ctx, description: str, total: int, progress: int = 0):
        await ctx.defer()
        clock = Clock(description, progress, total)
        await self.generate_embed(ctx, clock)
        self.clocks.append(clock)
    
    async def autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        choices = [clock.description for clock in self.clocks]
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]
    
    @commands.hybrid_command(name = "clocks", description = "Show a clock in the channel based on description.")
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @app_commands.autocomplete(description = autocomplete)
    @app_commands.describe(
        description = "Enter the description of the clock you wish to show."
    )
    async def clocks_display(self, ctx, description: str):
        await ctx.defer()
        description = description.lower()
        index = self.find_clock(description)
        if index != -1:
            await self.generate_embed(ctx, self.clocks[index])

    @commands.hybrid_command(name = "tick", description = "Tick a clock by an amount.")
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @app_commands.autocomplete(description = autocomplete)
    @app_commands.describe(
        description = "Enter the description for the clock you want to tick.",
        amount = "Enter a number for how much you want to tick the clock. Entering a negative amount will lower the clock."
    )
    async def tick_clock(self, ctx, description: str, amount: int):
        await ctx.defer()
        description = description.lower()
        index = self.find_clock(description)
        if index != -1:
            self.clocks[index].progress += amount
            if self.clocks[index].progress > self.clocks[index].total:
                self.clocks[index].progress = self.clocks[index].total
            if self.clocks[index].progress < 0:
                self.clocks[index].progress = 0
            await self.generate_embed(ctx, self.clocks[index])

    @commands.hybrid_command(name = "delete", description = "Delete a clock by the description.")
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @app_commands.autocomplete(description = autocomplete)
    @app_commands.describe(
        description = "Enter the description of the clock you wish to delete."
    )
    async def delete_clock(self, ctx, description: str):
        await ctx.defer()
        description = description.lower()
        index = self.find_clock(description)
        if index != -1:
            del self.clocks[index]
            await ctx.send("The clock has been deleted.")
    
async def setup(bot):
    await bot.add_cog(Clocks(bot))