import discord
from discord.ext import commands
import aiohttp

class Carte(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="carte")
    async def carte(self, ctx, *, nom: str):
        """Recherche une carte Yu-Gi-Oh! par son nom exact."""
        url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={nom}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données.")
                    return
                data = await resp.json()

        if "data" not in data:
            await ctx.send("❌ Carte introuvable.")
            return

        carte = data["data"][0]

        embed = discord.Embed(
            title=carte["name"],
            description=carte.get("desc", "Pas de description."),
            color=discord.Color.red()
        )
        embed.add_field(name="Type", value=carte.get("type", "?"), inline=True)
        embed.add_field(name="ATK/DEF", value=f"{carte.get('atk', '?')}/{carte.get('def', '?')}", inline=True)
        embed.add_field(name="Niveau/Rang", value=str(carte.get("level", "?")), inline=True)
        embed.add_field(name="Attribut", value=carte.get("attribute", "?"), inline=True)
        embed.add_field(name="Race", value=carte.get("race", "?"), inline=True)
        embed.set_thumbnail(url=carte["card_images"][0]["image_url"])

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Carte(bot))
