import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Affiche la latence du bot."""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong !",
            description=f"Latence du bot : **{latency}ms**",
            color=discord.Color.green() if latency < 150 else discord.Color.orange()
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Ping(bot))
