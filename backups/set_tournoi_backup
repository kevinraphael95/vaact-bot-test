# ────────────────────────────────────────────────────────────────────────────────
# 📌 tournoi_admin.py — Commande !settournoi
# Objectif : Définir la prochaine date du tournoi dans Supabase
# Catégorie : 🧠 VAACT
# Accès : Administrateur uniquement
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from supabase_client import supabase

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class TournoiAdmin(commands.Cog):
    """
    🔒 Commandes administratives liées aux tournois.
    ➕ Exclusivement réservées aux administrateurs Discord.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="settournoi",
        help="📅 Définit la date du prochain tournoi.",
        description=(
            "Commande admin pour mettre à jour la date du tournoi dans Supabase.\n\n"
            "📌 Exemple : `!settournoi 30 juin 2025 à 20h`\n"
            "🔐 Réservé aux administrateurs."
        )
    )
    @commands.has_permissions(administrator=True)
    async def settournoi(self, ctx: commands.Context, *, date_text: str):
        """
        🛠️ Met à jour la date du tournoi dans Supabase (ligne avec id=1).
        """
        try:
            result = supabase.table("tournoi_info").update({
                "prochaine_date": date_text
            }).eq("id", 1).execute()

            if result.status_code == 200:
                await ctx.send(f"✅ Nouvelle date enregistrée pour le tournoi : **{date_text}**")
            else:
                await ctx.send("❌ Erreur lors de la mise à jour dans Supabase.")

        except Exception as e:
            print(f"[ERREUR SETTOURNOI] {e}")
            await ctx.send("🚨 Une erreur est survenue pendant la mise à jour.")

    def cog_load(self):
        self.settournoi.category = "VAACT"

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = TournoiAdmin(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"
    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiAdmin (catégorie = VAACT)")
