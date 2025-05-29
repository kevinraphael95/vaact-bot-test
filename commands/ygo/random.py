# =======================
# 📦 IMPORTS
# =======================
import discord
from discord.ext import commands
import aiohttp
import random

# =======================
# 🧠 CLASSE Random
# =======================
class Random(commands.Cog):
    """Cog contenant une commande pour tirer une carte Yu-Gi-Oh! aléatoire."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =======================
    # 🎲 COMMANDE random
    # =======================
    @commands.command(name="random", aliases=["aléatoire", "ran"])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)  # ⏱️ Cooldown 5s
    async def random_card(self, ctx: commands.Context):
        """
        Tire une carte Yu-Gi-Oh! aléatoire (en français) depuis l'API YGOPRODeck.
        """

        # 🔗 API optimisée : on tire 1 carte aléatoire en français (évite de charger tout le dataset)
        url = "https://db.ygoprodeck.com/api/v7/randomcard.php?language=fr"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.send("❌ Erreur de connexion à l’API YGOProDeck.")
                    carte = await resp.json()
        except Exception as e:
            return await ctx.send(f"❌ Une erreur s’est produite : {e}")

        # 🖼️ Création de l’embed
        embed = discord.Embed(
            title=carte.get("name", "Carte inconnue"),
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

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    """
    Fonction appelée pour enregistrer ce cog dans le bot principal.
    On ajoute aussi manuellement une catégorie "🃏 Yu-Gi-Oh!" pour l’affichage dans !help.
    """
    cog = Random(bot)

    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"

    await bot.add_cog(cog)
