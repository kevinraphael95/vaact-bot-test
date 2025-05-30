# ────────────────────────────────────────────────────────────────────────────────
# 📁 tournoi_admin.py — Commande !settournoi (admin uniquement)
# ────────────────────────────────────────────────────────────────────────────────
# Ce module permet aux administrateurs de définir la prochaine date du tournoi
# directement dans la base Supabase (table : tournoi_info, ligne id=1).
# Exemple d’utilisation : !settournoi 30 juin 2025 à 20h
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ────────────────────────────────────────────────────────────────────────────────
import discord                            # 📦 API Discord
from discord.ext import commands          # 🧩 Extensions et commandes
from supabase_client import supabase      # 🔗 Client Supabase (configuré ailleurs)

# ────────────────────────────────────────────────────────────────────────────────
# 🔧 COG : TournoiAdmin
# ────────────────────────────────────────────────────────────────────────────────
class TournoiAdmin(commands.Cog):
    """
    🔒 Commandes administratives liées aux tournois.
    ➕ Exclusivement réservées aux administrateurs Discord.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Stocke une référence au bot

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 COMMANDE : !settournoi <date>
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(
        name="settournoi",
        help="📅 Définit la date du prochain tournoi.",
        description=(
            "Commande admin pour mettre à jour la date du tournoi dans Supabase.\n\n"
            "📌 Exemple : `!settournoi 30 juin 2025 à 20h`\n"
            "🔐 Réservé aux administrateurs."
        )
    )
    @commands.has_permissions(administrator=True)  # 🔐 Vérifie que l’auteur est admin
    async def settournoi(self, ctx: commands.Context, *, date_text: str):
        """
        🛠️ Met à jour la date du tournoi dans Supabase (ligne avec id=1).
        """
        try:
            # 📝 Mise à jour dans la table 'tournoi_info'
            result = supabase.table("tournoi_info").update({
                "prochaine_date": date_text
            }).eq("id", 1).execute()

            # ✅ Vérifie si l’opération a réussi
            if result.status_code == 200:
                await ctx.send(f"✅ Nouvelle date enregistrée pour le tournoi : **{date_text}**")
            else:
                await ctx.send("❌ Erreur lors de la mise à jour dans Supabase.")

        except Exception as e:
            print(f"[ERREUR SETTOURNOI] {e}")
            await ctx.send("🚨 Une erreur est survenue pendant la mise à jour.")

    # ────────────────────────────────────────────────────────────────────────────
    # 🏷️ CATEGORISATION pour !help
    # ────────────────────────────────────────────────────────────────────────────
    def cog_load(self):
        self.settournoi.category = "VAACT"

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 SETUP : Chargement automatique du cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    """
    🔁 Ajoute ce cog au bot lors du chargement.
    """
    cog = TournoiAdmin(bot)

    # 🏷️ S’assure que chaque commande a une catégorie définie
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"

    await bot.add_cog(cog)
    print("✅ Cog chargé : TournoiAdmin (catégorie = VAACT)")
