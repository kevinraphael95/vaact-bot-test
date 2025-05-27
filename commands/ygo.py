import discord
import random
import json
from discord.ext import commands
from pathlib import Path

# Charger les citations
with open(Path("data/quotes.json"), encoding="utf-8") as f:
    YUGIOH_QUOTES = json.load(f)

class YGO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quote", help="Affiche une citation aléatoire de Yu-Gi-Oh!")
    async def quote(self, ctx):
        citation = random.choice(YUGIOH_QUOTES)
        embed = discord.Embed(
            title="🎙️ Citation Yu-Gi-Oh!",
            description=f"\"{citation}\"",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Crois au cœur des cartes !")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(YGO(bot))
