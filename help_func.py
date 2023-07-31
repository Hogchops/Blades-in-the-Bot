from discord.ext import commands
import discord

class MyHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % ("=", command.qualified_name, command.signature)
    
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title = "Help", color = discord.Color.magenta())
        embed.set_author(name = self.context.author.display_name, icon_url = self.context.author.display_avatar.url)
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]

            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name = cog_name, value = "\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed = embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title = cog.qualified_name or "No Category", description = cog.description, color = discord.Color.magenta())

        if filtered_commands := await self.filter_commands(cog.get_commands()):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.description or "No Help Message Found... ")

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=self.get_command_signature(group), description=group.description, color=discord.Color.magenta())

        if filtered_commands := await self.filter_commands(group.commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.description or "No Help Message Found... ")

        await self.get_destination().send(embed=embed)
	
    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.magenta())
        if command.description:
            embed.description = command.description
        if alias := command.aliases:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    '''
	@commands.hybrid_command(name = "info", guild=discord.Object(id=807855936106135562))
	async def slash_help(inter: discord.Interaction):
		await inter.response.defer(ephemeral = True)
		embed = discord.Embed(title = "Help", color = discord.Color.magenta(), description = "Play Blades in the Dark or other Forged in the Dark systems through Discord! Featuring die rolling, clock tracking, faction management, and more, you'll have all the tools you will need to run your games.")
		embed.set_author(name = inter.message.author.display_name, icon_url = inter.message.author.display_avatar.url)
		embed.add_field(name = "Slash Commands", value = "Blades in the Bot comes equipped with full usage of slash commands. Using these slash commands will allow you to autocomplete commands, parameters, and view required arguments while typing. However, you can also use regular prefix commands. Please see `=help` for a full list of all commands.", inline = False)
		embed.add_field(name = "Rolling", value = "You can roll using `/r [num]` or `=r [num]`. Blades in the Bot uses d6s, and can handle 0d6. Blades in the Bot will automatically check to see whether or not you got a failure, mixed, success, or critical success and place a corresponding emoji next to the result.", inline = False)
		embed.add_field(name = "Factions", value = "Blades in the Bot allows the GM to create factions to store faction information through the bot. Players can view public information about these factions by using `/faction [name]` or `=faction [name]`.", inline = False)
		embed.add_field(name = "Clocks", value = "Blades in the Bot can create clocks for use during play. Use `/clock` and fill in the required arguments to create a clock. Use `/tick [num]` to tick an existing clock. Use `/delete` to delete a clock.", inline = False)
		await inter.response.send_message(embed = embed, ephemeral = True)
	'''