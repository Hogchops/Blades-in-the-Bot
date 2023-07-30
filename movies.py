from discord.ext import commands
from discord import app_commands
import discord
import json
from typing import List
import random

class Movie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.movie_list = []
        self.finished_list = []
        self.load_list()

    def find(self, movie_name):
        for i in range(len(self.movie_list)):
            if self.movie_list[i].lower() == movie_name.lower():
                return i
        return -1

    def save_list(self):
        file_path = "MovieLists\\movies.json"
        with open(file_path, 'w') as f:
            json.dump(self.movie_list, f)
        finished_path = "MovieLists\\finished_movies.json"
        with open(finished_path, 'w') as f:
            json.dump(self.finished_list, f)
            
    def load_list(self):
        file_path = "MovieLists\\movies.json"
        with open(file_path, 'r') as f:
            json_data = json.load(f)
            self.movie_list = json_data
        finished_path = "MovieLists\\finished_movies.json"
        with open(finished_path, 'r') as f:
            json_data = json.load(f)
            self.finished_list= json_data

    @commands.hybrid_group(name = "movie", aliases = ['m'])
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @commands.has_permissions(administrator = True)
    async def movie(self, ctx):
        pass

    @movie.command(name = "add", aliases = ['a'])
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @commands.has_permissions(administrator = True)
    async def add_movie(self, ctx, movie_name: str):
        await ctx.defer()
        index = self.find(movie_name)
        if index == -1:
            self.movie_list.append(movie_name.title())
            await ctx.send(f"{movie_name.title()} has been added to the list.")
            self.save_list()
        else:
            await ctx.send(f"{movie_name.title()} is already added to the list.")

    @movie.command(name = "list", aliases = ['l'])
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @commands.has_permissions(administrator = True)
    async def list_movies(self, ctx):
        await ctx.defer()
        output = "**Movies to Watch:**\n"
        for i in range(len(self.movie_list)):
            output += f"{i+1}. {self.movie_list[i].title()}.\n"
        output += "\n**Finished Movies:**\n"
        for i in range(len(self.finished_list)):
            output += f"{i+1}. {self.finished_list[i].title()}.\n"
        await ctx.send(output)

    async def autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        choices = [movie_name for movie_name in self.movie_list]
        return [
            app_commands.Choice(name = choice, value = choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @movie.command(name = "remove", aliases = ['r'])
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @commands.has_permissions(administrator = True)
    @app_commands.autocomplete(movie_name = autocomplete)
    async def remove_movie(self, ctx, movie_name: str):
        await ctx.defer()
        movie_name = movie_name.lower()
        index = self.find(movie_name)
        del self.movie_list[index]
        self.finished_list.append(movie_name)
        self.save_list()
        await ctx.send(f"{movie_name.title()} has been removed from the list and added to the finished list.")
    
    @movie.command(name = "random")
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @commands.has_permissions(administrator = True)
    async def random_movie(self, ctx):
        await ctx.defer()
        num = random.choice(len(self.movie_list))
        await ctx.send(f"I have selected {self.movie_list[num].title()}")

    async def autocomplete_full(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        choices = []
        for i in range(len(self.movie_list)):
            choices.append(self.movie_list[i])
        for i in range(len(self.finished_list)):
            choices.append(self.finished_list[i])
            

    
    @movie.command(name = "delete", description = "Delete a movie from either list.")
    @app_commands.guilds(discord.Object(id = 807855936106135562))
    @commands.has_permissions(administrator = True)
    @app_commands.autocomplete(movie_name = autocomplete_full)
    async def delete(self, ctx, movie_name: str):
        await ctx.defer()
        movie_name = movie_name.lower()
        index = self.find(movie_name)
        if index != -1:
            del self.movie_list[index]
            await ctx.send(f"{movie_name.title()} has been removed from the list.")
        else:
            index = -1
            for i in range(len(self.finished_list)):
                if self.finished_list[i].lower() == movie_name:
                    index = i
            if index == -1:
                await ctx.send(f"I could not find the movie {movie_name.title()}")
            else:
                del self.finished_list[i]
                await ctx.send(f"{movie_name.title()} has been removed from the finished list.")
        self.save_list()

async def setup(bot):
    await bot.add_cog(Movie(bot))
