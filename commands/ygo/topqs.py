# ───────────────────────────────────────────────────────────────────────────────
# 🏆 topqs.py — Commande !topqs
# Affiche le top 10 des meilleures séries de bonnes réponses.
# ───────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
from supabase_client import supabase  # Client Supabase déjà connecté

# ───────────────────────────────────────────────────────────────────────────────
# 📦 Cog principal — Commande !topqs
# ───────────────────────────────────────────────────────────────────────────────

class TopQS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="topqs",
        aliases=["topquestionstreak"],
        help="Affiche le classement des meilleures séries de bonnes réponses."
    )
    async def topqs(self, ctx):
        try:
            # 📥 Récupération des données Supabase
            response = supabase.table("ygo_streaks") \
                .select("user_id, best_streak") \
                .order("best_streak", desc=True) \
                .limit(10) \
                .execute()

            if not response.data:
                await ctx.send("📉 Aucun streak enregistré pour le moment.")
                return

            leaderboard = []
            for index, row in enumerate(response.data, start=1):
                user_id = row["user_id"]
                best_streak = row.get("best_streak", 0)

                try:
                    user = await self.bot.fetch_user(int(user_id))
                    username = user.name if user else f"Utilisateur inconnu ({user_id})"
                except:
                    username = f"Utilisateur inconnu ({user_id})"

                place = {1: "🥇", 2: "🥈", 3: "🥉"}.get(index, f"`#{index}`")
                leaderboard.append(f"{place} **{username}** : 🔥 {best_streak}")

            # 📊 Embed du classement
            embed = discord.Embed(
                title="🏆 Top 10 – Meilleures Séries",
                description="\n".join(leaderboard),
                color=discord.Color.gold()
            )
            embed.set_footer(text="Classement basé sur la meilleure série atteinte.")
            await ctx.send(embed=embed)

        except Exception as e:
            print("[ERREUR TOPQS]", e)
            await ctx.send("🚨 Une erreur est survenue lors du classement.")

# ───────────────────────────────────────────────────────────────────────────────
# 🔌 Chargement du Cog
# Attribution de la catégorie pour les systèmes de help personnalisés
# ───────────────────────────────────────────────────────────────────────────────

async def setup(bot):
    cog = TopQS(bot)

    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "YGO"

    await bot.add_cog(cog)
