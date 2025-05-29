# =======================
# 📦 IMPORTS
# =======================
import discord  # Pour créer des embeds et interagir avec Discord
from discord.ext import commands  # Pour créer des commandes de bot
import aiohttp  # Pour les requêtes HTTP asynchrones
import random  # Pour choisir une carte aléatoirement

# =======================
# 🧠 CLASSE Random
# =======================
class Random(commands.Cog):
    """Cog contenant une commande pour tirer une carte Yu-Gi-Oh! aléatoire."""

    def __init__(self, bot: commands.Bot):
        """
        Constructeur du cog.
        :param bot: instance du bot Discord
        """
        self.bot = bot

    # =======================
    # 🎲 COMMANDE random
    # =======================
    @commands.command(name="random", aliases=["aléatoire", "ran"])
    @commands.cooldown(1, 5, commands.BucketType.user)  # ⏱️ Cooldown de 5 secondes par utilisateur
    async def random_card(self, ctx: commands.Context):
        """
        Commande !random
        Tire une carte Yu-Gi-Oh! aléatoire (en français) depuis l'API de YGOPRODeck.
        """

        # 🔗 URL de l'API pour toutes les cartes (en français)
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"

        # 📡 Requête à l’API
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données depuis l’API.")
                    return

                data = await resp.json()

        # 🛑 Vérification de la validité des données
        if "data" not in data:
            await ctx.send("❌ Données de carte non valides.")
            return

        # 🎯 Choix d'une carte au hasard dans les données
        carte = random.choice(data["data"])

        # =======================
        # 🖼️ CRÉATION DE L’EMBED
        # =======================
        embed = discord.Embed(
            title=carte["name"],
            description=carte.get("desc", "Pas de description disponible."),
            color=discord.Color.gold()  # Couleur dorée pour le côté aléatoire
        )

        # 🔬 Type général (Magie, Piège, Monstre...)
        embed.add_field(name="🧪 Type", value=carte.get("type", "?"), inline=True)

        # =======================
        # 🧟 SI MONSTRE, AJOUTER LES STATS
        # =======================
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

        # 🖼️ Image de la carte
        embed.set_thumbnail(url=carte["card_images"][0]["image_url"])

        # 📤 Envoi du résultat
        await ctx.send(embed=embed)

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    """
    Fonction appelée pour enregistrer ce cog dans le bot principal.
    On ajoute aussi manuellement une catégorie "YGO" pour l’affichage dans !help.
    """
    cog = Random(bot)

    # 🗂️ Définir la catégorie "YGO" pour toutes les commandes de ce cog
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"

    await bot.add_cog(cog)
