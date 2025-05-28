# ───────────────────────────────────────────────────────────────────────────────
# 🔥 streak.py — Commande !streak
# Affiche la série de bonnes réponses de l'utilisateur.
# Catégorie : "VAACT"
# ───────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
from supabase_client import supabase  # Client Supabase déjà connecté

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !streak
# ───────────────────────────────────────────────────────────────────────────────

class Streak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="streak",
        aliases=["qs"],
        help="Affiche ta série de bonnes réponses."
    )
    async def streak(self, ctx):
        user_id = str(ctx.author.id)

        try:
            # 📦 Récupération des données Supabase
            response = supabase.table("ygo_streaks") \
                .select("current_streak", "best_streak") \
                .eq("user_id", user_id) \
                .execute()

            if response.data:
                # ✅ Données trouvées
                streak = response.data[0]
                current = streak.get("current_streak", 0)
                best = streak.get("best_streak", 0)

                await ctx.send(
                    f"🔥 **{ctx.author.display_name}**, ta série actuelle est de **{current}** 🔁\n"
                    f"🏆 Ton record absolu est de **{best}** bonnes réponses consécutives !"
                )
            else:
                # ⛔ Aucun streak trouvé
                await ctx.send(
                    "📉 Tu n'as pas encore commencé de série. "
                    "Lance une question avec `!question` pour démarrer ton streak !"
                )

        except Exception as e:
            print("[ERREUR STREAK]", e)
            await ctx.send("🚨 Une erreur est survenue en récupérant ta série.")

# ───────────────────────────────────────────────────────────────────────────────
# 🔌 Chargement du Cog
# Attribution de la catégorie "VAACT" pour les systèmes de help personnalisés
# ───────────────────────────────────────────────────────────────────────────────

async def setup(bot):
    cog = Streak(bot)

    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "VAACT"

    await bot.add_cog(cog)
