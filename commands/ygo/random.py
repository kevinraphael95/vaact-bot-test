import discord
from discord.ext import commands
import aiohttp
import random

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="random", aliases=["aléatoire"])
    async def random_card(self, ctx):
        """Tire une carte Yu-Gi-Oh! aléatoire (en français)."""
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données.")
                    return
                data = await resp.json()

        if "data" not in data:
            await ctx.send("❌ Données de carte non valides.")
            return

        carte = random.choice(data["data"])

        embed = discord.Embed(
            title=carte["name"],
            description=carte.get("desc", "Pas de description disponible."),
            color=discord.Color.gold()
        )
        embed.add_field(name="🧪 Type", value=carte.get("type", "?"), inline=True)

        if carte.get("type", "").lower().startswith("monstre"):
            atk = carte.get("atk", "?")
            defe = carte.get("def", "?")
            level = carte.get("level", "?")
            attr = carte.get("attribute", "?")
            race = carte.get("race", "?")

            embed.add_field(name="⚔️ ATK / DEF", value=f"{atk} / {defe}", inline=True)
            embed.add_field(name="⭐ Niveau / Rang", value=str(level), inline=True)
            embed.add_field(name="🌪️ Attribut", value=attr, inline=True)
            embed.add_field(name="👹 Race", value=race, inline=True)

        embed.set_thumbnail(url=carte["card_images"][0]["image_url"])
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Random(bot))
