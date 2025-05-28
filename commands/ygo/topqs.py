import discord
from discord.ext import commands
from supabase_client import supabase  # Assure-toi que ce client est bien configuré

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────────
    # 🏆 Commande !topqs / !topquestionstreak
    # Affiche le classement des meilleures séries de bonnes réponses
    # ──────────────────────────────────────────────────────────────
    @commands.command(
        name="topqs",
        aliases=["topquestionstreak"],
        help="Affiche le classement des meilleures séries de bonnes réponses."
    )
    async def topqs(self, ctx):
        try:
            # 🔄 Requête Supabase : récupérer les 10 meilleurs streaks (best_streak)
            response = supabase.table("ygo_streaks") \
                .select("user_id, best_streak") \
                .order("best_streak", desc=True) \
                .limit(10) \
                .execute()

            if not response.data:
                await ctx.send("📉 Aucun streak enregistré pour le moment.")
                return

            leaderboard = []

            # 🧾 Construction du classement
            for index, row in enumerate(response.data, start=1):
                user_id = row["user_id"]
                best_streak = row.get("best_streak", 0)

                try:
                    user = await self.bot.fetch_user(int(user_id))
                    username = user.name if user else f"Utilisateur inconnu ({user_id})"
                except Exception:
                    username = f"Utilisateur inconnu ({user_id})"

                # 🥇 Ajout des emojis pour le podium
                place = {1: "🥇", 2: "🥈", 3: "🥉"}.get(index, f"`#{index}`")
                leaderboard.append(f"{place} **{username}** : 🔥 {best_streak}")

            # 📊 Création de l'embed
            embed = discord.Embed(
                title="🏆 Top 10 – Meilleurs Streaks de Réponses Correctes",
                description="\n".join(leaderboard),
                color=discord.Color.gold()
            )
            embed.set_footer(text="Classement basé sur la meilleure série atteinte.")
            await ctx.send(embed=embed)

        except Exception as e:
            print("❌ Erreur dans la commande topqs :", e)
            await ctx.send("🚨 Une erreur est survenue lors de la récupération du classement.")

# 🔧 Chargement du cog
async def setup(bot):
    await bot.add_cog(Question(bot))
