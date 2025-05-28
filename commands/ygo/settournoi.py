# =============================================================
# 📁 tournoi_admin.py — Commande !settournoi (admin)
# Ce fichier contient la commande administrative pour mettre
# à jour la date du prochain tournoi dans la base Supabase.
# =============================================================

import discord
from discord.ext import commands
from supabase_client import supabase  # 🔗 Assure-toi que ce client est bien configuré ailleurs

# =============================================================
# 🛠️ Cog : TournoiAdmin
# =============================================================
class TournoiAdmin(commands.Cog):
    """
    🔒 Commandes administratives liées aux tournois (réservées aux admins).
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="settournoi",
        help="Définit la prochaine date de tournoi.",
        description="Utilisation : !settournoi <date>\nExemple : !settournoi 30 juin 2025 à 20h"
    )
    @commands.has_permissions(administrator=True)
    async def settournoi(self, ctx, *, date_text: str):
        """
        📅 Enregistre une nouvelle date de tournoi dans Supabase (ligne id=1).
        """
        try:
            result = supabase.table("tournoi_info").update({
                "prochaine_date": date_text
            }).eq("id", 1).execute()

            if result.status_code == 200:
                await ctx.send(f"📅 Nouvelle date enregistrée pour le tournoi : **{date_text}**")
            else:
                await ctx.send("❌ Erreur lors de la mise à jour dans Supabase.")

        except Exception as e:
            print(f"[ERREUR SETTOURNOI] {e}")
            await ctx.send("🚨 Une erreur est survenue pendant la mise à jour.")

    def cog_load(self):
        self.settournoi.category = "VAACT"  # 🏷️ Catégorie personnalisée pour affichage dans !help

# =============================================================
# ⚙️ Setup du Cog
# =============================================================
async def setup(bot):
    cog = TournoiAdmin(bot)

    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"

    await bot.add_cog(cog)
