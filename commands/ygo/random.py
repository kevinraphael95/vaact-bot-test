# ────────────────────────────────────────────────────────────────────────────────
# 🎲 Random.py — Commande !random
# Objectif : Tirer une carte Yu-Gi-Oh! aléatoire et l'afficher joliment dans un embed
# Source : API publique YGOPRODeck (https://db.ygoprodeck.com/api-guide/)
# Langue : 🇫🇷 Français uniquement
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord                                 # Pour créer des embeds Discord
from discord.ext import commands              # Pour créer des commandes dans un Cog
import aiohttp                                 # Pour effectuer des requêtes HTTP asynchrones
import random                                  # Pour choisir une carte au hasard

# ────────────────────────────────────────────────────────────────────────────────
# 📘 Classe principale du Cog de commande !random
# ────────────────────────────────────────────────────────────────────────────────
class Random(commands.Cog):
    """Commande !random : tire une carte Yu-Gi-Oh! aléatoire (langue FR)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # Référence au bot principal

    # ────────────────────────────────────────────────────────────────────────────
    # 🎲 Commande !random
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(name="random", aliases=["aléatoire", "ran"])
    @commands.cooldown(1, 5, commands.BucketType.user)  # ⏱️ Cooldown utilisateur : 5 sec
    async def random_card(self, ctx: commands.Context):
        """
        Tire une carte Yu-Gi-Oh! aléatoire en français via l’API YGOPRODeck.
        """

        # 🔗 API publique (cartes en langue française)
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr"

        # 📡 Requête HTTP à l’API
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Impossible de contacter l’API.")
                    return
                data = await resp.json()

        # 🛑 Données invalides
        if "data" not in data:
            await ctx.send("❌ Données reçues invalides.")
            return

        # 🎯 Tirage d'une carte aléatoire
        carte = random.choice(data["data"])

        # ────────────────────────────────────────────────────────────────────────
        # 🖼️ Création de l'embed de réponse
        # ────────────────────────────────────────────────────────────────────────
        embed = discord.Embed(
            title=carte["name"],
            description=carte.get("desc", "Pas de description disponible."),
            color=discord.Color.gold()
        )

        embed.set_author(name="Carte aléatoire Yu-Gi-Oh!", icon_url="https://cdn-icons-png.flaticon.com/512/361/361678.png")

        # 🔬 Type général
        embed.add_field(name="🧪 Type", value=carte.get("type", "—"), inline=True)

        # 💥 Si c'est un monstre, ajouter ses statistiques
        if carte.get("type", "").lower().startswith("monstre"):
            embed.add_field(name="⚔️ ATK / DEF", value=f"{carte.get('atk', '—')} / {carte.get('def', '—')}", inline=True)
            embed.add_field(name="⭐ Niveau / Rang", value=str(carte.get("level", "—")), inline=True)
            embed.add_field(name="🌪️ Attribut", value=carte.get("attribute", "—"), inline=True)
            embed.add_field(name="👹 Race", value=carte.get("race", "—"), inline=True)

        # 🖼️ Miniature de la carte
        image_url = carte.get("card_images", [{}])[0].get("image_url")
        if image_url:
            embed.set_thumbnail(url=image_url)

        # 📤 Envoi de l’embed
        await ctx.send(embed=embed)

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Fonction de setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    Fonction de chargement du Cog Random.
    Ajoute la commande dans la catégorie "🃏 Yu-Gi-Oh!".
    """
    cog = Random(bot)
    for command in cog.get_commands():
        command.category = "🃏 Yu-Gi-Oh!"
    await bot.add_cog(cog)
