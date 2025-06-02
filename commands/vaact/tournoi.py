# ────────────────────────────────────────────────────────────────────────────────
# 📌 tournoi.py — Commande interactive !tournoi
# Objectif : Affiche la date du prochain tournoi à partir de Supabase
# Catégorie : 🧠 VAACT
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp
import os

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement des données Supabase (aucun fichier local requis)
# ────────────────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Aucune interface interactive requise pour cette commande simple
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class TournoiCommand(commands.Cog):
    """
    Commande !tournoi — Affiche la date du prochain tournoi
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="tournoi",
        help="📅 Affiche la date du prochain tournoi.",
        description="Récupère et affiche la date du prochain tournoi depuis Supabase."
    )
    async def tournoi(self, ctx: commands.Context):
        """Commande simple pour consulter la prochaine date de tournoi."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            await ctx.send("❌ Configuration manquante (SUPABASE_URL ou SUPABASE_KEY).")
            return

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{SUPABASE_URL}/rest/v1/tournoi_info?select=prochaine_date&order=id.desc&limit=1"
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        await ctx.send("❌ Erreur lors de la récupération des données Supabase.")
                        return
                    data = await response.json()
        except Exception as e:
            print(f"[ERREUR tournoi] {e}")
            await ctx.send("❌ Erreur de connexion à Supabase.")
            return

        if not data or not data[0].get("prochaine_date"):
            await ctx.send("📭 Aucun tournoi prévu pour le moment.")
            return

        prochaine_date = data[0]["prochaine_date"]
        await ctx.send(f"📅 Prochain tournoi : **{prochaine_date}**")



# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = TournoiCommand(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
    print("✅ Cog chargé : Code (catégorie = VAACT)")
