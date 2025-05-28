# 📁 ygo/carte.py

# =======================
# 📦 IMPORTS
# =======================
import discord  # Pour créer des embeds et interagir avec Discord
from discord.ext import commands  # Pour les commandes de bot Discord
import aiohttp  # Pour faire des requêtes HTTP de manière asynchrone
import urllib.parse  # Pour encoder les noms de cartes dans l’URL

# =======================
# 🧠 CLASSE Carte
# =======================
class Carte(commands.Cog):
    """Cog contenant la commande pour rechercher une carte Yu-Gi-Oh!"""

    def __init__(self, bot: commands.Bot):
        """
        Constructeur du cog.
        :param bot: instance du bot Discord
        """
        self.bot = bot

    # =======================
    # 🔍 COMMANDE carte
    # =======================
    @commands.command(name="carte", aliases=["card"])
    async def carte(self, ctx: commands.Context, *, nom: str):
        """
        Commande !carte <nom>
        Recherche une carte Yu-Gi-Oh! en français via l’API de YGOPRODeck.
        Le nom doit être exact.
        """

        # 1️⃣ Encodage du nom pour l’URL
        nom_encode = urllib.parse.quote(nom)

        # 2️⃣ Construction de l’URL de l’API (langue = français)
        url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={nom_encode}&language=fr"

        # 3️⃣ Envoi de la requête HTTP à l’API
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                # ❌ Si l’API ne répond pas correctement
                if resp.status != 200:
                    await ctx.send("❌ Impossible de récupérer les données depuis l’API.")
                    return

                # ✅ Lecture de la réponse JSON
                data = await resp.json()

        # 4️⃣ Vérifie si des données de carte ont été reçues
        if "data" not in data:
            await ctx.send("❌ Carte introuvable. Vérifie le nom exact.")
            return

        # 5️⃣ On récupère la première carte trouvée
        carte = data["data"][0]

        # =======================
        # 📋 CRÉATION DE L'EMBED
        # =======================
        embed = discord.Embed(
            title=carte["name"],  # Nom de la carte
            description=carte.get("desc", "Pas de description disponible."),  # Description de la carte
            color=discord.Color.red()  # Couleur rouge pour le thème Yu-Gi-Oh!
        )

        # 🔬 Type général de la carte (Monstre, Magie, Piège, etc.)
        embed.add_field(name="🧪 Type", value=carte.get("type", "?"), inline=True)

        # =======================
        # 🧟 SI C’EST UN MONSTRE
        # =======================
        if carte.get("type", "").lower().startswith("monstre"):
            # Statistiques du monstre
            atk = carte.get("atk", "?")
            defe = carte.get("def", "?")
            level = carte.get("level", "?")
            attr = carte.get("attribute", "?")
            race = carte.get("race", "?")

            # Champs additionnels pour les monstres
            embed.add_field(name="⚔️ ATK / DEF", value=f"{atk} / {defe}", inline=True)
            embed.add_field(name="⭐ Niveau / Rang", value=str(level), inline=True)
            embed.add_field(name="🌪️ Attribut", value=attr, inline=True)
            embed.add_field(name="👹 Race", value=race, inline=True)

        # 🖼️ Ajout de l’image miniature de la carte
        embed.set_thumbnail(url=carte["card_images"][0]["image_url"])

        # 📤 Envoi de l’embed dans le salon
        await ctx.send(embed=embed)

# =======================
# ⚙️ SETUP DU COG
# =======================
async def setup(bot: commands.Bot):
    """
    Fonction appelée pour enregistrer ce cog dans le bot principal.
    """
    await bot.add_cog(Carte(bot))
