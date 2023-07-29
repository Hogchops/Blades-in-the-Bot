import discord
from discord.ext import commands
from faction_clock_objects import Clock
from difflib import get_close_matches
from asyncio import TimeoutError
from asyncio import wait_for

class Clocks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.clocks = []
    
    def generate_embed(self, index):
        pass
    
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

    @commands.group(name = "clock", aliases = ['c'])
    async def clock_group(self, ctx):
        if ctx.invoked_subcommand is None:
            output = "Here are your active clocks:\n"
            for clock in self.clocks:
                output += f"{clock.description} **{clock.progress}/{clock.total}**\n"
            await ctx.send(output)
    
    #@clock_group.command(name = "add", aliases = ['a'])
    #async def add_clock(interaction: discord.Interaction, ):
    #    pass
    
async def setup(bot):
    await bot.add_cog(Clocks(bot))

