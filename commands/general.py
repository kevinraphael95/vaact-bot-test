import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Affiche la latence du bot.")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        color = discord.Color.green() if latency < 150 else discord.Color.orange()
        embed = discord.Embed(
            title="🏓 Pong !",
            description=f"Latence du bot : **{latency}ms**",
            color=color
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))
