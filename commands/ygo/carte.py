# ────────────────────────────────────────────────────────────────────────────────
# 📁 ygo/carte.py — Commande !carte
# ────────────────────────────────────────────────────────────────────────────────
# Ce module permet de rechercher et afficher les détails d’une carte Yu-Gi-Oh!
# en utilisant l’API YGOPRODeck (en français).
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                            # 📦 Outils de création d'embeds pour Discord
from discord.ext import commands          # 🧩 Pour les commandes du bot
import aiohttp                            # 🌐 Requêtes HTTP asynchrones
import urllib.parse                       # 🔠 Encodage URL pour les noms de cartes

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 COG : Carte
# ────────────────────────────────────────────────────────────────────────────────
class Carte(commands.Cog):
    """
    🔎 Cog contenant la commande !carte permettant de chercher une carte
    Yu-Gi-Oh! en langue française via l'API YGOPRODeck.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l’instance du bot

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !carte / !card
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="carte",
        aliases=["card"],
        help="📄 Affiche les infos d’une carte Yu-Gi-Oh! en français."
    )
    async def carte(self, ctx: commands.Context, *, nom: str):
        """
        🧠 Commande !carte <nom>
        Recherche une carte Yu-Gi-Oh! par son nom (exact), et affiche ses infos.
        """

        # 1️⃣ Encodage du nom de la carte pour l’URL (ex : "Dragon Blanc" → "Dragon%20Blanc")
        nom_encode = urllib.parse.quote(nom)

        # 2️⃣ Construction de l’URL vers l’API YGOPRODeck (langue = fr)
        url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={nom_encode}&language=fr"

        try:
            # 3️⃣ Envoi de la requête asynchrone à l’API
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    # ❌ Si l’API ne répond pas correctement
                    if resp.status != 200:
                        await ctx.send("🚨 Erreur : Impossible de récupérer les données depuis l’API.")
                        return
                    data = await resp.json()

            # 4️⃣ Vérifie si la carte existe dans les données retournées
            if "data" not in data:
                await ctx.send("❌ Carte introuvable. Vérifie l’orthographe exacte.")
                return

            # 5️⃣ Récupère la première carte trouvée dans le résultat
            carte = data["data"][0]

            # ────────────────────────────────────────────────────────────────────
            # 🎨 CRÉATION DE L'EMBED — Informations de la carte
            # ────────────────────────────────────────────────────────────────────
            embed = discord.Embed(
                title=carte.get("name", "Carte inconnue"),  # 🔠 Nom de la carte
                description=carte.get("desc", "Pas de description disponible."),  # 📜 Texte d'effet
                color=discord.Color.red()  # 🎨 Couleur thématique Yu-Gi-Oh!
            )

            # 🔬 Type général (Magie, Monstre, Piège, etc.)
            embed.add_field(name="🧪 Type", value=carte.get("type", "?"), inline=True)

            # ────────────────────────────────────────────────────────────────────
            # 🧟 SI C’EST UN MONSTRE : Ajouter ATK/DEF/Niveau/Attribut/Race
            # ────────────────────────────────────────────────────────────────────
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

            # 📤 Envoi du message embed dans le salon
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERREUR CARTE] {e}")
            await ctx.send("💥 Une erreur est survenue lors de la recherche de la carte.")

    # ────────────────────────────────────────────────────────────────────────────
    # 🏷️ CATÉGORIE personnalisée pour !help
    # ────────────────────────────────────────────────────────────────────────────
    def cog_load(self):
        self.carte.category = "🃏 Yu-Gi-Oh!"

# ────────────────────────────────────────────────────────────────────────────────
# ⚙️ SETUP DU COG
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    🔁 Fonction appelée lors du chargement du cog.
    Elle ajoute le cog et définit une catégorie visible dans !help.
    """
    cog = Carte(bot)

    # 🗂️ Ajout d'une catégorie à toutes les commandes du cog
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"

    await bot.add_cog(cog)
    print("✅ Cog chargé : Carte (catégorie = 🃏 Yu-Gi-Oh!)")
