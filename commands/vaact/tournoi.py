# ──────────────────────────────────────────────────────────────
# 📁 VAACT — tournoi.py
# ──────────────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !tournoi
# ───────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import aiohttp
import os

# ──────────────────────────────────────────────────────────────
# 🔧 COG : TournoiCommand
# ──────────────────────────────────────────────────────────────
class TournoiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke l'instance du bot

    # ──────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !tournoi
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="tournoi",
        help="📅 Affiche la date du prochain tournoi."
    )
    async def tournoi(self, ctx: commands.Context):
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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
        except Exception:
            await ctx.send("❌ Erreur de connexion à Supabase.")
            return

        if not data or not data[0].get("prochaine_date"):
            await ctx.send("📭 Aucun tournoi prévu pour le moment.")
            return

        prochaine_date = data[0]["prochaine_date"]
        await ctx.send(f"📅 Prochain tournoi : **{prochaine_date}**")

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = TournoiCommand(bot)
    cog.tournoi.category = "VAACT"  # 🏷️ Catégorie affichée dans !help
    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiCommand (catégorie = "VAACT")")
