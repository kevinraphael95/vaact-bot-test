import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="Affiche toutes les commandes disponibles.")
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 Commandes disponibles",
            description="Voici les commandes regroupées par catégorie :",
            color=discord.Color.green()
        )

        # Parcourt tous les Cogs (groupes de commandes)
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_commands()
            if commands_list:
                command_descriptions = ""
                for command in commands_list:
                    command_descriptions += f"`{ctx.prefix}{command.name}` : {command.help or 'Aucune description'}\n"
                embed.add_field(name=f"📂 {cog_name}", value=command_descriptions, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
