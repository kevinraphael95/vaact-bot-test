import discord
from discord.ext import commands

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────────
    # 🏆 Commande !topqs / !topquestionstreak
    # Affiche le classement des meilleures séries de bonnes réponses
    # ──────────────────────────────────────────────────────────────
    @commands.command(name="topqs", aliases=["topquestionstreak"], help="Affiche le classement des meilleures séries de bonnes réponses.")
    async def topqs(self, ctx):
        from supabase_client import supabase  # Import local pour éviter conflit si le module est optionnel

        try:
            # 🔄 Requête Supabase : récupérer les 10 plus grands streaks
            response = supabase.table("ygo_streaks") \
                .select("user_id, current_streak") \
                .order("current_streak", desc=True) \
                .limit(10) \
                .execute()

            if not response.data:
                await ctx.send("📉 Aucun streak enregistré pour le moment.")
                return

            # 🧾 Construction du leaderboard
            leaderboard = []
            for index, entry in enumerate(response.data, start=1):
                try:
                    user = await self.bot.fetch_user(int(entry["user_id"]))
                    username = user.name if user else f"Utilisateur inconnu ({entry['user_id']})"
                except:
                    username = f"Utilisateur inconnu ({entry['user_id']})"

                streak = entry["current_streak"]

                # 🌟 Emojis pour le top 3
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(index, f"`#{index}`")
                leaderboard.append(f"{medal} **{username}** : 🔥 {streak}")

            # 📊 Embed final
            embed = discord.Embed(
                title="🏆 Top 10 – Séries de bonnes réponses",
                description="\n".join(leaderboard),
                color=discord.Color.gold()
            )
            embed.set_footer(text="Classement basé sur les streaks actuels.")
            await ctx.send(embed=embed)

        except Exception as e:
            print("❌ Erreur dans la commande topqs :", e)
            await ctx.send("🚨 Une erreur est survenue lors de la récupération du classement.")

# N'oublie pas d’ajouter ce cog dans ton setup
async def setup(bot):
    await bot.add_cog(Question(bot))
